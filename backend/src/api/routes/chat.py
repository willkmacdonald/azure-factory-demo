"""Chat API routes for AI assistant with tool calling."""

import json
import logging
import uuid
import time
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, field_validator
from openai import AsyncAzureOpenAI
from slowapi import Limiter
from slowapi.util import get_remote_address

from shared.chat_service import get_chat_response, get_chat_response_streaming, build_system_prompt
from shared.config import AZURE_ENDPOINT, AZURE_API_KEY, AZURE_API_VERSION, RATE_LIMIT_CHAT, DEBUG, REQUIRE_AUTH
from ..auth import get_current_user_conditional

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["Chat"])

# Create limiter instance for this router
# This will be used to apply rate limits to individual endpoints
limiter = Limiter(key_func=get_remote_address)


# Request/Response models
class ChatMessage(BaseModel):
    """Individual chat message model with strict role enforcement."""

    role: str = Field(description="Message role: user or assistant only")
    content: Optional[str] = Field(
        default=None,
        description="Message content (can be None for tool calls)",
        max_length=2000,
        min_length=1
    )

    @field_validator('role')
    @classmethod
    def validate_role(cls, v: str) -> str:
        """Ensure role is either 'user' or 'assistant'.

        This prevents malformed history with invalid roles that could
        cause issues with the Azure OpenAI API.

        Args:
            v: Role value to validate

        Returns:
            str: Validated role value

        Raises:
            ValueError: If role is not 'user' or 'assistant'
        """
        allowed_roles = {"user", "assistant"}
        if v not in allowed_roles:
            raise ValueError(
                f"Invalid role '{v}'. Only 'user' and 'assistant' are allowed "
                f"in conversation history."
            )
        return v

    @field_validator('content')
    @classmethod
    def validate_content(cls, v: Optional[str]) -> Optional[str]:
        """Ensure content is non-empty after stripping whitespace (or None for tool calls).

        Args:
            v: Content value to validate

        Returns:
            Optional[str]: Validated content value or None

        Raises:
            ValueError: If content is empty or whitespace-only (but None is allowed)
        """
        # Allow None for tool calls
        if v is None:
            return v
        # If not None, ensure it's not empty/whitespace
        if not v.strip():
            raise ValueError("Message content cannot be empty or whitespace-only")
        return v


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""

    message: str = Field(
        description="User's message text",
        max_length=2000,
        min_length=1
    )
    history: List[ChatMessage] = Field(
        default_factory=list,
        description="Previous conversation messages",
        max_length=50
    )

    @field_validator('message')
    @classmethod
    def validate_message_content(cls, v: str) -> str:
        """Ensure message is non-empty after stripping whitespace.

        This prevents users from submitting empty or whitespace-only messages,
        which would waste API tokens and provide no value.

        Args:
            v: Message content to validate

        Returns:
            str: Validated message content

        Raises:
            ValueError: If message is empty or whitespace-only
        """
        if not v.strip():
            raise ValueError("Message cannot be empty or whitespace-only")
        return v

    @field_validator('history')
    @classmethod
    def validate_total_history_size(cls, v: List[ChatMessage]) -> List[ChatMessage]:
        """Ensure total history size doesn't exceed reasonable limits to prevent token exhaustion.

        This prevents attackers from sending many large messages to consume excessive API tokens.
        """
        total_chars = sum(len(msg.content) for msg in v if msg.content is not None)
        if total_chars > 50000:  # 50K character limit for entire history
            raise ValueError(
                f"Total conversation history too large: {total_chars} characters "
                f"(max: 50000). Please reduce history size."
            )
        return v


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""

    response: str = Field(description="AI assistant's response")
    history: List[ChatMessage] = Field(
        description="Updated conversation history including this exchange"
    )


# Dependency: Get Azure OpenAI client
async def get_openai_client() -> AsyncAzureOpenAI:
    """Create and return AsyncAzureOpenAI client instance.

    Returns:
        AsyncAzureOpenAI: Configured Azure OpenAI client

    Raises:
        HTTPException: If Azure credentials are not configured or client creation fails
    """
    # Validate environment variables exist
    if not AZURE_ENDPOINT:
        logger.error("AZURE_ENDPOINT environment variable not set")
        raise HTTPException(
            status_code=500,
            detail="Server configuration error: AZURE_ENDPOINT not configured",
        )

    if not AZURE_API_KEY:
        logger.error("AZURE_API_KEY environment variable not set")
        raise HTTPException(
            status_code=500,
            detail="Server configuration error: AZURE_API_KEY not configured",
        )

    # Validate endpoint format
    if not AZURE_ENDPOINT.startswith("https://"):
        logger.error(f"Invalid AZURE_ENDPOINT format: {AZURE_ENDPOINT}")
        raise HTTPException(
            status_code=500,
            detail="Server configuration error: Invalid AZURE_ENDPOINT format",
        )

    try:
        client = AsyncAzureOpenAI(
            azure_endpoint=AZURE_ENDPOINT,
            api_key=AZURE_API_KEY,
            api_version=AZURE_API_VERSION,
        )
        logger.debug(f"Azure OpenAI client created successfully (API version: {AZURE_API_VERSION})")
        return client
    except Exception as e:
        logger.error(f"Failed to create Azure OpenAI client: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to initialize Azure OpenAI client",
        )


@router.post("/chat", response_model=ChatResponse)
@limiter.limit(RATE_LIMIT_CHAT)
async def chat(
    request: Request,
    chat_request: ChatRequest,
    client: AsyncAzureOpenAI = Depends(get_openai_client),
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user_conditional)
) -> ChatResponse:
    """Chat endpoint with AI assistant using tool calling.

    This endpoint allows users to send messages to the AI assistant and receive
    responses. The AI can call tools to fetch factory metrics and data.

    Security Considerations (PR24B):
    - Conditional authentication based on REQUIRE_AUTH setting:
      * When REQUIRE_AUTH=true: Requires valid Azure AD token (production mode)
      * When REQUIRE_AUTH=false: Allows anonymous access with demo user (demo mode)
      * User info is logged for audit trail and cost attribution
    - Rate limiting (PR7): Limited to 10 requests/minute per IP to prevent abuse
    - Input validation: Message length capped at 2000 chars, history at 50 messages
    - Prompt injection mitigation:
      * System prompt is controlled server-side and not user-modifiable
      * Tool calling is restricted to predefined functions only (no arbitrary code)
      * User messages are validated via Pydantic models before processing
      * History size limits prevent token exhaustion attacks
      * No user input is directly concatenated into system prompts
    - Data isolation: Tools only access factory data, no system-level operations
    - Error handling: Production mode hides internal errors (DEBUG=false)

    Note: While these measures reduce prompt injection risk, LLM applications remain
    vulnerable to social engineering attacks. For production use, consider:
    - Content filtering on user inputs (Azure Content Safety API)
    - Monitoring for unusual tool calling patterns
    - Enable REQUIRE_AUTH=true for authenticated access
    - Audit logging of all chat interactions (currently implemented)

    Args:
        request: FastAPI Request object (required for rate limiting - slowapi)
        chat_request: Chat request containing message and conversation history
        client: Azure OpenAI client (injected dependency)
        current_user: User information (authenticated or demo user based on REQUIRE_AUTH)

    Returns:
        ChatResponse containing AI response and updated conversation history

    Raises:
        HTTPException: 401 if REQUIRE_AUTH=true and token is missing/invalid
        HTTPException: If chat processing fails
        RateLimitExceeded: If rate limit is exceeded (returns 429 status)
    """
    # Generate request ID for tracking
    request_id = str(uuid.uuid4())
    start_time = time.time()

    # Log request with authentication status for audit trail
    user_identifier = current_user.get('email') if current_user else "anonymous"
    logger.info(
        f"Chat request received [request_id={request_id}, user={user_identifier}]: "
        f"{chat_request.message[:50]}...",
        extra={
            "request_id": request_id,
            "user": user_identifier,
            "authenticated": current_user is not None,
            "message_length": len(chat_request.message),
            "history_size": len(chat_request.history),
        },
    )

    try:
        # Build system prompt with factory context
        system_prompt = await build_system_prompt()

        # Convert ChatMessage objects to dictionaries for chat service
        history_dicts = [msg.model_dump() for msg in chat_request.history]

        # Get AI response with tool calling
        response_text, updated_history_dicts = await get_chat_response(
            client=client,
            system_prompt=system_prompt,
            conversation_history=history_dicts,
            user_message=chat_request.message,
        )

        # Filter out tool messages and convert back to ChatMessage objects
        # Only keep user and assistant messages with content for the UI
        updated_history = [
            ChatMessage(**msg)
            for msg in updated_history_dicts
            if msg.get("role") in ["user", "assistant"] and msg.get("content")
        ]

        # Log completion with timing
        elapsed_time = time.time() - start_time
        logger.info(
            f"Chat response generated successfully [request_id={request_id}] in {elapsed_time:.2f}s",
            extra={
                "request_id": request_id,
                "elapsed_time": elapsed_time,
                "response_length": len(response_text),
            },
        )
        return ChatResponse(response=response_text, history=updated_history)

    except RuntimeError as e:
        # Handle data not available error
        elapsed_time = time.time() - start_time
        logger.error(
            f"Runtime error in chat endpoint [request_id={request_id}]: {e}",
            extra={"request_id": request_id, "elapsed_time": elapsed_time},
        )
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Handle unexpected errors
        elapsed_time = time.time() - start_time
        logger.error(
            f"Unexpected error in chat endpoint [request_id={request_id}]: {e}",
            exc_info=True,
            extra={"request_id": request_id, "elapsed_time": elapsed_time},
        )
        # Environment-based error messages (PR8)
        # In production (DEBUG=False), hide internal details
        # In development (DEBUG=True), show full error for debugging
        if DEBUG:
            # Development mode: provide detailed error information
            error_detail = f"Chat processing failed: {str(e)}"
        else:
            # Production mode: hide internal details to prevent information disclosure
            error_detail = "An error occurred while processing your request. Please try again later."
        raise HTTPException(status_code=500, detail=error_detail)


@router.post("/chat/stream")
@limiter.limit(RATE_LIMIT_CHAT)
async def chat_stream(
    request: Request,
    chat_request: ChatRequest,
    client: AsyncAzureOpenAI = Depends(get_openai_client),
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user_conditional)
) -> StreamingResponse:
    """Streaming chat endpoint with AI assistant using Server-Sent Events (SSE).

    This endpoint streams the AI response as it's generated, providing real-time
    feedback to the user. It supports tool calling with status updates.

    Event types sent via SSE:
    - status: Processing status (e.g., "Thinking...", "Analyzing results...")
    - delta: Text chunks as they arrive
    - tool_call: When AI is calling a tool (e.g., "Executing get_oee_metrics")
    - tool_result: When tool execution completes
    - done: Final event with complete response
    - error: If an error occurs

    Args:
        request: FastAPI Request object (required for rate limiting)
        chat_request: Chat request containing message and conversation history
        client: Azure OpenAI client (injected dependency)
        current_user: Optional authenticated user information

    Returns:
        StreamingResponse with text/event-stream content type
    """
    request_id = str(uuid.uuid4())
    start_time = time.time()

    user_identifier = current_user.get('email') if current_user else "anonymous"
    logger.info(
        f"Streaming chat request received [request_id={request_id}, user={user_identifier}]: "
        f"{chat_request.message[:50]}...",
    )

    async def event_generator():
        """Generate SSE events from the streaming chat response."""
        try:
            # Build system prompt with factory context
            system_prompt = await build_system_prompt()

            # Convert ChatMessage objects to dictionaries for chat service
            history_dicts = [msg.model_dump() for msg in chat_request.history]

            # Stream the response
            async for event in get_chat_response_streaming(
                client=client,
                system_prompt=system_prompt,
                conversation_history=history_dicts,
                user_message=chat_request.message,
            ):
                # Format as SSE event
                event_data = json.dumps(event)
                yield f"data: {event_data}\n\n"

                # Log completion on done event
                if event.get("type") == "done":
                    elapsed_time = time.time() - start_time
                    logger.info(
                        f"Streaming chat completed [request_id={request_id}] in {elapsed_time:.2f}s"
                    )

        except RuntimeError as e:
            logger.error(f"Runtime error in streaming chat [request_id={request_id}]: {e}")
            error_event = json.dumps({"type": "error", "content": str(e)})
            yield f"data: {error_event}\n\n"

        except Exception as e:
            logger.error(f"Error in streaming chat [request_id={request_id}]: {e}", exc_info=True)
            error_msg = str(e) if DEBUG else "An error occurred while processing your request."
            error_event = json.dumps({"type": "error", "content": error_msg})
            yield f"data: {error_event}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        }
    )
