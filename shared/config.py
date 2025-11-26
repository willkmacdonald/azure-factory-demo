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


def _strip_quotes(value: Optional[str]) -> Optional[str]:
    """Strip surrounding quotes from a value if present.

    This handles cases where secrets are stored with literal quotes,
    which can happen when values are copied with quotes included.

    Args:
        value: The value to strip quotes from

    Returns:
        Value with surrounding quotes removed, or None if input is None
    """
    if value is None:
        return None
    # Strip surrounding double or single quotes
    if len(value) >= 2:
        if (value.startswith('"') and value.endswith('"')) or \
           (value.startswith("'") and value.endswith("'")):
            return value[1:-1]
    return value


def get_secret(secret_name: str, default: Optional[str] = None) -> Optional[str]:
    """
    Retrieve a secret from Azure Key Vault with fallback to environment variables.

    Args:
        secret_name: Name of the secret in Key Vault (must use hyphens, not underscores)
        default: Default value if secret not found in Key Vault or environment

    Returns:
        Secret value from Key Vault, environment variable, or default if not found

    Note:
        Azure Key Vault secret names use hyphens instead of underscores.
        Example: AZURE_API_KEY becomes AZURE-API-KEY in Key Vault.
        The corresponding environment variable uses underscores: AZURE_API_KEY.
    """
    value: Optional[str] = None

    # Try Key Vault first
    if _kv_client is not None:
        try:
            secret = _kv_client.get_secret(secret_name)
            value = secret.value
            logger.debug(f"Successfully retrieved secret from Key Vault: {secret_name}")
        except AzureError as e:
            logger.warning(f"Failed to retrieve secret '{secret_name}' from Key Vault: {e}")
        except Exception as e:
            logger.error(f"Unexpected error retrieving secret '{secret_name}': {e}")

    # Fall back to environment variable if Key Vault didn't return a value
    if value is None:
        # Convert hyphenated Key Vault name to underscored env var name
        env_name = secret_name.replace("-", "_")
        value = os.getenv(env_name)
        if value is not None:
            logger.debug(f"Retrieved '{secret_name}' from environment variable {env_name}")
        else:
            logger.debug(f"Secret '{secret_name}' not found in Key Vault or environment")

    # Strip any surrounding quotes and return
    return _strip_quotes(value) if value is not None else default


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
# Stricter rate limit for anonymous/demo access (cost protection)
RATE_LIMIT_SETUP_ANONYMOUS: str = os.getenv("RATE_LIMIT_SETUP_ANONYMOUS", "1/hour")

# Environment settings
DEBUG: bool = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")

# Storage settings
STORAGE_MODE: str = os.getenv("STORAGE_MODE", "azure")  # "local" or "azure"

# Warn if using local storage mode (intended for debugging only)
if STORAGE_MODE.lower() == "local":
    logger.warning(
        "Using LOCAL storage mode. This is intended for debugging only. "
        "Production deployments should use STORAGE_MODE='azure'."
    )
AZURE_STORAGE_CONNECTION_STRING: Optional[str] = get_secret("AZURE-STORAGE-CONNECTION-STRING")
AZURE_BLOB_CONTAINER: str = os.getenv("AZURE_BLOB_CONTAINER", "factory-data")
AZURE_BLOB_NAME: str = os.getenv("AZURE_BLOB_NAME", "production.json")

# Azure Blob Storage retry and timeout settings
AZURE_BLOB_RETRY_TOTAL: int = int(os.getenv("AZURE_BLOB_RETRY_TOTAL", "3"))
AZURE_BLOB_INITIAL_BACKOFF: int = int(os.getenv("AZURE_BLOB_INITIAL_BACKOFF", "2"))
AZURE_BLOB_INCREMENT_BASE: int = int(os.getenv("AZURE_BLOB_INCREMENT_BASE", "2"))
AZURE_BLOB_CONNECTION_TIMEOUT: int = int(os.getenv("AZURE_BLOB_CONNECTION_TIMEOUT", "30"))
AZURE_BLOB_OPERATION_TIMEOUT: int = int(os.getenv("AZURE_BLOB_OPERATION_TIMEOUT", "60"))

# Upload size limit (bytes) - default 50MB for demo data
# This prevents DoS attacks via large payload uploads
AZURE_BLOB_MAX_UPLOAD_SIZE: int = int(os.getenv("AZURE_BLOB_MAX_UPLOAD_SIZE", str(50 * 1024 * 1024)))

# Cost estimation settings
DEFECT_COST_ESTIMATE: float = 50.0  # USD per defect (for demo cost impact calculations)

# Memory storage settings (PR25)
# Uses existing AZURE_BLOB_CONTAINER, just different blob name
MEMORY_BLOB_NAME: str = os.getenv("MEMORY_BLOB_NAME", "memory.json")
