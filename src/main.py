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

from .config import (
    AZURE_ENDPOINT,
    AZURE_API_KEY,
    AZURE_DEPLOYMENT_NAME,
    FACTORY_NAME,
    RECORDING_DURATION,
    WHISPER_MODEL,
    TTS_MODEL,
    TTS_VOICE,
)
from .data import initialize_data, data_exists, load_data, MACHINES
from .metrics import (
    calculate_oee,
    get_scrap_metrics,
    get_quality_issues,
    get_downtime_analysis,
)

# Initialize CLI app and console
app = typer.Typer(help="Factory Operations Chatbot - Demo Application")
console = Console()


# Audio utility functions for voice interface
def _record_audio(duration: int = 5) -> Path:
    """Record audio from microphone and save to temporary WAV file.

    Captures audio in 16kHz mono format optimized for OpenAI Whisper API.
    Uses PyAudio for cross-platform recording. Caller must delete returned file.

    Code Flow:
    1. Initialize PyAudio and configure recording parameters (16kHz, mono, 16-bit)
    2. Open audio input stream and record in 1024-frame chunks
    3. Clean up PyAudio resources (guaranteed via finally block)
    4. Write audio data to temporary WAV file and return path

    Args:
        duration: Recording duration in seconds (default: 5)

    Returns:
        Path to temporary WAV file (16kHz, mono, 16-bit PCM)
        Caller must delete file after use with audio_file.unlink()

    Raises:
        ImportError: If PyAudio not installed (see INSTALL.md)
        RuntimeError: If microphone access fails or not available
        OSError: If temporary file cannot be created
    """
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
    """Play audio file through system speakers.

    Uses pygame.mixer for reliable cross-platform audio playback.
    Supports MP3, WAV, OGG formats. Blocks until playback completes.

    Code Flow:
    1. Verify audio file exists
    2. Initialize pygame mixer if not already initialized
    3. Load and play audio file
    4. Block until playback completes

    Args:
        audio_file: Path to audio file (MP3, WAV, OGG, etc.)

    Returns:
        None (blocks until playback finishes)

    Raises:
        ImportError: If pygame not installed
        FileNotFoundError: If audio_file does not exist
        RuntimeError: If playback fails or format unsupported
    """
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


# Shared chat logic for text and voice interfaces
def _build_system_prompt() -> str:
    """Build system prompt with factory context and tool definitions.

    Loads production data and constructs a complete system prompt for Claude
    with date range, available machines, and instructions for answering questions.

    Code Flow:
    1. Load production data from JSON via load_data()
    2. Extract start_date and end_date, strip time component (keep YYYY-MM-DD)
    3. Build comma-separated list of machine names from MACHINES constant
    4. Construct system prompt with:
       - Factory name and assistant role
       - Available data range (30 days)
       - Machine and shift information
       - Instructions for tool usage and response formatting
       - Current date context for relative date queries

    Returns:
        Complete system prompt string with factory context and guidelines
    """
    data = load_data()
    start_date = data["start_date"].split("T")[0]
    end_date = data["end_date"].split("T")[0]
    machines = ", ".join([m["name"] for m in MACHINES])

    return f"""You are a factory operations assistant for {FACTORY_NAME}.

You have access to 30 days of production data ({start_date} to {end_date}) covering:
- 4 machines: {machines}
- 2 shifts: Day (6am-2pm) and Night (2pm-10pm)
- Metrics: OEE, scrap, quality issues, downtime

When answering:
1. Use tools to get accurate data
2. Provide specific numbers and percentages
3. Explain trends and patterns
4. Compare metrics when relevant
5. Be concise but thorough

Today's date is {datetime.now().strftime('%Y-%m-%d')}. When users ask about \
"today", "this week", or relative dates, calculate the appropriate date range \
based on the data available."""


def _get_chat_response(
    client: AzureOpenAI,
    system_prompt: str,
    conversation_history: List[Dict[str, Any]],
    user_message: str,
) -> Tuple[str, List[Dict[str, Any]]]:
    """Get Azure OpenAI response with tool calling support.

    Manages the complete tool-calling loop: sends message to Azure OpenAI, executes
    any requested tools, and returns final text response. Handles multiple
    tool call iterations automatically.

    Code Flow:
    1. Build messages list: system prompt + conversation history + new user message
    2. Enter tool-calling loop:
       a. Send messages to Azure OpenAI API with tool definitions
       b. If model returns tool calls (not final answer):
          - Append assistant message with tool_calls to messages
          - Execute each requested tool via execute_tool()
          - Append tool results to messages
          - Loop back to step 2a with updated messages
       c. If model returns text (no tool calls):
          - Extract final assistant response
          - Build updated history with all new messages (user + tool calls + assistant)
          - Return response text and updated history
    3. Caller must update their conversation_history with returned history

    Args:
        client: AzureOpenAI client configured for Azure AI Foundry
        system_prompt: System prompt with factory context
        conversation_history: List of previous conversation messages
        user_message: Current user message to process

    Returns:
        Tuple of (response_text, updated_history):
        - response_text: Final assistant response text after all tool calls complete
        - updated_history: New messages to append (user msg, tool calls, assistant msg)
    """
    # Build messages list with system prompt, history, and new message
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(conversation_history)
    messages.append({"role": "user", "content": user_message})

    # Track where new messages start (after existing history)
    history_start_index = len(messages) - 1  # Index of new user message

    # Tool calling loop - continues until Claude provides final answer
    while True:
        response = client.chat.completions.create(
            model=AZURE_DEPLOYMENT_NAME, messages=messages, tools=TOOLS, tool_choice="auto"
        )

        message = response.choices[0].message

        # If no tool calls, we have the final answer
        if not message.tool_calls:
            # Extract new messages added during this conversation turn
            new_history = messages[history_start_index:]
            # Add final assistant response
            new_history.append({"role": "assistant", "content": message.content})
            return message.content, new_history

        # Add assistant message with tool calls to history
        messages.append(message.model_dump())

        # Execute each requested tool
        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)

            # Execute tool and get result
            result = execute_tool(tool_name, tool_args)

            # Add tool result to messages
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_name,
                    "content": json.dumps(result),
                }
            )


# Tool definitions for Claude
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "calculate_oee",
            "description": (
                "Calculate Overall Equipment Effectiveness (OEE) for a "
                "date range. Returns OEE percentage and breakdown."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": "Start date (YYYY-MM-DD)",
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date (YYYY-MM-DD)",
                    },
                    "machine_name": {
                        "type": "string",
                        "description": "Optional machine name filter",
                    },
                },
                "required": ["start_date", "end_date"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_scrap_metrics",
            "description": (
                "Get scrap production metrics including total scrap, "
                "scrap rate, and breakdown by machine."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": "Start date (YYYY-MM-DD)",
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date (YYYY-MM-DD)",
                    },
                    "machine_name": {
                        "type": "string",
                        "description": "Optional machine name filter",
                    },
                },
                "required": ["start_date", "end_date"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_quality_issues",
            "description": (
                "Get quality defect events with details about defect types, "
                "severity, and affected parts."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": "Start date (YYYY-MM-DD)",
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date (YYYY-MM-DD)",
                    },
                    "severity": {
                        "type": "string",
                        "description": "Optional severity filter: Low, Medium, or High",
                    },
                    "machine_name": {
                        "type": "string",
                        "description": "Optional machine name filter",
                    },
                },
                "required": ["start_date", "end_date"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_downtime_analysis",
            "description": (
                "Analyze downtime events including reasons, duration, "
                "and major incidents."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": "Start date (YYYY-MM-DD)",
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date (YYYY-MM-DD)",
                    },
                    "machine_name": {
                        "type": "string",
                        "description": "Optional machine name filter",
                    },
                },
                "required": ["start_date", "end_date"],
            },
        },
    },
]


def execute_tool(tool_name: str, tool_args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a tool function and return results.

    Maps tool names to their corresponding metric functions and executes them
    with the provided arguments.

    Args:
        tool_name: Name of the tool to execute
        tool_args: Dictionary of arguments to pass to the tool

    Returns:
        Dictionary containing tool execution results or error message
    """
    if tool_name == "calculate_oee":
        return calculate_oee(**tool_args)
    elif tool_name == "get_scrap_metrics":
        return get_scrap_metrics(**tool_args)
    elif tool_name == "get_quality_issues":
        return get_quality_issues(**tool_args)
    elif tool_name == "get_downtime_analysis":
        return get_downtime_analysis(**tool_args)
    else:
        return {"error": f"Unknown tool: {tool_name}"}


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
    system_prompt = _build_system_prompt()
    data = load_data()
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
        api_version="2024-08-01-preview"  # Use latest API version
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
                response_text, new_history = _get_chat_response(
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
        api_version="2024-08-01-preview"
    )
    openai_client: OpenAI = OpenAI(api_key=openai_key)  # For Whisper/TTS

    # Build system prompt
    system_prompt: str = _build_system_prompt()
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
                response_text, new_history = _get_chat_response(
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
