"""Chat API routes for AI assistant with tool calling."""

import logging
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from openai import AsyncAzureOpenAI

from shared.chat_service import get_chat_response, build_system_prompt
from shared.config import AZURE_ENDPOINT, AZURE_API_KEY

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["Chat"])


# Request/Response models
class ChatMessage(BaseModel):
    """Individual chat message model."""

    role: str
    content: str


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""

    message: str
    history: List[Dict[str, Any]] = []


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""

    response: str
    history: List[Dict[str, Any]]


# Dependency: Get Azure OpenAI client
async def get_openai_client() -> AsyncAzureOpenAI:
    """Create and return AsyncAzureOpenAI client instance.

    Returns:
        AsyncAzureOpenAI: Configured Azure OpenAI client

    Raises:
        HTTPException: If Azure credentials are not configured
    """
    if not AZURE_ENDPOINT or not AZURE_API_KEY:
        logger.error("Azure OpenAI credentials not configured")
        raise HTTPException(
            status_code=500,
            detail="Azure OpenAI credentials not configured. Please set AZURE_ENDPOINT and AZURE_API_KEY environment variables.",
        )

    return AsyncAzureOpenAI(
        azure_endpoint=AZURE_ENDPOINT,
        api_key=AZURE_API_KEY,
        api_version="2024-08-01-preview",
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
    logger.info(f"Chat request received: {request.message[:50]}...")

    try:
        # Build system prompt with factory context
        system_prompt = await build_system_prompt()

        # Get AI response with tool calling
        response_text, updated_history = await get_chat_response(
            client=client,
            system_prompt=system_prompt,
            conversation_history=request.history,
            user_message=request.message,
        )

        logger.info("Chat response generated successfully")
        return ChatResponse(response=response_text, history=updated_history)

    except RuntimeError as e:
        # Handle data not available error
        logger.error(f"Runtime error in chat endpoint: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Unexpected error in chat endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")
