"""Chat API routes for AI assistant with tool calling."""

import logging
import uuid
import time
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from openai import AsyncAzureOpenAI

from shared.chat_service import get_chat_response, build_system_prompt
from shared.config import AZURE_ENDPOINT, AZURE_API_KEY, AZURE_API_VERSION

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["Chat"])


# Request/Response models
class ChatMessage(BaseModel):
    """Individual chat message model."""

    role: str = Field(description="Message role: user, assistant, system, or tool")
    content: str = Field(description="Message content")


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
async def chat(
    request: ChatRequest, client: AsyncAzureOpenAI = Depends(get_openai_client)
) -> ChatResponse:
    """Chat endpoint with AI assistant using tool calling.

    This endpoint allows users to send messages to the AI assistant and receive
    responses. The AI can call tools to fetch factory metrics and data.

    Args:
        request: Chat request containing message and conversation history
        client: Azure OpenAI client (injected dependency)

    Returns:
        ChatResponse containing AI response and updated conversation history

    Raises:
        HTTPException: If chat processing fails
    """
    # Generate request ID for tracking
    request_id = str(uuid.uuid4())
    start_time = time.time()

    logger.info(
        f"Chat request received [request_id={request_id}]: {request.message[:50]}...",
        extra={
            "request_id": request_id,
            "message_length": len(request.message),
            "history_size": len(request.history),
        },
    )

    try:
        # Build system prompt with factory context
        system_prompt = await build_system_prompt()

        # Convert ChatMessage objects to dictionaries for chat service
        history_dicts = [msg.model_dump() for msg in request.history]

        # Get AI response with tool calling
        response_text, updated_history_dicts = await get_chat_response(
            client=client,
            system_prompt=system_prompt,
            conversation_history=history_dicts,
            user_message=request.message,
        )

        # Convert updated history dictionaries back to ChatMessage objects
        updated_history = [ChatMessage(**msg) for msg in updated_history_dicts]

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
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")
