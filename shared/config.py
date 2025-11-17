"""Configuration settings for the factory operations chatbot."""

import os
from typing import Optional, List
from dotenv import load_dotenv

load_dotenv()

# Azure AI Foundry settings
AZURE_ENDPOINT: Optional[str] = os.getenv("AZURE_ENDPOINT")
AZURE_API_KEY: Optional[str] = os.getenv("AZURE_API_KEY")
AZURE_DEPLOYMENT_NAME: str = os.getenv("AZURE_DEPLOYMENT_NAME", "gpt-4")
AZURE_API_VERSION: str = os.getenv("AZURE_API_VERSION", "2024-08-01-preview")
FACTORY_NAME: str = os.getenv("FACTORY_NAME", "Demo Factory")
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
AZURE_STORAGE_CONNECTION_STRING: Optional[str] = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
AZURE_BLOB_CONTAINER: str = os.getenv("AZURE_BLOB_CONTAINER", "factory-data")
AZURE_BLOB_NAME: str = os.getenv("AZURE_BLOB_NAME", "production.json")

# Cost estimation settings
DEFECT_COST_ESTIMATE: float = 50.0  # USD per defect (for demo cost impact calculations)
