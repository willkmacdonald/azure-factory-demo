"""
Smoke tests for extracted chat functions.

Tests the three functions extracted in PR #4:
- build_system_prompt(): System prompt generation
- get_chat_response(): AI API interaction with tool calling
- execute_tool(): Tool execution and routing

Functions moved from src.main to backend.src.services.chat_service for code reuse.
"""

import json
from typing import Any, Dict, List, Optional
from unittest.mock import Mock, patch
import sys
from pathlib import Path

import pytest

# Import from shared package (proper Python imports)
from shared.chat_service import build_system_prompt, get_chat_response, execute_tool


class TestBuildSystemPrompt:
    """Smoke tests for build_system_prompt()."""

    @pytest.mark.anyio
    @patch("shared.chat_service.load_data_async")
    async def test_includes_factory_context(self, mock_load_data_async):
        """Verify prompt includes factory name, dates, and machines."""
        mock_load_data_async.return_value = {
            "start_date": "2024-01-01T00:00:00",
            "end_date": "2024-01-30T23:59:59",
        }

        prompt = await build_system_prompt()

        # Check key components present
        assert "Demo Factory" in prompt
        assert "2024-01-01" in prompt
        assert "2024-01-30" in prompt
        assert "CNC-001" in prompt
        assert "Assembly-001" in prompt


class TestExecuteTool:
    """Smoke tests for execute_tool()."""

    @pytest.mark.anyio
    @patch("shared.chat_service.calculate_oee")
    async def test_routes_to_correct_function(self, mock_calculate_oee):
        """Verify tool routing works correctly."""
        mock_calculate_oee.return_value = {"oee": 85.5}

        result = await execute_tool(
            "calculate_oee",
            {"start_date": "2024-01-01", "end_date": "2024-01-07"},
        )

        mock_calculate_oee.assert_called_once_with(
            start_date="2024-01-01", end_date="2024-01-07"
        )
        assert result["oee"] == 85.5

    @pytest.mark.anyio
    async def test_returns_error_for_unknown_tool(self):
        """Verify unknown tools return error dict."""
        result = await execute_tool("nonexistent_tool", {})

        assert "error" in result
        assert "unknown" in result["error"].lower()


class TestGetChatResponse:
    """Smoke tests for get_chat_response()."""

    @pytest.mark.anyio
    async def test_handles_simple_response_without_tools(self):
        """Verify basic chat flow when AI doesn't use tools."""
        from unittest.mock import AsyncMock

        # Mock client that returns simple response
        mock_client = Mock()
        mock_message = Mock(content="Hello!", tool_calls=None)
        mock_client.chat.completions.create = AsyncMock(
            return_value=Mock(choices=[Mock(message=mock_message)])
        )

        response_text, new_history = await get_chat_response(
            client=mock_client,
            system_prompt="You are helpful.",
            conversation_history=[],
            user_message="Hi",
        )

        assert response_text == "Hello!"
        assert len(new_history) == 2  # user message + assistant response
        assert new_history[0]["role"] == "user"
        assert new_history[1]["role"] == "assistant"

    @pytest.mark.anyio
    @patch("shared.chat_service.execute_tool")
    async def test_handles_tool_calling_flow(self, mock_execute_tool):
        """Verify tool calling loop executes tools and returns response."""
        from unittest.mock import AsyncMock

        mock_execute_tool.return_value = {"oee": 85.5}

        mock_client = Mock()

        # First call: AI requests tool
        tool_call = Mock()
        tool_call.id = "call_123"
        tool_call.function = Mock()
        tool_call.function.name = "calculate_oee"
        tool_call.function.arguments = json.dumps(
            {"start_date": "2024-01-01", "end_date": "2024-01-07"}
        )

        first_message = Mock(tool_calls=[tool_call])
        first_message.model_dump = Mock(
            return_value={
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": "call_123",
                        "function": {
                            "name": "calculate_oee",
                            "arguments": json.dumps(
                                {"start_date": "2024-01-01", "end_date": "2024-01-07"}
                            ),
                        },
                    }
                ],
            }
        )

        # Second call: AI provides final answer
        second_message = Mock(content="The OEE is 85.5%", tool_calls=None)

        mock_client.chat.completions.create = AsyncMock(
            side_effect=[
                Mock(choices=[Mock(message=first_message)]),
                Mock(choices=[Mock(message=second_message)]),
            ]
        )

        response_text, new_history = await get_chat_response(
            client=mock_client,
            system_prompt="You are helpful.",
            conversation_history=[],
            user_message="What's the OEE?",
        )

        # Verify response and tool execution
        assert response_text == "The OEE is 85.5%"
        assert len(new_history) == 4  # user, assistant (tool), tool result, assistant
        mock_execute_tool.assert_called_once()

    @pytest.mark.anyio
    async def test_preserves_conversation_history(self):
        """Verify existing conversation history is included in API calls."""
        from unittest.mock import AsyncMock

        mock_client = Mock()
        mock_message = Mock(content="Response", tool_calls=None)
        mock_client.chat.completions.create = AsyncMock(
            return_value=Mock(choices=[Mock(message=mock_message)])
        )

        existing_history = [
            {"role": "user", "content": "Previous question"},
            {"role": "assistant", "content": "Previous answer"},
        ]

        await get_chat_response(
            client=mock_client,
            system_prompt="System prompt",
            conversation_history=existing_history,
            user_message="New question",
        )

        # Check that API call included existing history
        call_args = mock_client.chat.completions.create.call_args
        messages = call_args.kwargs["messages"]

        # Should have: system + 2 history + new user message
        assert len(messages) == 4
        assert messages[0]["role"] == "system"
        assert messages[1] == existing_history[0]
        assert messages[2] == existing_history[1]
        assert messages[3]["role"] == "user"
