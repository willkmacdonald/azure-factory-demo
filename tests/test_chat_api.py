"""Tests for chat API endpoint with input validation (PR8)."""

import pytest
from pydantic import ValidationError
from backend.src.api.routes.chat import ChatMessage, ChatRequest


class TestChatMessageValidation:
    """Test ChatMessage model validation (PR8)."""

    def test_valid_user_message(self) -> None:
        """Test valid user message creation."""
        msg = ChatMessage(role="user", content="Hello, assistant!")
        assert msg.role == "user"
        assert msg.content == "Hello, assistant!"

    def test_valid_assistant_message(self) -> None:
        """Test valid assistant message creation."""
        msg = ChatMessage(role="assistant", content="Hello, how can I help?")
        assert msg.role == "assistant"
        assert msg.content == "Hello, how can I help?"

    def test_invalid_role_system(self) -> None:
        """Test that 'system' role is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ChatMessage(role="system", content="You are a helpful assistant")

        error = exc_info.value.errors()[0]
        assert "Invalid role 'system'" in str(error["ctx"]["error"])
        assert "user" in str(error["ctx"]["error"])
        assert "assistant" in str(error["ctx"]["error"])

    def test_invalid_role_tool(self) -> None:
        """Test that 'tool' role is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ChatMessage(role="tool", content="Tool response")

        error = exc_info.value.errors()[0]
        assert "Invalid role 'tool'" in str(error["ctx"]["error"])

    def test_invalid_role_custom(self) -> None:
        """Test that custom/random roles are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ChatMessage(role="hacker", content="Malicious content")

        error = exc_info.value.errors()[0]
        assert "Invalid role 'hacker'" in str(error["ctx"]["error"])

    def test_empty_content(self) -> None:
        """Test that empty content is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ChatMessage(role="user", content="")

        # Should fail on either min_length or custom validator
        errors = exc_info.value.errors()
        assert any("empty" in str(err).lower() or "at least 1" in str(err).lower()
                   for err in errors)

    def test_whitespace_only_content(self) -> None:
        """Test that whitespace-only content is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ChatMessage(role="user", content="   \t\n  ")

        error = exc_info.value.errors()[0]
        assert "empty" in str(error["ctx"]["error"]).lower() or "whitespace" in str(error["ctx"]["error"]).lower()

    def test_content_max_length(self) -> None:
        """Test that content exceeding max length is rejected."""
        long_content = "x" * 2001  # Max is 2000
        with pytest.raises(ValidationError) as exc_info:
            ChatMessage(role="user", content=long_content)

        error = exc_info.value.errors()[0]
        assert "2000" in str(error)

    def test_content_at_max_length(self) -> None:
        """Test that content at exactly max length is accepted."""
        max_content = "x" * 2000
        msg = ChatMessage(role="user", content=max_content)
        assert len(msg.content) == 2000


class TestChatRequestValidation:
    """Test ChatRequest model validation (PR8)."""

    def test_valid_request_no_history(self) -> None:
        """Test valid request without history."""
        req = ChatRequest(message="Hello!", history=[])
        assert req.message == "Hello!"
        assert len(req.history) == 0

    def test_valid_request_with_history(self) -> None:
        """Test valid request with conversation history."""
        history = [
            ChatMessage(role="user", content="First message"),
            ChatMessage(role="assistant", content="First response"),
            ChatMessage(role="user", content="Second message"),
        ]
        req = ChatRequest(message="Third message", history=history)
        assert req.message == "Third message"
        assert len(req.history) == 3

    def test_empty_message(self) -> None:
        """Test that empty message is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ChatRequest(message="", history=[])

        errors = exc_info.value.errors()[0]
        assert "at least 1" in str(errors).lower()

    def test_message_max_length(self) -> None:
        """Test that message exceeding max length is rejected."""
        long_message = "x" * 2001
        with pytest.raises(ValidationError) as exc_info:
            ChatRequest(message=long_message, history=[])

        error = exc_info.value.errors()[0]
        assert "2000" in str(error)

    def test_history_max_items(self) -> None:
        """Test that history exceeding 50 items is rejected."""
        # Create 51 messages
        large_history = [
            ChatMessage(role="user" if i % 2 == 0 else "assistant", content=f"Message {i}")
            for i in range(51)
        ]

        with pytest.raises(ValidationError) as exc_info:
            ChatRequest(message="Test", history=large_history)

        error = exc_info.value.errors()[0]
        assert "50" in str(error)

    def test_history_exactly_50_items(self) -> None:
        """Test that history with exactly 50 items is accepted."""
        history = [
            ChatMessage(role="user" if i % 2 == 0 else "assistant", content=f"Message {i}")
            for i in range(50)
        ]

        req = ChatRequest(message="Test", history=history)
        assert len(req.history) == 50

    def test_history_total_size_limit(self) -> None:
        """Test that total history character limit is enforced."""
        # Create messages that exceed 50K character limit
        # Each message has 1500 chars, 35 messages = 52,500 chars
        large_messages = [
            ChatMessage(
                role="user" if i % 2 == 0 else "assistant",
                content="x" * 1500
            )
            for i in range(35)
        ]

        with pytest.raises(ValidationError) as exc_info:
            ChatRequest(message="Test", history=large_messages)

        error = exc_info.value.errors()[0]
        assert "50000" in str(error["ctx"]["error"]) or "50K" in str(error["ctx"]["error"])

    def test_history_with_invalid_role(self) -> None:
        """Test that history with invalid roles is rejected."""
        invalid_history = [
            ChatMessage(role="user", content="Valid message"),
            # This should fail during ChatMessage creation
        ]

        with pytest.raises(ValidationError):
            # Try to create a message with invalid role
            invalid_msg = ChatMessage(role="system", content="Invalid")
            invalid_history.append(invalid_msg)

    def test_history_with_empty_content(self) -> None:
        """Test that history with empty content messages is rejected."""
        with pytest.raises(ValidationError):
            history = [ChatMessage(role="user", content="")]


class TestChatMessageEdgeCases:
    """Test edge cases for ChatMessage validation."""

    def test_role_case_sensitivity(self) -> None:
        """Test that role validation is case-sensitive."""
        with pytest.raises(ValidationError):
            ChatMessage(role="User", content="Test")  # Capital U

        with pytest.raises(ValidationError):
            ChatMessage(role="ASSISTANT", content="Test")  # All caps

    def test_unicode_content(self) -> None:
        """Test that Unicode content is handled properly."""
        msg = ChatMessage(role="user", content="Hello 世界! 🌍")
        assert msg.content == "Hello 世界! 🌍"

    def test_special_characters_in_content(self) -> None:
        """Test special characters in message content."""
        special_content = "Test with special chars: <script>alert('xss')</script>"
        msg = ChatMessage(role="user", content=special_content)
        assert msg.content == special_content

    def test_newlines_in_content(self) -> None:
        """Test that newlines in content are preserved."""
        multiline_content = "Line 1\nLine 2\nLine 3"
        msg = ChatMessage(role="user", content=multiline_content)
        assert "\n" in msg.content
        assert msg.content.count("\n") == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
