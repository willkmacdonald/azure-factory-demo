"""Chat API routes for AI assistant with tool calling."""

import logging
import uuid
import time
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, Field, field_validator
from openai import AsyncAzureOpenAI
from slowapi import Limiter
from slowapi.util import get_remote_address

from shared.chat_service import get_chat_response, build_system_prompt
from shared.config import AZURE_ENDPOINT, AZURE_API_KEY, AZURE_API_VERSION, RATE_LIMIT_CHAT, DEBUG

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

    @field_validator('history')
    @classmethod
    def validate_total_history_size(cls, v: List[ChatMessage]) -> List[ChatMessage]:
        """Ensure total history size doesn't exceed reasonable limits to prevent token exhaustion.

        This prevents attackers from sending many large messages to consume excessive API tokens.
        """
        total_chars = sum(len(msg.content) for msg in v)
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
    client: AsyncAzureOpenAI = Depends(get_openai_client)
) -> ChatResponse:
    """Chat endpoint with AI assistant using tool calling.

    This endpoint allows users to send messages to the AI assistant and receive
    responses. The AI can call tools to fetch factory metrics and data.

    Rate limiting (PR7): This endpoint is rate-limited to prevent abuse.
    Default limit is 10 requests per minute per IP address (configurable via
    RATE_LIMIT_CHAT environment variable). Exceeded requests receive 429 error.

    Args:
        request: FastAPI Request object (required for rate limiting - slowapi)
        chat_request: Chat request containing message and conversation history
        client: Azure OpenAI client (injected dependency)

    Returns:
        ChatResponse containing AI response and updated conversation history

    Raises:
        HTTPException: If chat processing fails
        RateLimitExceeded: If rate limit is exceeded (returns 429 status)
    """
    # Generate request ID for tracking
    request_id = str(uuid.uuid4())
    start_time = time.time()

    logger.info(
        f"Chat request received [request_id={request_id}]: {chat_request.message[:50]}...",
        extra={
            "request_id": request_id,
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
