"""Azure Blob Storage client wrapper for async operations."""

import json
import logging
from typing import Dict, Any, Optional
from azure.storage.blob.aio import BlobServiceClient, BlobClient, ContainerClient
from azure.core.exceptions import (
    ResourceNotFoundError,
    ClientAuthenticationError,
    ServiceRequestError,
    HttpResponseError,
)
from .config import (
    AZURE_STORAGE_CONNECTION_STRING,
    AZURE_BLOB_CONTAINER,
    AZURE_BLOB_NAME,
)

logger = logging.getLogger(__name__)


class BlobStorageClient:
    """
    Async Azure Blob Storage client for reading and writing production data.

    This class provides async methods for:
    - Uploading JSON data to Azure Blob Storage
    - Downloading JSON data from Azure Blob Storage
    - Checking blob existence
    - Retry logic for transient failures
    """

    def __init__(
        self,
        connection_string: Optional[str] = None,
        container_name: Optional[str] = None,
        blob_name: Optional[str] = None,
    ):
        """
        Initialize blob storage client.

        Args:
            connection_string: Azure Storage connection string (defaults to env var)
            container_name: Blob container name (defaults to env var)
            blob_name: Blob file name (defaults to env var)
        """
        self.connection_string = connection_string or AZURE_STORAGE_CONNECTION_STRING
        self.container_name = container_name or AZURE_BLOB_CONTAINER
        self.blob_name = blob_name or AZURE_BLOB_NAME

        if not self.connection_string:
            raise ValueError(
                "Azure Storage connection string not provided. "
                "Set AZURE_STORAGE_CONNECTION_STRING environment variable."
            )

        # Client will be created per-operation (async context manager pattern)
        self._blob_service_client: Optional[BlobServiceClient] = None

    async def _get_blob_client(self) -> BlobClient:
        """
        Get blob client for operations.

        Returns:
            BlobClient instance configured for the production data blob
        """
        if not self._blob_service_client:
            self._blob_service_client = BlobServiceClient.from_connection_string(
                self.connection_string
            )

        return self._blob_service_client.get_blob_client(
            container=self.container_name, blob=self.blob_name
        )

    async def blob_exists(self) -> bool:
        """
        Check if the production data blob exists.

        Returns:
            True if blob exists, False otherwise
        """
        try:
            blob_client = await self._get_blob_client()
            exists = await blob_client.exists()
            logger.debug(
                f"Blob exists check: {self.blob_name} in {self.container_name} = {exists}"
            )
            return exists
        except ClientAuthenticationError as e:
            logger.error(
                f"Authentication failed for Azure Blob Storage: {e}. "
                "Check your AZURE_STORAGE_CONNECTION_STRING"
            )
            raise RuntimeError(
                "Azure Blob Storage authentication failed. "
                "Verify your connection string is correct."
            ) from e
        except Exception as e:
            logger.error(f"Error checking blob existence: {e}")
            return False

    async def upload_blob(self, data: Dict[str, Any], max_retries: int = 3) -> None:
        """
        Upload JSON data to Azure Blob Storage with retry logic.

        Args:
            data: Dictionary to upload as JSON
            max_retries: Maximum number of retry attempts for transient failures

        Raises:
            RuntimeError: If upload fails after all retries
        """
        json_data = json.dumps(data, indent=2, default=str)

        for attempt in range(max_retries):
            try:
                blob_client = await self._get_blob_client()
                await blob_client.upload_blob(
                    json_data, overwrite=True, content_type="application/json"
                )
                logger.info(
                    f"Successfully uploaded {len(json_data)} bytes to blob "
                    f"{self.blob_name} in {self.container_name}"
                )
                return
            except ClientAuthenticationError as e:
                logger.error(f"Authentication error uploading blob: {e}")
                raise RuntimeError(
                    "Azure Blob Storage authentication failed. "
                    "Check AZURE_STORAGE_CONNECTION_STRING."
                ) from e
            except ServiceRequestError as e:
                # Network error - retry
                if attempt < max_retries - 1:
                    logger.warning(
                        f"Network error uploading blob (attempt {attempt + 1}/{max_retries}): {e}. "
                        "Retrying..."
                    )
                    continue
                else:
                    logger.error(f"Network error uploading blob after {max_retries} attempts: {e}")
                    raise RuntimeError(
                        f"Failed to upload blob after {max_retries} attempts due to network errors"
                    ) from e
            except HttpResponseError as e:
                logger.error(f"Azure service error uploading blob: {e}")
                raise RuntimeError(f"Azure Blob Storage service error: {e}") from e
            except Exception as e:
                logger.error(f"Unexpected error uploading blob: {e}")
                raise RuntimeError(f"Failed to upload blob: {e}") from e

    async def download_blob(self, max_retries: int = 3) -> Dict[str, Any]:
        """
        Download JSON data from Azure Blob Storage with retry logic.

        Args:
            max_retries: Maximum number of retry attempts for transient failures

        Returns:
            Dictionary containing the blob's JSON data

        Raises:
            RuntimeError: If download fails after all retries or blob doesn't exist
        """
        for attempt in range(max_retries):
            try:
                blob_client = await self._get_blob_client()
                # Download blob content
                stream = await blob_client.download_blob()
                content = await stream.readall()

                # Parse JSON
                data = json.loads(content.decode("utf-8"))
                logger.info(
                    f"Successfully downloaded {len(content)} bytes from blob "
                    f"{self.blob_name} in {self.container_name}"
                )
                return data

            except ResourceNotFoundError as e:
                logger.error(
                    f"Blob not found: {self.blob_name} in container {self.container_name}"
                )
                raise RuntimeError(
                    f"Production data blob '{self.blob_name}' not found in container "
                    f"'{self.container_name}'. Run setup to generate initial data."
                ) from e
            except ClientAuthenticationError as e:
                logger.error(f"Authentication error downloading blob: {e}")
                raise RuntimeError(
                    "Azure Blob Storage authentication failed. "
                    "Check AZURE_STORAGE_CONNECTION_STRING."
                ) from e
            except ServiceRequestError as e:
                # Network error - retry
                if attempt < max_retries - 1:
                    logger.warning(
                        f"Network error downloading blob (attempt {attempt + 1}/{max_retries}): {e}. "
                        "Retrying..."
                    )
                    continue
                else:
                    logger.error(
                        f"Network error downloading blob after {max_retries} attempts: {e}"
                    )
                    raise RuntimeError(
                        f"Failed to download blob after {max_retries} attempts due to network errors"
                    ) from e
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON from blob: {e}")
                raise RuntimeError(
                    f"Blob '{self.blob_name}' contains invalid JSON: {e}"
                ) from e
            except HttpResponseError as e:
                logger.error(f"Azure service error downloading blob: {e}")
                raise RuntimeError(f"Azure Blob Storage service error: {e}") from e
            except Exception as e:
                logger.error(f"Unexpected error downloading blob: {e}")
                raise RuntimeError(f"Failed to download blob: {e}") from e

    async def close(self) -> None:
        """Close the blob service client."""
        if self._blob_service_client:
            await self._blob_service_client.close()
            self._blob_service_client = None
