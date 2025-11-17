"""
Chat Service - Shared chat logic for CLI and API

This module provides reusable chat functionality for both the CLI interface
and the REST API. It handles Azure OpenAI integration, tool calling, and
conversation management.

Extracted from src/main.py in PR4 to enable code reuse between CLI and web interfaces.
"""

from datetime import datetime
from typing import Any, Dict, List, Tuple
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
]


async def build_system_prompt() -> str:
    """Build system prompt with factory context, date range, and available machines.

    Returns:
        str: System prompt containing factory context and instructions

    Raises:
        RuntimeError: If no data is available
    """
    logger.debug("Building system prompt with factory context")
    data = await load_data_async()
    if not data:
        logger.error("No data available for building system prompt")
        raise RuntimeError("No data available. Run 'python -m src.main setup' first.")
    start_date = data["start_date"].split("T")[0]
    end_date = data["end_date"].split("T")[0]
    machines = ", ".join([str(m["name"]) for m in MACHINES])

    logger.debug(f"System prompt built for date range: {start_date} to {end_date}")
    return f"""You are a factory operations assistant for {FACTORY_NAME}.

You have access to 30 days of production data ({start_date} to {end_date}) covering:
- 4 machines: {machines}
- 2 shifts: Day (6am-2pm) and Night (2pm-10pm)
- Metrics: OEE, scrap, quality issues, downtime

When answering:
1. Use tools to get accurate data
2. Provide specific numbers and percentages
3. Explain trends and patterns
4. Compare metrics when relevant
5. Be concise but thorough

Today's date is {datetime.now().strftime('%Y-%m-%d')}. When users ask about \
"today", "this week", or relative dates, calculate the appropriate date range \
based on the data available."""


async def execute_tool(tool_name: str, tool_args: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a tool function and return results as dictionary.

    Args:
        tool_name: Name of the tool to execute
        tool_args: Arguments to pass to the tool function

    Returns:
        Dict containing tool execution results or error message
    """
    logger.info(f"Executing tool: {tool_name} with args: {tool_args}")
    try:
        result: Any
        if tool_name == "calculate_oee":
            result = await calculate_oee(**tool_args)
        elif tool_name == "get_scrap_metrics":
            result = await get_scrap_metrics(**tool_args)
        elif tool_name == "get_quality_issues":
            result = await get_quality_issues(**tool_args)
        elif tool_name == "get_downtime_analysis":
            result = await get_downtime_analysis(**tool_args)
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
            logger.info("Chat completed successfully without tool calls" if iteration == 1 else f"Chat completed after {iteration} iterations")
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
