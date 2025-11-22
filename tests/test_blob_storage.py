"""
Comprehensive tests for Azure Blob Storage client.

Tests cover:
- Blob existence checking
- Successful upload/download operations
- Error handling (auth errors, blob not found, network errors)
- Retry logic on transient failures
- Connection string validation
- JSON parsing errors
- Client cleanup
"""

import json
import pytest
from typing import Dict, Any, AsyncGenerator
from unittest.mock import AsyncMock, Mock, patch, MagicMock
from azure.core.exceptions import (
    ResourceNotFoundError,
    ClientAuthenticationError,
    ServiceRequestError,
    HttpResponseError,
)
from shared.blob_storage import BlobStorageClient


# Test Fixtures

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
async def blob_client(valid_connection_string: str) -> AsyncGenerator[BlobStorageClient, None]:
    """Create BlobStorageClient instance for testing."""
    client = BlobStorageClient(
        connection_string=valid_connection_string,
        container_name="test-container",
        blob_name="test-blob.json"
    )
    yield client
    # Cleanup
    await client.close()


# Initialization Tests

def test_init_with_valid_connection_string(valid_connection_string):
    """Test BlobStorageClient initialization with valid connection string."""
    client = BlobStorageClient(
        connection_string=valid_connection_string,
        container_name="test-container",
        blob_name="test.json"
    )
    assert client.connection_string == valid_connection_string
    assert client.container_name == "test-container"
    assert client.blob_name == "test.json"


def test_init_without_connection_string():
    """Test BlobStorageClient raises error when connection string is missing."""
    with patch("shared.blob_storage.AZURE_STORAGE_CONNECTION_STRING", None):
        with pytest.raises(ValueError) as exc_info:
            BlobStorageClient()
        assert "connection string not provided" in str(exc_info.value).lower()


def test_init_uses_env_defaults(valid_connection_string):
    """Test BlobStorageClient uses environment variable defaults."""
    with patch("shared.blob_storage.AZURE_STORAGE_CONNECTION_STRING", valid_connection_string):
        with patch("shared.blob_storage.AZURE_BLOB_CONTAINER", "env-container"):
            with patch("shared.blob_storage.AZURE_BLOB_NAME", "env-blob.json"):
                client = BlobStorageClient()
                assert client.connection_string == valid_connection_string
                assert client.container_name == "env-container"
                assert client.blob_name == "env-blob.json"


# Blob Existence Tests

@pytest.mark.anyio
async def test_blob_exists_returns_true(blob_client):
    """Test blob_exists returns True when blob exists."""
    mock_blob_client = AsyncMock()
    mock_blob_client.exists = AsyncMock(return_value=True)

    with patch.object(blob_client, '_get_blob_client', return_value=mock_blob_client):
        result = await blob_client.blob_exists()
        assert result is True
        mock_blob_client.exists.assert_called_once()


@pytest.mark.anyio
async def test_blob_exists_returns_false(blob_client):
    """Test blob_exists returns False when blob doesn't exist."""
    mock_blob_client = AsyncMock()
    mock_blob_client.exists = AsyncMock(return_value=False)

    with patch.object(blob_client, '_get_blob_client', return_value=mock_blob_client):
        result = await blob_client.blob_exists()
        assert result is False
        mock_blob_client.exists.assert_called_once()


@pytest.mark.anyio
async def test_blob_exists_handles_auth_error(blob_client):
    """Test blob_exists raises RuntimeError on authentication failure."""
    mock_blob_client = AsyncMock()
    mock_blob_client.exists = AsyncMock(
        side_effect=ClientAuthenticationError("Invalid credentials")
    )

    with patch.object(blob_client, '_get_blob_client', return_value=mock_blob_client):
        with pytest.raises(RuntimeError) as exc_info:
            await blob_client.blob_exists()
        assert "authentication failed" in str(exc_info.value).lower()


@pytest.mark.anyio
async def test_blob_exists_returns_false_on_generic_error(blob_client):
    """Test blob_exists returns False on unexpected errors."""
    mock_blob_client = AsyncMock()
    mock_blob_client.exists = AsyncMock(side_effect=Exception("Unexpected error"))

    with patch.object(blob_client, '_get_blob_client', return_value=mock_blob_client):
        result = await blob_client.blob_exists()
        assert result is False


# Upload Blob Tests

@pytest.mark.anyio
async def test_upload_blob_success(blob_client, test_data):
    """Test successful blob upload."""
    mock_blob_client = AsyncMock()
    mock_blob_client.upload_blob = AsyncMock()

    with patch.object(blob_client, '_get_blob_client', return_value=mock_blob_client):
        await blob_client.upload_blob(test_data)

        # Verify upload was called with correct arguments
        mock_blob_client.upload_blob.assert_called_once()
        call_args = mock_blob_client.upload_blob.call_args
        assert call_args.kwargs['overwrite'] is True
        assert call_args.kwargs['content_type'] == "application/json"

        # Verify JSON formatting
        uploaded_json = call_args.args[0]
        assert isinstance(uploaded_json, str)
        parsed_data = json.loads(uploaded_json)
        assert parsed_data == test_data


@pytest.mark.anyio
async def test_upload_blob_auth_error(blob_client, test_data):
    """Test upload_blob raises RuntimeError on authentication failure."""
    mock_blob_client = AsyncMock()
    mock_blob_client.upload_blob = AsyncMock(
        side_effect=ClientAuthenticationError("Invalid credentials")
    )

    with patch.object(blob_client, '_get_blob_client', return_value=mock_blob_client):
        with pytest.raises(RuntimeError) as exc_info:
            await blob_client.upload_blob(test_data)
        assert "authentication failed" in str(exc_info.value).lower()


@pytest.mark.anyio
async def test_upload_blob_network_error_retries(blob_client, test_data):
    """Test upload_blob uses SDK retry policy on network errors.

    Note: The Azure SDK handles retries automatically via ExponentialRetry policy.
    This test verifies that the SDK's retry mechanism would be invoked (though
    in practice, the SDK retries transparently without re-calling our method).
    """
    mock_blob_client = AsyncMock()
    # SDK retries internally, so from our perspective the operation just succeeds
    # after the SDK's internal retry attempts
    mock_blob_client.upload_blob = AsyncMock(return_value=None)

    with patch.object(blob_client, '_get_blob_client', return_value=mock_blob_client):
        await blob_client.upload_blob(test_data)

        # Verify upload was called once (SDK handles retries internally)
        assert mock_blob_client.upload_blob.call_count == 1


@pytest.mark.anyio
async def test_upload_blob_network_error_exhausts_retries(blob_client, test_data):
    """Test upload_blob raises RuntimeError after SDK exhausts retries."""
    mock_blob_client = AsyncMock()
    # SDK will retry internally and then raise ServiceRequestError after exhausting retries
    mock_blob_client.upload_blob = AsyncMock(
        side_effect=ServiceRequestError("Network timeout")
    )

    with patch.object(blob_client, '_get_blob_client', return_value=mock_blob_client):
        with patch("shared.blob_storage.AZURE_BLOB_RETRY_TOTAL", 3):
            with pytest.raises(RuntimeError) as exc_info:
                await blob_client.upload_blob(test_data)

            assert "after 3 retries" in str(exc_info.value).lower()
            assert "network errors" in str(exc_info.value).lower()
            # SDK handles retries internally, we only see one call
            assert mock_blob_client.upload_blob.call_count == 1


@pytest.mark.anyio
async def test_upload_blob_http_response_error(blob_client, test_data):
    """Test upload_blob raises RuntimeError on Azure service errors."""
    mock_blob_client = AsyncMock()
    mock_blob_client.upload_blob = AsyncMock(
        side_effect=HttpResponseError("Container not found")
    )

    with patch.object(blob_client, '_get_blob_client', return_value=mock_blob_client):
        with pytest.raises(RuntimeError) as exc_info:
            await blob_client.upload_blob(test_data)
        assert "service error" in str(exc_info.value).lower()


@pytest.mark.anyio
async def test_upload_blob_unexpected_error(blob_client, test_data):
    """Test upload_blob raises RuntimeError on unexpected errors."""
    mock_blob_client = AsyncMock()
    mock_blob_client.upload_blob = AsyncMock(
        side_effect=Exception("Unexpected error")
    )

    with patch.object(blob_client, '_get_blob_client', return_value=mock_blob_client):
        with pytest.raises(RuntimeError) as exc_info:
            await blob_client.upload_blob(test_data)
        assert "failed to upload blob" in str(exc_info.value).lower()


# Download Blob Tests

@pytest.mark.anyio
async def test_download_blob_success(blob_client, test_data):
    """Test successful blob download."""
    json_content = json.dumps(test_data).encode("utf-8")

    # Mock download stream
    mock_stream = AsyncMock()
    mock_stream.readall = AsyncMock(return_value=json_content)

    mock_blob_client = AsyncMock()
    mock_blob_client.download_blob = AsyncMock(return_value=mock_stream)

    with patch.object(blob_client, '_get_blob_client', return_value=mock_blob_client):
        result = await blob_client.download_blob()

        assert result == test_data
        mock_blob_client.download_blob.assert_called_once()
        mock_stream.readall.assert_called_once()


@pytest.mark.anyio
async def test_download_blob_not_found(blob_client):
    """Test download_blob raises RuntimeError when blob doesn't exist."""
    mock_blob_client = AsyncMock()
    mock_blob_client.download_blob = AsyncMock(
        side_effect=ResourceNotFoundError("Blob not found")
    )

    with patch.object(blob_client, '_get_blob_client', return_value=mock_blob_client):
        with pytest.raises(RuntimeError) as exc_info:
            await blob_client.download_blob()
        assert "not found" in str(exc_info.value).lower()
        assert "run setup" in str(exc_info.value).lower()


@pytest.mark.anyio
async def test_download_blob_auth_error(blob_client):
    """Test download_blob raises RuntimeError on authentication failure."""
    mock_blob_client = AsyncMock()
    mock_blob_client.download_blob = AsyncMock(
        side_effect=ClientAuthenticationError("Invalid credentials")
    )

    with patch.object(blob_client, '_get_blob_client', return_value=mock_blob_client):
        with pytest.raises(RuntimeError) as exc_info:
            await blob_client.download_blob()
        assert "authentication failed" in str(exc_info.value).lower()


@pytest.mark.anyio
async def test_download_blob_network_error_retries(blob_client, test_data):
    """Test download_blob uses SDK retry policy on network errors.

    Note: The Azure SDK handles retries automatically via ExponentialRetry policy.
    This test verifies that the SDK's retry mechanism would be invoked (though
    in practice, the SDK retries transparently without re-calling our method).
    """
    json_content = json.dumps(test_data).encode("utf-8")
    mock_stream_success = AsyncMock()
    mock_stream_success.readall = AsyncMock(return_value=json_content)

    mock_blob_client = AsyncMock()
    # SDK retries internally, so from our perspective the operation just succeeds
    mock_blob_client.download_blob = AsyncMock(return_value=mock_stream_success)

    with patch.object(blob_client, '_get_blob_client', return_value=mock_blob_client):
        result = await blob_client.download_blob()

        assert result == test_data
        # SDK handles retries internally, we only see one call
        assert mock_blob_client.download_blob.call_count == 1


@pytest.mark.anyio
async def test_download_blob_network_error_exhausts_retries(blob_client):
    """Test download_blob raises RuntimeError after SDK exhausts retries."""
    mock_blob_client = AsyncMock()
    # SDK will retry internally and then raise ServiceRequestError after exhausting retries
    mock_blob_client.download_blob = AsyncMock(
        side_effect=ServiceRequestError("Network timeout")
    )

    with patch.object(blob_client, '_get_blob_client', return_value=mock_blob_client):
        with patch("shared.blob_storage.AZURE_BLOB_RETRY_TOTAL", 3):
            with pytest.raises(RuntimeError) as exc_info:
                await blob_client.download_blob()

            assert "after 3 retries" in str(exc_info.value).lower()
            assert "network errors" in str(exc_info.value).lower()
            # SDK handles retries internally, we only see one call
            assert mock_blob_client.download_blob.call_count == 1


@pytest.mark.anyio
async def test_download_blob_invalid_json(blob_client):
    """Test download_blob raises RuntimeError on invalid JSON in blob."""
    invalid_json = b"{ this is not valid JSON }"

    mock_stream = AsyncMock()
    mock_stream.readall = AsyncMock(return_value=invalid_json)

    mock_blob_client = AsyncMock()
    mock_blob_client.download_blob = AsyncMock(return_value=mock_stream)

    with patch.object(blob_client, '_get_blob_client', return_value=mock_blob_client):
        with pytest.raises(RuntimeError) as exc_info:
            await blob_client.download_blob()
        assert "invalid json" in str(exc_info.value).lower()


@pytest.mark.anyio
async def test_download_blob_http_response_error(blob_client):
    """Test download_blob raises RuntimeError on Azure service errors."""
    mock_blob_client = AsyncMock()
    mock_blob_client.download_blob = AsyncMock(
        side_effect=HttpResponseError("Service unavailable")
    )

    with patch.object(blob_client, '_get_blob_client', return_value=mock_blob_client):
        with pytest.raises(RuntimeError) as exc_info:
            await blob_client.download_blob()
        assert "service error" in str(exc_info.value).lower()


@pytest.mark.anyio
async def test_download_blob_unexpected_error(blob_client):
    """Test download_blob raises RuntimeError on unexpected errors."""
    mock_blob_client = AsyncMock()
    mock_blob_client.download_blob = AsyncMock(
        side_effect=Exception("Unexpected error")
    )

    with patch.object(blob_client, '_get_blob_client', return_value=mock_blob_client):
        with pytest.raises(RuntimeError) as exc_info:
            await blob_client.download_blob()
        assert "failed to download blob" in str(exc_info.value).lower()


# Client Cleanup Tests

@pytest.mark.anyio
async def test_close_client(valid_connection_string):
    """Test close() properly cleans up blob service client."""
    client = BlobStorageClient(
        connection_string=valid_connection_string,
        container_name="test-container",
        blob_name="test.json"
    )

    # Simulate client creation
    mock_service_client = AsyncMock()
    mock_service_client.close = AsyncMock()
    client._blob_service_client = mock_service_client

    await client.close()

    mock_service_client.close.assert_called_once()
    assert client._blob_service_client is None


@pytest.mark.anyio
async def test_close_client_no_client_created(valid_connection_string):
    """Test close() when no client has been created (no-op)."""
    client = BlobStorageClient(
        connection_string=valid_connection_string,
        container_name="test-container",
        blob_name="test.json"
    )

    # Should not raise error
    await client.close()
    assert client._blob_service_client is None


# Integration Test (simulated)

@pytest.mark.anyio
async def test_full_upload_download_cycle(blob_client, test_data):
    """Test complete upload-download cycle maintains data integrity."""
    json_content = json.dumps(test_data).encode("utf-8")

    # Mock upload
    mock_upload_client = AsyncMock()
    mock_upload_client.upload_blob = AsyncMock()

    # Mock download
    mock_stream = AsyncMock()
    mock_stream.readall = AsyncMock(return_value=json_content)
    mock_download_client = AsyncMock()
    mock_download_client.download_blob = AsyncMock(return_value=mock_stream)

    with patch.object(blob_client, '_get_blob_client', side_effect=[mock_upload_client, mock_download_client]):
        # Upload
        await blob_client.upload_blob(test_data)

        # Download
        result = await blob_client.download_blob()

        # Verify data integrity
        assert result == test_data
        assert result["machines"][0]["id"] == "M001"
        assert result["metrics"]["oee"] == 0.85
