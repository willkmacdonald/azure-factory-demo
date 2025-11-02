"""Configuration settings for the factory operations chatbot."""

import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# Azure AI Foundry settings
AZURE_ENDPOINT: Optional[str] = os.getenv("AZURE_ENDPOINT")
AZURE_API_KEY: Optional[str] = os.getenv("AZURE_API_KEY")
AZURE_DEPLOYMENT_NAME: str = os.getenv("AZURE_DEPLOYMENT_NAME", "gpt-4")
FACTORY_NAME: str = os.getenv("FACTORY_NAME", "Demo Factory")
DATA_FILE: str = os.getenv("DATA_FILE", "./data/production.json")

# Voice interface settings
TTS_VOICE: str = "alloy"  # OpenAI voice: alloy, echo, fable, onyx, nova, shimmer
TTS_MODEL: str = "tts-1"  # or "tts-1-hd" for higher quality
WHISPER_MODEL: str = "whisper-1"
RECORDING_DURATION: int = 5  # seconds
