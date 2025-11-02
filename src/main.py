"""
Factory Operations Chatbot - CLI Interface

This module provides the main CLI interface for the factory operations chatbot.
It handles user interaction, Claude API integration, and tool execution.
"""

from datetime import datetime
from typing import Any, Dict, List, Tuple
import json
import os
import tempfile
import wave
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from openai import AzureOpenAI, OpenAI
from openai.types.audio import Transcription

from shared.config import (
    AZURE_ENDPOINT,
    AZURE_API_KEY,
    AZURE_DEPLOYMENT_NAME,
    FACTORY_NAME,
    RECORDING_DURATION,
    WHISPER_MODEL,
    TTS_MODEL,
    TTS_VOICE,
)
from shared.data import initialize_data, data_exists, load_data, MACHINES
from shared.chat_service import build_system_prompt, get_chat_response

# Initialize CLI app and console
app = typer.Typer(help="Factory Operations Chatbot - Demo Application")
console = Console()


# Audio utility functions for voice interface
def _record_audio(duration: int = 5) -> Path:
    """Record audio from microphone (16kHz mono for Whisper). Returns temp WAV file."""
    try:
        import pyaudio
    except ImportError as e:
        raise ImportError(
            "PyAudio not installed. Install with:\n"
            "  macOS: brew install portaudio && pip install pyaudio\n"
            "  Linux: sudo apt install portaudio19-dev && pip install pyaudio\n"
            "  Windows: pip install pyaudio"
        ) from e

    # Configure audio recording (16kHz mono, 16-bit PCM for Whisper)
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000

    audio = None
    stream = None
    try:
        audio = pyaudio.PyAudio()
        stream = audio.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK,
        )

        # Record audio in chunks
        frames = []
        for _ in range(0, int(RATE / CHUNK * duration)):
            data = stream.read(CHUNK)
            frames.append(data)

    except OSError as e:
        raise RuntimeError(
            f"Microphone access failed. Check:\n"
            f"  1. Microphone is connected\n"
            f"  2. Permissions granted\n"
            f"  3. Not in use by another app\n"
            f"Error: {e}"
        ) from e
    finally:
        # Always clean up PyAudio resources
        if stream is not None:
            stream.stop_stream()
            stream.close()
        if audio is not None:
            audio.terminate()

    # Write to temporary WAV file
    temp_file = Path(tempfile.mktemp(suffix=".wav"))
    try:
        with wave.open(str(temp_file), "wb") as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(audio.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b"".join(frames))
    except OSError as e:
        raise OSError(f"Failed to write audio file: {e}") from e

    return temp_file


def _play_audio(audio_file: Path) -> None:
    """Play audio file using pygame. Blocks until playback completes."""
    try:
        import pygame
    except ImportError as e:
        raise ImportError(
            "pygame not installed. Install with:\n" "  pip install pygame"
        ) from e

    if not audio_file.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_file}")

    try:
        # Initialize pygame mixer if not already initialized
        if not pygame.mixer.get_init():
            pygame.mixer.init()

        # Load and play audio file
        pygame.mixer.music.load(str(audio_file))
        pygame.mixer.music.play()

        # Block until playback completes
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

    except Exception as e:
        raise RuntimeError(
            f"Audio playback failed. Check:\n"
            f"  1. Audio format supported\n"
            f"  2. ffmpeg installed (for non-WAV)\n"
            f"  3. Audio device available\n"
            f"Error: {e}"
        ) from e


# Note: Chat functions (_build_system_prompt, _get_chat_response, execute_tool, TOOLS)
# have been moved to backend/src/services/chat_service.py for code reuse between CLI and API


@app.command()
def setup() -> None:
    """Initialize database with synthetic data."""
    console.print(Panel.fit("🏭 Factory Operations Data Generation", style="bold blue"))

    initialize_data(days=30)

    console.print("\n✅ Setup complete! Run 'chat' to start.\n", style="bold green")


@app.command()
def chat() -> None:
    """Start interactive factory operations chatbot."""

    # Validate Azure credentials
    if not AZURE_API_KEY or not AZURE_ENDPOINT:
        console.print(
            "❌ Azure API key or endpoint not set. Please configure your .env file.",
            style="bold red",
        )
        raise typer.Exit(1)

    # Check if data exists
    if not data_exists():
        console.print("❌ Data not found. Please run 'setup' first.", style="bold red")
        raise typer.Exit(1)

    # Build system prompt and get date range for display
    system_prompt = build_system_prompt()
    data = load_data()
    if not data:
        console.print("❌ Data loading failed.", style="bold red")
        raise typer.Exit(1)
    start_date = data["start_date"].split("T")[0]
    end_date = data["end_date"].split("T")[0]

    # Display welcome panel
    console.print(
        Panel.fit(
            f"🏭 {FACTORY_NAME} Operations Assistant\n\n"
            f"Data range: {start_date} to {end_date}\n"
            "Ask questions about production metrics, quality, downtime, and more.\n"
            "Type 'exit' or 'quit' to end.",
            style="bold blue",
        )
    )

    # Initialize Azure OpenAI client
    client: AzureOpenAI = AzureOpenAI(
        azure_endpoint=AZURE_ENDPOINT,
        api_key=AZURE_API_KEY,
        api_version="2024-08-01-preview",  # Use latest API version
    )

    # Conversation history
    conversation_history: List[Dict[str, Any]] = []

    # Main chat loop
    while True:
        # Get user input
        try:
            question = console.input("\n[bold green]You:[/bold green] ")
        except (KeyboardInterrupt, EOFError):
            break

        # Check for exit commands
        if question.lower().strip() in ["exit", "quit", "q"]:
            break

        # Skip empty input
        if not question.strip():
            continue

        try:
            # Get response using shared chat logic
            with console.status("[bold blue]Thinking...", spinner="dots"):
                response_text, new_history = get_chat_response(
                    client, system_prompt, conversation_history, question
                )

            # Display assistant response
            console.print(f"\n[bold blue]Assistant:[/bold blue] {response_text}")

            # Update conversation history with all new messages (includes tool calls)
            conversation_history.extend(new_history)

        except Exception as e:
            console.print(f"\n[bold red]Error:[/bold red] {str(e)}")

    console.print("\n👋 Goodbye!\n", style="bold blue")


@app.command()
def voice() -> None:
    """Start voice chat with factory assistant.

    Uses OpenAI Whisper for speech-to-text and TTS for text-to-speech.
    Press Enter to record 5 seconds of audio, then get spoken response.
    """
    if not AZURE_API_KEY or not AZURE_ENDPOINT:
        console.print("❌ Azure API key or endpoint not set", style="bold red")
        raise typer.Exit(1)

    if not data_exists():
        console.print("❌ Data not found. Please run 'setup' first.", style="bold red")
        raise typer.Exit(1)

    # Check for OpenAI API key (needed for Whisper/TTS)
    openai_key: str | None = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        console.print(
            "❌ OPENAI_API_KEY not set (needed for Whisper/TTS)", style="bold red"
        )
        raise typer.Exit(1)

    # Initialize clients
    azure_client: AzureOpenAI = AzureOpenAI(
        azure_endpoint=AZURE_ENDPOINT,
        api_key=AZURE_API_KEY,
        api_version="2024-08-01-preview",
    )
    openai_client: OpenAI = OpenAI(api_key=openai_key)  # For Whisper/TTS

    # Build system prompt
    system_prompt: str = build_system_prompt()
    conversation_history: List[Dict[str, Any]] = []

    # Welcome message
    console.print(
        Panel.fit(
            "[bold blue]🎤 Voice Chat Mode[/bold blue]\n\n"
            "Press Enter to record (5 seconds)\n"
            "Type 'exit' to quit",
            border_style="blue",
        )
    )

    # Voice chat loop
    while True:
        try:
            # Wait for Enter or exit command
            user_input: str = input(
                "\n[Press Enter to record, or type 'exit']: "
            ).strip()

            if user_input.lower() in ["exit", "quit"]:
                console.print("\n👋 Goodbye!", style="bold blue")
                break

            # Record audio
            console.print("🎤 Recording... (5 seconds)", style="yellow")
            audio_file: Path = _record_audio(duration=RECORDING_DURATION)

            # Transcribe with Whisper
            with console.status("⏳ Transcribing..."):
                with open(audio_file, "rb") as f:
                    transcript: Transcription = (
                        openai_client.audio.transcriptions.create(
                            model=WHISPER_MODEL, file=f
                        )
                    )
                transcribed_text: str = transcript.text

            console.print(f"[bold green]You said:[/bold green] {transcribed_text}")

            # Get Claude response using shared logic
            with console.status("⏳ Assistant is thinking..."):
                response_text: str
                new_history: List[Dict[str, Any]]
                response_text, new_history = get_chat_response(
                    azure_client,
                    system_prompt,
                    conversation_history,
                    transcribed_text,
                )

            # Display text response
            console.print(f"\n[bold blue]Assistant:[/bold blue] {response_text}")

            # Generate speech with TTS
            with console.status("🔊 Generating speech..."):
                tts_file: Path = Path(tempfile.mktemp(suffix=".mp3"))
                tts_response = openai_client.audio.speech.create(
                    model=TTS_MODEL, voice=TTS_VOICE, input=response_text
                )
                tts_response.stream_to_file(tts_file)

            # Play audio
            _play_audio(tts_file)

            # Update conversation history with all new messages
            conversation_history.extend(new_history)

            # Cleanup temp files
            audio_file.unlink()
            tts_file.unlink()

        except KeyboardInterrupt:
            console.print("\n\n👋 Goodbye!", style="bold blue")
            break
        except Exception as e:
            console.print(f"\n❌ Error: {e}", style="bold red")


@app.command()
def stats() -> None:
    """Show data statistics."""
    if not data_exists():
        console.print("❌ Data not found. Please run 'setup' first.", style="bold red")
        raise typer.Exit(1)

    data = load_data()
    if not data:
        console.print("❌ Data loading failed.", style="bold red")
        raise typer.Exit(1)

    # Create statistics table
    table = Table(title=f"📊 {FACTORY_NAME} Data")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="magenta")

    table.add_row(
        "Date Range",
        f"{data['start_date'].split('T')[0]} to {data['end_date'].split('T')[0]}",
    )
    table.add_row("Days", str(len(data["production"])))
    table.add_row("Machines", str(len(data["machines"])))
    table.add_row("Shifts", str(len(data["shifts"])))

    console.print(table)
    console.print()


if __name__ == "__main__":
    app()
