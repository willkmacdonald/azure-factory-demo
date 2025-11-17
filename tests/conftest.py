"""Pytest configuration for root-level tests.

This module configures pytest behavior for tests in the tests/ directory.
"""

import pytest


@pytest.fixture(scope="session")
def anyio_backend():
    """Configure pytest-anyio to use only asyncio backend (not trio).

    This project uses FastAPI which is built on asyncio. We don't need
    trio support, so we configure pytest-anyio to only test with asyncio.
    This prevents the "ModuleNotFoundError: No module named 'trio'" errors.

    Returns:
        str: The backend name ('asyncio')
    """
    return 'asyncio'
