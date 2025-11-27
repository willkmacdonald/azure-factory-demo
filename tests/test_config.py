"""Tests for configuration module.

Tests cover:
- Required configuration constants are accessible
- OEE performance factor validation (PR24D)
- Prompt injection mode configuration (PR24D)
- Storage mode configuration

Note: Audio/voice configuration tests removed - the voice interface was deprecated
in favor of the web-only architecture (React + FastAPI).
"""

import pytest
from unittest.mock import patch
import os


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


def test_oee_performance_factor_default():
    """Verify OEE_PERFORMANCE_FACTOR has valid default (PR24D)."""
    from shared.config import OEE_PERFORMANCE_FACTOR

    assert isinstance(OEE_PERFORMANCE_FACTOR, float), "OEE_PERFORMANCE_FACTOR must be a float"
    assert 0.0 <= OEE_PERFORMANCE_FACTOR <= 1.0, "OEE_PERFORMANCE_FACTOR must be between 0.0 and 1.0"


def test_prompt_injection_mode_default():
    """Verify PROMPT_INJECTION_MODE has valid default (PR24D)."""
    from shared.config import PROMPT_INJECTION_MODE

    assert PROMPT_INJECTION_MODE in ("log", "block"), \
        f"PROMPT_INJECTION_MODE must be 'log' or 'block', got '{PROMPT_INJECTION_MODE}'"


def test_storage_mode_default():
    """Verify STORAGE_MODE has valid default."""
    from shared.config import STORAGE_MODE

    assert STORAGE_MODE in ("azure", "local"), \
        f"STORAGE_MODE must be 'azure' or 'local', got '{STORAGE_MODE}'"


def test_rate_limit_constants():
    """Verify rate limiting configuration constants."""
    from shared.config import RATE_LIMIT_CHAT, RATE_LIMIT_SETUP, RATE_LIMIT_SETUP_ANONYMOUS

    # Rate limits should be strings in format "N/period"
    assert "/" in RATE_LIMIT_CHAT, "RATE_LIMIT_CHAT should be in format 'N/period'"
    assert "/" in RATE_LIMIT_SETUP, "RATE_LIMIT_SETUP should be in format 'N/period'"
    assert "/" in RATE_LIMIT_SETUP_ANONYMOUS, "RATE_LIMIT_SETUP_ANONYMOUS should be in format 'N/period'"


def test_azure_blob_config():
    """Verify Azure Blob Storage configuration constants."""
    from shared.config import (
        AZURE_BLOB_CONTAINER,
        AZURE_BLOB_NAME,
        AZURE_BLOB_RETRY_TOTAL,
        AZURE_BLOB_MAX_UPLOAD_SIZE,
    )

    # Container and blob names should have defaults
    assert AZURE_BLOB_CONTAINER is not None, "AZURE_BLOB_CONTAINER should have a default"
    assert AZURE_BLOB_NAME is not None, "AZURE_BLOB_NAME should have a default"

    # Retry count should be positive
    assert isinstance(AZURE_BLOB_RETRY_TOTAL, int), "AZURE_BLOB_RETRY_TOTAL must be an integer"
    assert AZURE_BLOB_RETRY_TOTAL >= 0, "AZURE_BLOB_RETRY_TOTAL must be non-negative"

    # Max upload size should be positive (PR24C)
    assert isinstance(AZURE_BLOB_MAX_UPLOAD_SIZE, int), "AZURE_BLOB_MAX_UPLOAD_SIZE must be an integer"
    assert AZURE_BLOB_MAX_UPLOAD_SIZE > 0, "AZURE_BLOB_MAX_UPLOAD_SIZE must be positive"


def test_require_auth_default():
    """Verify REQUIRE_AUTH configuration (PR24B)."""
    from shared.config import REQUIRE_AUTH

    assert isinstance(REQUIRE_AUTH, bool), "REQUIRE_AUTH must be a boolean"


def test_debug_mode_default():
    """Verify DEBUG configuration."""
    from shared.config import DEBUG

    assert isinstance(DEBUG, bool), "DEBUG must be a boolean"


def test_memory_blob_name():
    """Verify memory blob configuration (PR25)."""
    from shared.config import MEMORY_BLOB_NAME

    assert MEMORY_BLOB_NAME is not None, "MEMORY_BLOB_NAME should have a default"
    assert MEMORY_BLOB_NAME.endswith(".json"), "MEMORY_BLOB_NAME should be a JSON file"
