"""Tests for configuration module."""

import pytest


def test_voice_config_constants():
    """Verify voice configuration constants are properly set."""
    from shared.config import TTS_VOICE, TTS_MODEL, WHISPER_MODEL, RECORDING_DURATION

    # Test TTS_VOICE is one of valid OpenAI voices
    valid_voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
    assert TTS_VOICE in valid_voices, f"TTS_VOICE must be one of {valid_voices}"

    # Test TTS_MODEL is valid
    valid_models = ["tts-1", "tts-1-hd"]
    assert TTS_MODEL in valid_models, f"TTS_MODEL must be one of {valid_models}"

    # Test WHISPER_MODEL
    assert WHISPER_MODEL == "whisper-1", "WHISPER_MODEL should be 'whisper-1'"

    # Test RECORDING_DURATION is positive integer
    assert isinstance(RECORDING_DURATION, int), "RECORDING_DURATION must be an integer"
    assert RECORDING_DURATION > 0, "RECORDING_DURATION must be positive"


def test_audio_dependencies_import():
    """Verify audio libraries can be imported."""
    try:
        import pyaudio
        import pydub
        import simpleaudio

        # If we get here, imports succeeded
        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import audio library: {e}")


def test_existing_config_constants():
    """Verify existing configuration constants are accessible."""
    from shared.config import (
        AZURE_API_KEY,
        AZURE_ENDPOINT,
        AZURE_DEPLOYMENT_NAME,
        FACTORY_NAME,
        DATA_FILE,
    )

    # These can be None/default, just verify they're accessible
    assert (
        AZURE_DEPLOYMENT_NAME is not None
    ), "AZURE_DEPLOYMENT_NAME should have a default value"
    assert FACTORY_NAME is not None, "FACTORY_NAME should have a default value"
    assert DATA_FILE is not None, "DATA_FILE should have a default value"
    # AZURE_API_KEY and AZURE_ENDPOINT can be None if not set in environment
