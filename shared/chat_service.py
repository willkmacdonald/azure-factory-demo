"""
Chat Service - Shared chat logic for CLI and API

This module provides reusable chat functionality for both the CLI interface
and the REST API. It handles Azure OpenAI integration, tool calling, and
conversation management.

Extracted from src/main.py in PR4 to enable code reuse between CLI and web interfaces.

CURRENT IMPLEMENTATION: Azure OpenAI Service (Direct)
-------------------------------------------------------
This module currently uses Azure OpenAI Service directly via the openai package.

FUTURE ENHANCEMENT: Migrate to Azure AI Foundry
------------------------------------------------
For production deployments and multi-provider flexibility, consider migrating to
Azure AI Foundry, which provides:

✅ Multi-Provider Support:
   - OpenAI models (GPT-4, GPT-4o, GPT-4 Vision, etc.)
   - Anthropic models (Claude 3.5 Sonnet, Claude 3 Opus, etc.)
   - Meta models (Llama 3.1, Llama 3.2, etc.)
   - DeepSeek, Mistral, Cohere, and other providers

✅ Flexibility Benefits:
   - Switch between providers without code changes
   - Compare model performance across providers
   - Cost optimization by choosing best price/performance ratio
   - No vendor lock-in to OpenAI

Migration Guide: See ~/.claude/CLAUDE.md section "Azure AI Services Pattern"

For this demo/prototype, direct Azure OpenAI Service integration is sufficient.
"""

from datetime import datetime
from typing import Any, AsyncGenerator, Dict, List, Tuple
import json
import logging

from openai import AsyncAzureOpenAI

logger = logging.getLogger(__name__)

# Import from shared package (proper Python imports, no sys.path manipulation)
from shared.config import FACTORY_NAME, AZURE_DEPLOYMENT_NAME
from shared.data import load_data, load_data_async, MACHINES
from shared.metrics import (
    calculate_oee,
    get_scrap_metrics,
    get_quality_issues,
    get_downtime_analysis,
)
from shared.memory_service import (
    save_investigation,
    update_investigation,
    log_action,
    get_relevant_memories,
    generate_shift_summary,
)


def sanitize_user_input(user_message: str) -> str:
    """Sanitize user input to prevent prompt injection attacks.

    Args:
        user_message: Raw user input message

    Returns:
        Sanitized message safe for LLM processing

    Security Considerations (PR20B):
        This function provides BASIC protection against prompt injection attacks,
        which is sufficient for demo/prototype environments. It includes:

        ✅ Detection of common prompt injection patterns
        ✅ Logging of suspicious inputs for security monitoring
        ✅ Removal of null bytes and excessive newlines
        ✅ Whitespace normalization

        ⚠️  LIMITATIONS (Not suitable for production as-is):
        - Does NOT block detected injection attempts (only logs warnings)
        - Pattern matching is basic and can be bypassed with creative encoding
        - No defense against adversarial prompts or jailbreak techniques
        - No semantic analysis of potentially malicious instructions
        - No user reputation or rate limiting integration

        🔒 PRODUCTION RECOMMENDATIONS:
        1. Implement strict input validation with length limits (already done: 2000 chars)
        2. Use LLM-based content filtering (Azure Content Safety API)
        3. Implement semantic analysis for malicious intent detection
        4. Add user authentication and rate limiting per user (not just IP)
        5. Consider rejecting (not just logging) messages with injection patterns
        6. Implement output filtering to prevent data exfiltration
        7. Use separate system prompts with strong delimiter tokens
        8. Monitor and alert on repeated injection attempts
        9. Consider using Azure OpenAI's content filtering features
        10. Regular security audits and red team testing

        📚 REFERENCES:
        - OWASP LLM Top 10 (LLM01: Prompt Injection)
        - Azure OpenAI Content Safety: https://learn.microsoft.com/azure/ai-services/openai/concepts/content-filter
        - Prompt Injection Primer: https://simonwillison.net/2023/Apr/14/worst-that-can-happen/

    Note:
        This is a basic sanitization approach suitable for demo purposes.
        Production systems should implement more comprehensive security measures
        as outlined above.
    """
    # Strip leading/trailing whitespace
    sanitized = user_message.strip()

    # Check for suspicious patterns that could indicate prompt injection
    suspicious_patterns = [
        "ignore previous instructions",
        "ignore all previous",
        "disregard previous",
        "forget previous",
        "system:",
        "assistant:",
        "[SYSTEM]",
        "[INST]",
        "</s>",
        "<|im_start|>",
        "<|im_end|>",
    ]

    # Convert to lowercase for case-insensitive matching
    lower_message = sanitized.lower()

    # Log warning if suspicious patterns detected (but don't block - could be false positive)
    for pattern in suspicious_patterns:
        if pattern in lower_message:
            logger.warning(
                f"Potential prompt injection detected in user input: pattern '{pattern}' found",
                extra={"user_message_preview": sanitized[:100]},
            )
            # For demo purposes, we log but don't block
            # Production systems might want to reject or further sanitize

    # Remove any null bytes
    sanitized = sanitized.replace("\x00", "")

    # Limit consecutive newlines to prevent prompt breaking
    import re

    sanitized = re.sub(r"\n{4,}", "\n\n\n", sanitized)

    return sanitized


# Tool definitions for Azure OpenAI
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "calculate_oee",
            "description": (
                "Calculate Overall Equipment Effectiveness (OEE) for a "
                "date range. Returns OEE percentage and breakdown."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": "Start date (YYYY-MM-DD)",
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date (YYYY-MM-DD)",
                    },
                    "machine_name": {
                        "type": "string",
                        "description": "Optional machine name filter",
                    },
                },
                "required": ["start_date", "end_date"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_scrap_metrics",
            "description": (
                "Get scrap production metrics including total scrap, "
                "scrap rate, and breakdown by machine."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": "Start date (YYYY-MM-DD)",
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date (YYYY-MM-DD)",
                    },
                    "machine_name": {
                        "type": "string",
                        "description": "Optional machine name filter",
                    },
                },
                "required": ["start_date", "end_date"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_quality_issues",
            "description": (
                "Get quality defect events with details about defect types, "
                "severity, and affected parts."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": "Start date (YYYY-MM-DD)",
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date (YYYY-MM-DD)",
                    },
                    "severity": {
                        "type": "string",
                        "description": "Optional severity filter: Low, Medium, or High",
                    },
                    "machine_name": {
                        "type": "string",
                        "description": "Optional machine name filter",
                    },
                },
                "required": ["start_date", "end_date"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_downtime_analysis",
            "description": (
                "Analyze downtime events including reasons, duration, "
                "and major incidents."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": "Start date (YYYY-MM-DD)",
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date (YYYY-MM-DD)",
                    },
                    "machine_name": {
                        "type": "string",
                        "description": "Optional machine name filter",
                    },
                },
                "required": ["start_date", "end_date"],
            },
        },
    },
    # Memory tools for persistent context across sessions
    {
        "type": "function",
        "function": {
            "name": "save_investigation",
            "description": (
                "Create a new investigation to track an ongoing factory issue. "
                "Use this when the user reports a problem that needs follow-up, "
                "such as quality issues, machine anomalies, or supplier concerns. "
                "The investigation can be referenced in future conversations."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Brief investigation title (e.g., 'CNC-001 Surface Finish Degradation')",
                    },
                    "initial_observation": {
                        "type": "string",
                        "description": "What triggered this investigation - the initial problem or anomaly observed",
                    },
                    "machine_id": {
                        "type": "string",
                        "description": "Related machine ID if applicable (e.g., 'CNC-001', 'MILL-002')",
                    },
                    "supplier_id": {
                        "type": "string",
                        "description": "Related supplier ID if applicable",
                    },
                },
                "required": ["title", "initial_observation"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "log_action",
            "description": (
                "Record an action taken by the user with baseline metrics for impact tracking. "
                "Use this when the user makes a parameter change, schedules maintenance, "
                "or implements a process change. Enables proactive follow-up on results."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "description": "What action was taken (e.g., 'Increased feed rate from 100 to 120 mm/min')",
                    },
                    "action_type": {
                        "type": "string",
                        "enum": ["parameter_change", "maintenance", "process_change"],
                        "description": "Category of the action",
                    },
                    "expected_impact": {
                        "type": "string",
                        "description": "What improvement is expected (e.g., 'Reduce cycle time by 10%')",
                    },
                    "machine_id": {
                        "type": "string",
                        "description": "Related machine ID if applicable",
                    },
                    "baseline_metrics": {
                        "type": "object",
                        "description": 'Metrics captured before the action (e.g., {"oee": 0.72, "quality_rate": 0.95})',
                    },
                    "follow_up_date": {
                        "type": "string",
                        "description": "When to check results (YYYY-MM-DD format)",
                    },
                },
                "required": ["description", "action_type", "expected_impact"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_pending_followups",
            "description": (
                "Check for actions that are due for follow-up. "
                "Returns actions where the follow-up date has passed and actual impact "
                "has not been recorded. Use this proactively to remind users about "
                "checking on past improvements."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_memory_context",
            "description": (
                "Retrieve relevant memory context for the current conversation. "
                "Use this to check for open investigations or recent actions related "
                "to a specific machine or supplier before responding to queries about them."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "machine_id": {
                        "type": "string",
                        "description": "Filter by machine ID",
                    },
                    "supplier_id": {
                        "type": "string",
                        "description": "Filter by supplier ID",
                    },
                    "status": {
                        "type": "string",
                        "enum": ["open", "in_progress", "resolved", "closed"],
                        "description": "Filter investigations by status",
                    },
                },
                "required": [],
            },
        },
    },
]


async def build_system_prompt() -> str:
    """Build system prompt with factory context, date range, available machines, and memory.

    Includes active investigations and pending follow-ups for continuity across sessions.

    Returns:
        str: System prompt containing factory context, memory context, and instructions

    Raises:
        RuntimeError: If no data is available
    """
    logger.debug("Building system prompt with factory context and memory")
    data = await load_data_async()
    if not data:
        logger.error("No data available for building system prompt")
        raise RuntimeError("No data available. Run 'python -m src.main setup' first.")
    start_date = data["start_date"].split("T")[0]
    end_date = data["end_date"].split("T")[0]
    machines = ", ".join([str(m["name"]) for m in MACHINES])

    # Build memory context section
    memory_section = await _build_memory_context()

    logger.debug(f"System prompt built for date range: {start_date} to {end_date}")
    return f"""You are a factory operations assistant for {FACTORY_NAME}.

You have access to 30 days of production data ({start_date} to {end_date}) covering:
- 4 machines: {machines}
- 2 shifts: Day (6am-2pm) and Night (2pm-10pm)
- Metrics: OEE, scrap, quality issues, downtime

{memory_section}

When answering:
1. Use tools to get accurate data
2. Provide specific numbers and percentages
3. Explain trends and patterns
4. Compare metrics when relevant
5. Be concise but thorough
6. Reference relevant open investigations when discussing related machines/suppliers
7. Proactively mention pending follow-ups when relevant

Memory capabilities:
- Use save_investigation to track ongoing issues that need follow-up
- Use log_action when users make changes (parameter adjustments, maintenance, etc.)
- Use get_pending_followups to check for actions needing follow-up
- Use get_memory_context to retrieve relevant context for a machine or supplier

Today's date is {datetime.now().strftime('%Y-%m-%d')}. When users ask about \
"today", "this week", or relative dates, calculate the appropriate date range \
based on the data available."""


async def _build_memory_context() -> str:
    """Build memory context section for system prompt.

    Retrieves active investigations and pending follow-ups to provide
    continuity across chat sessions.

    Returns:
        str: Formatted memory context section, or empty string if no memories
    """
    try:
        shift_summary = await generate_shift_summary()
    except Exception as e:
        logger.warning(f"Failed to load memory context: {e}")
        return ""

    sections = []

    # Active investigations
    if shift_summary["counts"]["active_investigations"] > 0:
        inv_lines = ["**Active Investigations:**"]
        for inv in shift_summary["active_investigations"]:
            status_emoji = "🔍" if inv["status"] == "open" else "🔧"
            machine_info = f" ({inv['machine_id']})" if inv["machine_id"] else ""
            inv_lines.append(
                f"- {status_emoji} {inv['title']}{machine_info} - {inv['findings_count']} findings"
            )
        sections.append("\n".join(inv_lines))

    # Pending follow-ups
    if shift_summary["counts"]["pending_followups"] > 0:
        followup_lines = ["**Pending Follow-ups:**"]
        for action in shift_summary["pending_followups"]:
            followup_lines.append(
                f"- ⏰ {action['description']} (expected: {action['expected_impact']}, "
                f"due: {action['follow_up_date']})"
            )
        sections.append("\n".join(followup_lines))

    # Today's actions summary
    if shift_summary["counts"]["todays_actions"] > 0:
        sections.append(
            f"**Today's Activity:** {shift_summary['counts']['todays_actions']} actions logged"
        )

    if sections:
        return "**MEMORY CONTEXT:**\n" + "\n\n".join(sections)
    return ""


async def execute_tool(tool_name: str, tool_args: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a tool function and return results as dictionary.

    Supports both metrics tools and memory tools for persistent context.

    Args:
        tool_name: Name of the tool to execute
        tool_args: Arguments to pass to the tool function

    Returns:
        Dict containing tool execution results or error message
    """
    logger.info(f"Executing tool: {tool_name} with args: {tool_args}")
    try:
        result: Any

        # Metrics tools
        if tool_name == "calculate_oee":
            result = await calculate_oee(**tool_args)
        elif tool_name == "get_scrap_metrics":
            result = await get_scrap_metrics(**tool_args)
        elif tool_name == "get_quality_issues":
            result = await get_quality_issues(**tool_args)
        elif tool_name == "get_downtime_analysis":
            result = await get_downtime_analysis(**tool_args)

        # Memory tools
        elif tool_name == "save_investigation":
            investigation = await save_investigation(**tool_args)
            result = {
                "success": True,
                "investigation_id": investigation.id,
                "title": investigation.title,
                "status": investigation.status,
                "message": f"Investigation '{investigation.title}' created with ID {investigation.id}",
            }
        elif tool_name == "log_action":
            action = await log_action(**tool_args)
            result = {
                "success": True,
                "action_id": action.id,
                "description": action.description,
                "action_type": action.action_type,
                "follow_up_date": action.follow_up_date,
                "message": f"Action logged with ID {action.id}",
            }
        elif tool_name == "get_pending_followups":
            result = await _get_pending_followups()
        elif tool_name == "get_memory_context":
            result = await get_relevant_memories(**tool_args)

        else:
            logger.warning(f"Unknown tool requested: {tool_name}")
            return {"error": f"Unknown tool: {tool_name}"}

        # Convert Pydantic model to dictionary if needed
        if hasattr(result, "model_dump"):
            result_dict = result.model_dump()
        else:
            result_dict = result

        logger.debug(f"Tool {tool_name} completed successfully")
        return result_dict
    except Exception as e:
        logger.error(f"Error executing tool {tool_name}: {e}", exc_info=True)
        return {"error": f"Tool execution failed: {str(e)}"}


async def _get_pending_followups() -> Dict[str, Any]:
    """Get actions that are due for follow-up.

    Returns actions where follow_up_date has passed and actual_impact is not set.

    Returns:
        Dict with pending follow-ups and count
    """
    try:
        shift_summary = await generate_shift_summary()
        pending = shift_summary.get("pending_followups", [])
        return {
            "pending_followups": pending,
            "count": len(pending),
            "message": (
                f"Found {len(pending)} actions pending follow-up"
                if pending
                else "No pending follow-ups"
            ),
        }
    except Exception as e:
        logger.error(f"Failed to get pending follow-ups: {e}")
        return {"error": str(e), "pending_followups": [], "count": 0}


async def get_chat_response(
    client: AsyncAzureOpenAI,
    system_prompt: str,
    conversation_history: List[Dict[str, Any]],
    user_message: str,
) -> Tuple[str, List[Dict[str, Any]]]:
    """Get Azure OpenAI response with tool calling.

    Handles the tool-calling loop: sends message, executes requested tools,
    and returns final response with updated conversation history.

    Args:
        client: AsyncAzureOpenAI client instance
        system_prompt: System prompt with factory context
        conversation_history: Previous conversation messages
        user_message: Current user message

    Returns:
        Tuple of (response_text, new_history)
        - response_text: AI's final response
        - new_history: List of new messages added during this turn
    """
    logger.info(f"Processing chat message: {user_message[:50]}...")

    # Sanitize user input to prevent prompt injection
    sanitized_message = sanitize_user_input(user_message)
    if sanitized_message != user_message:
        logger.debug("User input was sanitized")

    # Build messages list with system prompt, history, and new message
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(conversation_history)
    messages.append({"role": "user", "content": sanitized_message})

    # Track where new messages start (after existing history)
    history_start_index = len(messages) - 1  # Index of new user message

    # Tool calling loop - continues until AI provides final answer
    iteration = 0
    while True:
        iteration += 1
        logger.debug(f"Chat iteration {iteration}: Calling Azure OpenAI API")

        try:
            response = await client.chat.completions.create(
                model=AZURE_DEPLOYMENT_NAME,
                messages=messages,
                tools=TOOLS,
                tool_choice="auto",
            )
        except Exception as e:
            logger.error(f"Azure OpenAI API call failed: {e}", exc_info=True)
            raise

        message = response.choices[0].message

        # If no tool calls, we have the final answer
        if not message.tool_calls:
            logger.info(
                "Chat completed successfully without tool calls"
                if iteration == 1
                else f"Chat completed after {iteration} iterations"
            )
            # Extract new messages added during this conversation turn
            new_history = messages[history_start_index:]
            # Add final assistant response
            new_history.append({"role": "assistant", "content": message.content})
            return message.content, new_history

        # Add assistant message with tool calls to history
        logger.debug(f"AI requested {len(message.tool_calls)} tool call(s)")
        messages.append(message.model_dump())

        # Execute each requested tool
        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)

            # Execute tool and get result
            result = await execute_tool(tool_name, tool_args)

            # Add tool result to messages
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_name,
                    "content": json.dumps(result),
                }
            )


async def get_chat_response_streaming(
    client: AsyncAzureOpenAI,
    system_prompt: str,
    conversation_history: List[Dict[str, Any]],
    user_message: str,
) -> AsyncGenerator[Dict[str, Any], None]:
    """Get Azure OpenAI response with streaming and tool calling.

    Yields events as the response is generated, including:
    - status: Processing status updates (e.g., "Calling tool: get_oee_metrics")
    - delta: Text chunks as they arrive
    - done: Final signal with complete response and history

    Args:
        client: AsyncAzureOpenAI client instance
        system_prompt: System prompt with factory context
        conversation_history: Previous conversation messages
        user_message: Current user message

    Yields:
        Dict with event type and data:
        - {"type": "status", "content": "Processing..."}
        - {"type": "delta", "content": "partial text"}
        - {"type": "tool_call", "name": "get_oee_metrics", "status": "executing"}
        - {"type": "tool_result", "name": "get_oee_metrics", "status": "complete"}
        - {"type": "done", "content": "full response", "history": [...]}
        - {"type": "error", "content": "error message"}
    """
    logger.info(f"Processing streaming chat message: {user_message[:50]}...")

    # Sanitize user input to prevent prompt injection
    sanitized_message = sanitize_user_input(user_message)
    if sanitized_message != user_message:
        logger.debug("User input was sanitized")

    # Build messages list with system prompt, history, and new message
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(conversation_history)
    messages.append({"role": "user", "content": sanitized_message})

    # Track where new messages start (after existing history)
    history_start_index = len(messages) - 1  # Index of new user message

    yield {"type": "status", "content": "Thinking..."}

    # Tool calling loop - continues until AI provides final answer
    iteration = 0
    while True:
        iteration += 1
        logger.debug(f"Streaming chat iteration {iteration}: Calling Azure OpenAI API")

        try:
            # Use streaming for the final response
            stream = await client.chat.completions.create(
                model=AZURE_DEPLOYMENT_NAME,
                messages=messages,
                tools=TOOLS,
                tool_choice="auto",
                stream=True,
            )

            # Collect the streamed response
            collected_content = ""
            collected_tool_calls: List[Dict[str, Any]] = []
            current_tool_call: Dict[str, Any] | None = None

            async for chunk in stream:
                if not chunk.choices:
                    continue

                delta = chunk.choices[0].delta

                # Handle content streaming
                if delta.content:
                    collected_content += delta.content
                    yield {"type": "delta", "content": delta.content}

                # Handle tool calls
                if delta.tool_calls:
                    for tool_call_delta in delta.tool_calls:
                        # New tool call starting
                        if tool_call_delta.index is not None:
                            idx = tool_call_delta.index
                            # Extend list if needed
                            while len(collected_tool_calls) <= idx:
                                collected_tool_calls.append({
                                    "id": "",
                                    "type": "function",
                                    "function": {"name": "", "arguments": ""}
                                })
                            current_tool_call = collected_tool_calls[idx]

                        if current_tool_call:
                            if tool_call_delta.id:
                                current_tool_call["id"] = tool_call_delta.id
                            if tool_call_delta.function:
                                if tool_call_delta.function.name:
                                    current_tool_call["function"]["name"] = tool_call_delta.function.name
                                if tool_call_delta.function.arguments:
                                    current_tool_call["function"]["arguments"] += tool_call_delta.function.arguments

            # If no tool calls, we have the final answer
            if not collected_tool_calls or all(not tc.get("function", {}).get("name") for tc in collected_tool_calls):
                logger.info(
                    "Streaming chat completed successfully without tool calls"
                    if iteration == 1
                    else f"Streaming chat completed after {iteration} iterations"
                )
                # Extract new messages added during this conversation turn
                new_history = messages[history_start_index:]
                # Add final assistant response
                new_history.append({"role": "assistant", "content": collected_content})
                yield {
                    "type": "done",
                    "content": collected_content,
                    "history": new_history
                }
                return

            # We have tool calls to execute
            logger.debug(f"AI requested {len(collected_tool_calls)} tool call(s)")

            # Add assistant message with tool calls to history
            assistant_message = {
                "role": "assistant",
                "content": collected_content or None,
                "tool_calls": [
                    {
                        "id": tc["id"],
                        "type": "function",
                        "function": {
                            "name": tc["function"]["name"],
                            "arguments": tc["function"]["arguments"]
                        }
                    }
                    for tc in collected_tool_calls
                    if tc.get("function", {}).get("name")
                ]
            }
            messages.append(assistant_message)

            # Execute each requested tool
            for tool_call in collected_tool_calls:
                if not tool_call.get("function", {}).get("name"):
                    continue

                tool_name = tool_call["function"]["name"]
                tool_args_str = tool_call["function"]["arguments"]

                yield {
                    "type": "tool_call",
                    "name": tool_name,
                    "status": "executing"
                }

                try:
                    tool_args = json.loads(tool_args_str) if tool_args_str else {}
                except json.JSONDecodeError:
                    tool_args = {}

                # Execute tool and get result
                result = await execute_tool(tool_name, tool_args)

                yield {
                    "type": "tool_result",
                    "name": tool_name,
                    "status": "complete"
                }

                # Add tool result to messages
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "name": tool_name,
                        "content": json.dumps(result),
                    }
                )

            # Continue the loop to get the final response after tool execution
            yield {"type": "status", "content": "Analyzing results..."}

        except Exception as e:
            logger.error(f"Streaming chat error: {e}", exc_info=True)
            yield {"type": "error", "content": str(e)}
            return
