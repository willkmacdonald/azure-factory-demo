"""Configuration settings for the factory operations chatbot."""

import os
import logging
from typing import Optional, List
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from azure.core.exceptions import AzureError

load_dotenv()

logger = logging.getLogger(__name__)

# Azure Key Vault Configuration
KEYVAULT_URL: Optional[str] = os.getenv("KEYVAULT_URL")

# Initialize Key Vault client if URL is provided
_kv_client: Optional[SecretClient] = None
if KEYVAULT_URL:
    try:
        credential = DefaultAzureCredential()
        _kv_client = SecretClient(vault_url=KEYVAULT_URL, credential=credential)
        logger.info(f"Azure Key Vault client initialized: {KEYVAULT_URL}")
    except Exception as e:
        logger.warning(f"Failed to initialize Key Vault client: {e}")
        _kv_client = None


def get_secret(secret_name: str, default: Optional[str] = None) -> Optional[str]:
    """
    Retrieve a secret from Azure Key Vault.

    Args:
        secret_name: Name of the secret in Key Vault (must use hyphens, not underscores)
        default: Default value if secret not found

    Returns:
        Secret value from Key Vault, or default if not found

    Note:
        Azure Key Vault secret names use hyphens instead of underscores.
        Example: AZURE_API_KEY becomes AZURE-API-KEY in Key Vault.
    """
    if _kv_client is None:
        logger.debug(f"Key Vault not configured, cannot retrieve secret: {secret_name}")
        return default

    try:
        secret = _kv_client.get_secret(secret_name)
        logger.debug(f"Successfully retrieved secret from Key Vault: {secret_name}")
        return secret.value
    except AzureError as e:
        logger.warning(f"Failed to retrieve secret '{secret_name}' from Key Vault: {e}")
        return default
    except Exception as e:
        logger.error(f"Unexpected error retrieving secret '{secret_name}': {e}")
        return default


# Azure AI Foundry settings
AZURE_ENDPOINT: Optional[str] = get_secret("AZURE-ENDPOINT")
AZURE_API_KEY: Optional[str] = get_secret("AZURE-API-KEY")
AZURE_DEPLOYMENT_NAME: str = get_secret("AZURE-DEPLOYMENT-NAME") or "gpt-4"
AZURE_API_VERSION: str = get_secret("AZURE-API-VERSION") or "2024-08-01-preview"
FACTORY_NAME: str = get_secret("FACTORY-NAME") or "Demo Factory"
DATA_FILE: str = os.getenv("DATA_FILE", "./data/production.json")

# Voice interface settings
TTS_VOICE: str = "alloy"  # OpenAI voice: alloy, echo, fable, onyx, nova, shimmer
TTS_MODEL: str = "tts-1"  # or "tts-1-hd" for higher quality
WHISPER_MODEL: str = "whisper-1"
RECORDING_DURATION: int = 5  # seconds

# API Security settings
ALLOWED_ORIGINS: List[str] = [
    origin.strip()
    for origin in os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:3000,http://localhost:5173,http://localhost:5174"
    ).split(",")
]
RATE_LIMIT_CHAT: str = os.getenv("RATE_LIMIT_CHAT", "10/minute")
RATE_LIMIT_SETUP: str = os.getenv("RATE_LIMIT_SETUP", "5/minute")

# Environment settings
DEBUG: bool = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")

# Storage settings
STORAGE_MODE: str = os.getenv("STORAGE_MODE", "local")  # "local" or "azure"
AZURE_STORAGE_CONNECTION_STRING: Optional[str] = get_secret("AZURE-STORAGE-CONNECTION-STRING")
AZURE_BLOB_CONTAINER: str = os.getenv("AZURE_BLOB_CONTAINER", "factory-data")
AZURE_BLOB_NAME: str = os.getenv("AZURE_BLOB_NAME", "production.json")

# Azure Blob Storage retry and timeout settings
AZURE_BLOB_RETRY_TOTAL: int = int(os.getenv("AZURE_BLOB_RETRY_TOTAL", "3"))
AZURE_BLOB_INITIAL_BACKOFF: int = int(os.getenv("AZURE_BLOB_INITIAL_BACKOFF", "2"))
AZURE_BLOB_INCREMENT_BASE: int = int(os.getenv("AZURE_BLOB_INCREMENT_BASE", "2"))
AZURE_BLOB_CONNECTION_TIMEOUT: int = int(os.getenv("AZURE_BLOB_CONNECTION_TIMEOUT", "30"))
AZURE_BLOB_OPERATION_TIMEOUT: int = int(os.getenv("AZURE_BLOB_OPERATION_TIMEOUT", "60"))

# Cost estimation settings
DEFECT_COST_ESTIMATE: float = 50.0  # USD per defect (for demo cost impact calculations)
