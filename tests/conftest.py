"""Pytest configuration for root-level tests.

This module configures pytest behavior for tests in the tests/ directory.
It also provides shared test fixtures and helper functions.
"""

import pytest
from typing import Dict, Any, AsyncGenerator
from unittest.mock import AsyncMock, MagicMock
from contextlib import asynccontextmanager


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


# =============================================================================
# Azure Blob Storage Test Helpers
# =============================================================================


@pytest.fixture
def valid_connection_string() -> str:
    """Valid Azure Storage connection string for testing."""
    return "DefaultEndpointsProtocol=https;AccountName=testaccount;AccountKey=dGVzdGtleQ==;EndpointSuffix=core.windows.net"


@pytest.fixture
def test_data() -> Dict[str, Any]:
    """Sample production data for testing."""
    return {
        "machines": [
            {"id": "M001", "name": "CNC Mill 1", "status": "running"},
            {"id": "M002", "name": "Lathe 2", "status": "idle"}
        ],
        "metrics": {
            "oee": 0.85,
            "availability": 0.92,
            "performance": 0.93,
            "quality": 0.99
        }
    }


@pytest.fixture
def mock_blob_client_factory():
    """Factory fixture for creating mock blob clients.

    Returns a function that creates a mock blob client with the given mock
    service client. This allows tests to configure specific mock behaviors.

    Usage:
        def test_something(mock_blob_client_factory):
            mock_blob = AsyncMock()
            mock_service = mock_blob_client_factory(mock_blob)
    """
    def _create_mock_service_client(mock_blob_client: AsyncMock) -> MagicMock:
        """Create a mock service client that returns a mock blob client."""
        mock_service = MagicMock()
        mock_service.get_blob_client = MagicMock(return_value=mock_blob_client)
        return mock_service
    return _create_mock_service_client


@pytest.fixture
def mock_service_context_factory():
    """Factory fixture for creating async context manager wrappers.

    Returns a function that wraps a mock service client in an async
    context manager, matching the BlobStorageClient._get_service_client pattern.

    Usage:
        def test_something(mock_service_context_factory):
            mock_service = MagicMock()
            context = mock_service_context_factory(mock_service)
    """
    def _create_mock_service_context(mock_service: MagicMock):
        """Async context manager wrapper for mock service client."""
        @asynccontextmanager
        async def _context():
            yield mock_service
        return _context()
    return _create_mock_service_context
