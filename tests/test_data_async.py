"""
Comprehensive tests for async data layer operations.

Tests cover:
- load_data_async() in both local and Azure storage modes
- save_data_async() in both local and Azure storage modes
- Data consistency across storage backends
- Auto-generation of missing blob in Azure mode
- Error handling and propagation
- Storage mode configuration
- Async file I/O operations
"""

import json
import pytest
import pytest_asyncio
from pathlib import Path
from typing import Dict, Any
from unittest.mock import AsyncMock, Mock, patch, mock_open
from shared.data import load_data_async, save_data_async, generate_production_data
from shared.blob_storage import BlobStorageClient


# Test Fixtures

@pytest.fixture
def test_data() -> Dict[str, Any]:
    """Sample production data for testing."""
    return {
        "machines": [
            {"id": 1, "name": "CNC-001", "type": "CNC Machining Center"},
            {"id": 2, "name": "Assembly-001", "type": "Assembly Station"}
        ],
        "metrics": {
            "oee": 0.85,
            "availability": 0.92,
            "performance": 0.93,
            "quality": 0.99
        },
        "production": [
            {
                "timestamp": "2025-01-01T10:00:00",
                "machine_id": 1,
                "units_produced": 100,
                "good_units": 98
            }
        ],
        "downtime_events": [],
        "quality_issues": [],
        "system_info": {
            "generated_at": "2025-01-01T00:00:00",
            "factory_name": "Test Factory",
            "days_generated": 30
        }
    }


@pytest.fixture
def temp_data_file(tmp_path: Path) -> Path:
    """Create temporary data file path."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    return data_dir / "production.json"


# Local Storage Mode Tests

@pytest.mark.asyncio
async def test_load_data_async_local_mode_success(test_data, temp_data_file):
    """Test load_data_async successfully loads from local JSON file."""
    # Write test data to file
    with open(temp_data_file, "w") as f:
        json.dump(test_data, f)

    with patch("shared.data.STORAGE_MODE", "local"):
        with patch("shared.data.DATA_FILE", str(temp_data_file)):
            result = await load_data_async()

            assert result is not None
            assert result == test_data
            assert result["machines"][0]["name"] == "CNC-001"
            assert result["metrics"]["oee"] == 0.85


@pytest.mark.asyncio
async def test_load_data_async_local_mode_file_missing(temp_data_file):
    """Test load_data_async returns None when local file doesn't exist."""
    with patch("shared.data.STORAGE_MODE", "local"):
        with patch("shared.data.DATA_FILE", str(temp_data_file)):
            result = await load_data_async()
            assert result is None


@pytest.mark.asyncio
async def test_load_data_async_local_mode_invalid_json(temp_data_file):
    """Test load_data_async raises RuntimeError on invalid JSON."""
    # Write invalid JSON
    with open(temp_data_file, "w") as f:
        f.write("{ this is not valid JSON }")

    with patch("shared.data.STORAGE_MODE", "local"):
        with patch("shared.data.DATA_FILE", str(temp_data_file)):
            with pytest.raises(RuntimeError) as exc_info:
                await load_data_async()
            assert "failed to parse json" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_save_data_async_local_mode_success(test_data, temp_data_file):
    """Test save_data_async successfully writes to local JSON file."""
    with patch("shared.data.STORAGE_MODE", "local"):
        with patch("shared.data.DATA_FILE", str(temp_data_file)):
            await save_data_async(test_data)

            # Verify file was created and contains correct data
            assert temp_data_file.exists()
            with open(temp_data_file, "r") as f:
                saved_data = json.load(f)
            assert saved_data == test_data


@pytest.mark.asyncio
async def test_save_data_async_local_mode_creates_directory(test_data, tmp_path):
    """Test save_data_async creates parent directory if it doesn't exist."""
    nested_path = tmp_path / "nested" / "dir" / "production.json"

    with patch("shared.data.STORAGE_MODE", "local"):
        with patch("shared.data.DATA_FILE", str(nested_path)):
            await save_data_async(test_data)

            # Verify directory and file were created
            assert nested_path.exists()
            assert nested_path.parent.exists()


# Azure Storage Mode Tests

@pytest.mark.asyncio
async def test_load_data_async_azure_mode_blob_exists(test_data):
    """Test load_data_async successfully loads from Azure Blob Storage."""
    mock_blob_client = AsyncMock(spec=BlobStorageClient)
    mock_blob_client.blob_exists = AsyncMock(return_value=True)
    mock_blob_client.download_blob = AsyncMock(return_value=test_data)
    mock_blob_client.close = AsyncMock()

    with patch("shared.data.STORAGE_MODE", "azure"):
        with patch("shared.data.BlobStorageClient", return_value=mock_blob_client):
            result = await load_data_async()

            assert result == test_data
            mock_blob_client.blob_exists.assert_called_once()
            mock_blob_client.download_blob.assert_called_once()
            mock_blob_client.close.assert_called_once()


@pytest.mark.asyncio
async def test_load_data_async_azure_mode_blob_missing_generates_data(test_data):
    """Test load_data_async generates and uploads data when blob doesn't exist."""
    mock_blob_client = AsyncMock(spec=BlobStorageClient)
    mock_blob_client.blob_exists = AsyncMock(return_value=False)
    mock_blob_client.upload_blob = AsyncMock()
    mock_blob_client.close = AsyncMock()

    with patch("shared.data.STORAGE_MODE", "azure"):
        with patch("shared.data.BlobStorageClient", return_value=mock_blob_client):
            with patch("shared.data.generate_production_data", return_value=test_data):
                result = await load_data_async()

                assert result == test_data
                mock_blob_client.blob_exists.assert_called_once()
                mock_blob_client.upload_blob.assert_called_once_with(test_data)
                mock_blob_client.close.assert_called_once()


@pytest.mark.asyncio
async def test_load_data_async_azure_mode_blob_error(test_data):
    """Test load_data_async propagates RuntimeError from blob client."""
    mock_blob_client = AsyncMock(spec=BlobStorageClient)
    mock_blob_client.blob_exists = AsyncMock(return_value=True)
    mock_blob_client.download_blob = AsyncMock(
        side_effect=RuntimeError("Blob download failed")
    )
    mock_blob_client.close = AsyncMock()

    with patch("shared.data.STORAGE_MODE", "azure"):
        with patch("shared.data.BlobStorageClient", return_value=mock_blob_client):
            with pytest.raises(RuntimeError) as exc_info:
                await load_data_async()

            assert "blob download failed" in str(exc_info.value).lower()
            mock_blob_client.close.assert_called_once()


@pytest.mark.asyncio
async def test_load_data_async_azure_mode_unexpected_error():
    """Test load_data_async wraps unexpected errors in RuntimeError."""
    mock_blob_client = AsyncMock(spec=BlobStorageClient)
    mock_blob_client.blob_exists = AsyncMock(
        side_effect=Exception("Unexpected error")
    )
    mock_blob_client.close = AsyncMock()

    with patch("shared.data.STORAGE_MODE", "azure"):
        with patch("shared.data.BlobStorageClient", return_value=mock_blob_client):
            with pytest.raises(RuntimeError) as exc_info:
                await load_data_async()

            assert "failed to load data from azure blob storage" in str(exc_info.value).lower()
            mock_blob_client.close.assert_called_once()


@pytest.mark.asyncio
async def test_save_data_async_azure_mode_success(test_data):
    """Test save_data_async successfully uploads to Azure Blob Storage."""
    mock_blob_client = AsyncMock(spec=BlobStorageClient)
    mock_blob_client.upload_blob = AsyncMock()
    mock_blob_client.close = AsyncMock()

    with patch("shared.data.STORAGE_MODE", "azure"):
        with patch("shared.data.BlobStorageClient", return_value=mock_blob_client):
            await save_data_async(test_data)

            mock_blob_client.upload_blob.assert_called_once_with(test_data)
            mock_blob_client.close.assert_called_once()


@pytest.mark.asyncio
async def test_save_data_async_azure_mode_blob_error():
    """Test save_data_async propagates RuntimeError from blob client."""
    test_data = {"test": "data"}
    mock_blob_client = AsyncMock(spec=BlobStorageClient)
    mock_blob_client.upload_blob = AsyncMock(
        side_effect=RuntimeError("Blob upload failed")
    )
    mock_blob_client.close = AsyncMock()

    with patch("shared.data.STORAGE_MODE", "azure"):
        with patch("shared.data.BlobStorageClient", return_value=mock_blob_client):
            with pytest.raises(RuntimeError) as exc_info:
                await save_data_async(test_data)

            assert "blob upload failed" in str(exc_info.value).lower()
            mock_blob_client.close.assert_called_once()


@pytest.mark.asyncio
async def test_save_data_async_azure_mode_unexpected_error():
    """Test save_data_async wraps unexpected errors in RuntimeError."""
    test_data = {"test": "data"}
    mock_blob_client = AsyncMock(spec=BlobStorageClient)
    mock_blob_client.upload_blob = AsyncMock(
        side_effect=Exception("Unexpected error")
    )
    mock_blob_client.close = AsyncMock()

    with patch("shared.data.STORAGE_MODE", "azure"):
        with patch("shared.data.BlobStorageClient", return_value=mock_blob_client):
            with pytest.raises(RuntimeError) as exc_info:
                await save_data_async(test_data)

            assert "failed to save data to azure blob storage" in str(exc_info.value).lower()
            mock_blob_client.close.assert_called_once()


# Data Consistency Tests

@pytest.mark.asyncio
async def test_data_consistency_local_mode(test_data, temp_data_file):
    """Test save-load cycle maintains data integrity in local mode."""
    with patch("shared.data.STORAGE_MODE", "local"):
        with patch("shared.data.DATA_FILE", str(temp_data_file)):
            # Save
            await save_data_async(test_data)

            # Load
            loaded_data = await load_data_async()

            # Verify data integrity
            assert loaded_data == test_data
            assert loaded_data["machines"][0]["id"] == 1
            assert loaded_data["metrics"]["oee"] == 0.85


@pytest.mark.asyncio
async def test_data_consistency_azure_mode(test_data):
    """Test save-load cycle maintains data integrity in Azure mode."""
    # Mock blob client for save
    mock_save_client = AsyncMock(spec=BlobStorageClient)
    mock_save_client.upload_blob = AsyncMock()
    mock_save_client.close = AsyncMock()

    # Mock blob client for load
    mock_load_client = AsyncMock(spec=BlobStorageClient)
    mock_load_client.blob_exists = AsyncMock(return_value=True)
    mock_load_client.download_blob = AsyncMock(return_value=test_data)
    mock_load_client.close = AsyncMock()

    with patch("shared.data.STORAGE_MODE", "azure"):
        with patch("shared.data.BlobStorageClient", side_effect=[mock_save_client, mock_load_client]):
            # Save
            await save_data_async(test_data)

            # Load
            loaded_data = await load_data_async()

            # Verify data integrity
            assert loaded_data == test_data


# Storage Mode Configuration Tests

@pytest.mark.asyncio
async def test_storage_mode_case_insensitive_local(test_data, temp_data_file):
    """Test storage mode is case-insensitive for local mode."""
    with open(temp_data_file, "w") as f:
        json.dump(test_data, f)

    for mode in ["LOCAL", "Local", "local", "LOcaL"]:
        with patch("shared.data.STORAGE_MODE", mode):
            with patch("shared.data.DATA_FILE", str(temp_data_file)):
                result = await load_data_async()
                assert result == test_data


@pytest.mark.asyncio
async def test_storage_mode_case_insensitive_azure(test_data):
    """Test storage mode is case-insensitive for Azure mode."""
    mock_blob_client = AsyncMock(spec=BlobStorageClient)
    mock_blob_client.blob_exists = AsyncMock(return_value=True)
    mock_blob_client.download_blob = AsyncMock(return_value=test_data)
    mock_blob_client.close = AsyncMock()

    for mode in ["AZURE", "Azure", "azure", "AzUrE"]:
        with patch("shared.data.STORAGE_MODE", mode):
            with patch("shared.data.BlobStorageClient", return_value=mock_blob_client):
                result = await load_data_async()
                assert result == test_data


@pytest.mark.asyncio
async def test_default_mode_is_local(test_data, temp_data_file):
    """Test that unrecognized storage modes default to local."""
    with open(temp_data_file, "w") as f:
        json.dump(test_data, f)

    # Any non-azure value should use local mode
    for mode in ["", "unknown", "s3", "gcs"]:
        with patch("shared.data.STORAGE_MODE", mode):
            with patch("shared.data.DATA_FILE", str(temp_data_file)):
                result = await load_data_async()
                assert result == test_data


# Client Cleanup Tests

@pytest.mark.asyncio
async def test_load_data_async_azure_closes_client_on_success(test_data):
    """Test load_data_async closes blob client after successful operation."""
    mock_blob_client = AsyncMock(spec=BlobStorageClient)
    mock_blob_client.blob_exists = AsyncMock(return_value=True)
    mock_blob_client.download_blob = AsyncMock(return_value=test_data)
    mock_blob_client.close = AsyncMock()

    with patch("shared.data.STORAGE_MODE", "azure"):
        with patch("shared.data.BlobStorageClient", return_value=mock_blob_client):
            await load_data_async()

            mock_blob_client.close.assert_called_once()


@pytest.mark.asyncio
async def test_load_data_async_azure_closes_client_on_error():
    """Test load_data_async closes blob client even when error occurs."""
    mock_blob_client = AsyncMock(spec=BlobStorageClient)
    mock_blob_client.blob_exists = AsyncMock(
        side_effect=RuntimeError("Test error")
    )
    mock_blob_client.close = AsyncMock()

    with patch("shared.data.STORAGE_MODE", "azure"):
        with patch("shared.data.BlobStorageClient", return_value=mock_blob_client):
            with pytest.raises(RuntimeError):
                await load_data_async()

            # Client should still be closed
            mock_blob_client.close.assert_called_once()


@pytest.mark.asyncio
async def test_save_data_async_azure_closes_client_on_success(test_data):
    """Test save_data_async closes blob client after successful operation."""
    mock_blob_client = AsyncMock(spec=BlobStorageClient)
    mock_blob_client.upload_blob = AsyncMock()
    mock_blob_client.close = AsyncMock()

    with patch("shared.data.STORAGE_MODE", "azure"):
        with patch("shared.data.BlobStorageClient", return_value=mock_blob_client):
            await save_data_async(test_data)

            mock_blob_client.close.assert_called_once()


@pytest.mark.asyncio
async def test_save_data_async_azure_closes_client_on_error():
    """Test save_data_async closes blob client even when error occurs."""
    test_data = {"test": "data"}
    mock_blob_client = AsyncMock(spec=BlobStorageClient)
    mock_blob_client.upload_blob = AsyncMock(
        side_effect=RuntimeError("Test error")
    )
    mock_blob_client.close = AsyncMock()

    with patch("shared.data.STORAGE_MODE", "azure"):
        with patch("shared.data.BlobStorageClient", return_value=mock_blob_client):
            with pytest.raises(RuntimeError):
                await save_data_async(test_data)

            # Client should still be closed
            mock_blob_client.close.assert_called_once()


# Edge Cases and Performance Tests

@pytest.mark.asyncio
async def test_load_data_async_handles_large_data(temp_data_file):
    """Test load_data_async handles large JSON files efficiently."""
    # Generate large dataset
    large_data = {
        "machines": [{"id": i, "name": f"Machine-{i}"} for i in range(1000)],
        "production": [
            {
                "timestamp": f"2025-01-01T{h:02d}:{m:02d}:00",
                "machine_id": machine_id,
                "units": 100
            }
            for h in range(24)
            for m in range(60)
            for machine_id in range(10)
        ]
    }

    with open(temp_data_file, "w") as f:
        json.dump(large_data, f)

    with patch("shared.data.STORAGE_MODE", "local"):
        with patch("shared.data.DATA_FILE", str(temp_data_file)):
            result = await load_data_async()

            assert result is not None
            assert len(result["machines"]) == 1000
            assert len(result["production"]) == 14400  # 24 * 60 * 10


@pytest.mark.asyncio
async def test_save_data_async_handles_special_characters(temp_data_file):
    """Test save_data_async properly escapes special characters."""
    special_data = {
        "machines": [
            {"name": "Machine with \"quotes\""},
            {"name": "Machine with \nnewlines"},
            {"name": "Machine with 中文字符"},
            {"name": "Machine with emoji 🏭"}
        ]
    }

    with patch("shared.data.STORAGE_MODE", "local"):
        with patch("shared.data.DATA_FILE", str(temp_data_file)):
            await save_data_async(special_data)

            # Reload and verify
            loaded_data = await load_data_async()
            assert loaded_data == special_data
            assert loaded_data["machines"][2]["name"] == "Machine with 中文字符"
            assert loaded_data["machines"][3]["name"] == "Machine with emoji 🏭"
