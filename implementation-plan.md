# Azure Migration Implementation Plan
## Factory Agent: Streamlit/CLI → React + Azure Container Apps

**Version:** 2.0
**Created:** 2025-01-01
**Target Timeline:** 4-5 weeks
**Architecture:** Azure Container Apps + FastAPI + React

---

## 🎯 Migration Goals

Transform the factory operations chatbot from a local Streamlit/CLI application to a cloud-native web application deployed on Azure with:

- **React split-pane interface**: Dashboard (left) + Chat Console (right)
- **FastAPI backend**: RESTful API with WebSocket support
- **Azure Container Apps**: Serverless container hosting
- **Azure AD authentication**: Microsoft account login
- **Voice interface**: Browser-based recording with OpenAI Whisper/TTS
- **Full Azure deployment**: Container Apps, Blob Storage, Container Registry

---

## 🏗️ Architecture Overview

### Current Architecture
```
┌─────────────────────────────────────────────┐
│  Streamlit Dashboard (Port 8501)            │
│  - OEE gauges, charts, tables               │
│  - Sidebar filters                          │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│  Typer CLI (Terminal)                       │
│  - python -m src.main chat                  │
│  - python -m src.main voice                 │
│  - Rich console output                      │
└─────────────────────────────────────────────┘

        ↓ Both use same metrics layer

┌─────────────────────────────────────────────┐
│  Python Backend (Local)                     │
│  - metrics.py: 4 analysis functions         │
│  - data.py: JSON file storage               │
│  - Azure OpenAI client                      │
└─────────────────────────────────────────────┘
```

### Target Architecture
```
┌──────────────────────────────────────────────────────────┐
│  React Frontend (Azure Container Apps)                   │
│                                                           │
│  ┌─────────────────────┐  ┌──────────────────────────┐  │
│  │  Dashboard Panel    │  │  Console Panel           │  │
│  │  (Left Pane)        │  │  (Right Pane)            │  │
│  │                     │  │                          │  │
│  │  - OEE Gauge        │  │  - Chat History          │  │
│  │  - Trend Charts     │  │  - Message Input         │  │
│  │  - Downtime Table   │  │  - Voice Recorder        │  │
│  │  - Quality Table    │  │  - Audio Playback        │  │
│  │  - Machine Filter   │  │  - Typing Indicator      │  │
│  │                     │  │                          │  │
│  └─────────────────────┘  └──────────────────────────┘  │
│                                                           │
│  Uses: Material-UI, Recharts, react-split-pane          │
└──────────────────────────────────────────────────────────┘
                            ↓
                    HTTPS + Azure AD Auth
                            ↓
┌──────────────────────────────────────────────────────────┐
│  FastAPI Backend (Azure Container Apps)                  │
│                                                           │
│  REST Endpoints:                                         │
│  - GET  /api/metrics/oee                                 │
│  - GET  /api/metrics/scrap                               │
│  - GET  /api/metrics/quality                             │
│  - GET  /api/metrics/downtime                            │
│  - GET  /api/machines                                    │
│  - GET  /api/stats                                       │
│  - POST /api/setup                                       │
│                                                           │
│  Chat & Voice:                                           │
│  - POST /api/chat                                        │
│  - WS   /ws/chat (WebSocket for streaming)              │
│  - POST /api/voice/transcribe                            │
│  - POST /api/voice/synthesize                            │
│                                                           │
│  Reused Code:                                            │
│  - metrics.py (unchanged)                                │
│  - models.py (unchanged)                                 │
│  - data.py (updated for Blob Storage)                    │
│  - config.py (updated for Azure)                         │
└──────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────┐
│  Azure Services                                          │
│                                                           │
│  - Azure Blob Storage: production.json data              │
│  - Azure Container Registry: Docker images               │
│  - Azure AD (Entra ID): Authentication                   │
│  - Azure OpenAI: GPT-4 chat, Whisper (speech-to-text),  │
│                  TTS (text-to-speech)                    │
│  - Application Insights: Monitoring (optional)           │
└──────────────────────────────────────────────────────────┘
```

---

## 📋 Implementation Phases

### Phase 1: Backend API with FastAPI (Week 1-2)

**Goal:** Create REST API that reuses existing Python business logic

#### Tasks

**1.1 Project Structure Setup**
- Create `backend/` directory
- Set up Python package structure with `src/api/`
- Copy existing modules: `metrics.py`, `models.py`, `data.py`, `config.py`
- Create `requirements.txt` with FastAPI dependencies

**1.2 FastAPI Application Core**
- Create `backend/src/api/main.py` with FastAPI app
- Configure CORS for local React development
- Add health check endpoint: `GET /health`
- Set up environment variable loading

**1.3 Metrics Endpoints**
- Create `backend/src/api/routes/metrics.py`
- Implement endpoints:
  ```python
  GET /api/metrics/oee?start_date=X&end_date=Y&machine=Z
  GET /api/metrics/scrap?start_date=X&end_date=Y&machine=Z
  GET /api/metrics/quality?start_date=X&end_date=Y&severity=X&machine=Z
  GET /api/metrics/downtime?start_date=X&end_date=Y&machine=Z
  ```
- Use existing `metrics.py` functions directly (no changes needed)
- Return Pydantic models as JSON (automatic serialization)

**1.4 Data Management Endpoints**
- Create `backend/src/api/routes/data.py`
- Implement:
  ```python
  POST /api/setup          # Generate synthetic data
  GET  /api/stats          # Get data statistics
  GET  /api/machines       # List available machines
  GET  /api/date-range     # Get available data dates
  ```

**1.5 Chat Service Layer (Shared Logic)**
- Create `backend/src/services/chat_service.py`
- Extract from `src/main.py`:
  ```python
  # Move these functions to chat_service.py:
  def get_chat_response(client, system_prompt, history, user_message):
      """Renamed from _get_chat_response, identical logic"""
      # ... existing tool-calling loop ...

  def execute_tool(tool_name, tool_args):
      """Moved as-is from main.py"""
      # ... existing tool execution ...

  TOOLS = [...]  # Moved as-is from main.py
  ```
- This preserves all existing logic while making it reusable

**1.6 Chat Endpoint**
- Create `backend/src/api/routes/chat.py`
- Implement `POST /api/chat` endpoint using `chat_service`:
  ```python
  from services.chat_service import get_chat_response

  @router.post("/api/chat")
  async def chat(request: ChatRequest):
      response, updated_history = get_chat_response(
          client, system_prompt, request.history, request.message
      )
      return {"response": response, "history": updated_history}
  ```

**1.7 Test Migration**
- Rename `tests/test_main.py` → `tests/test_chat_service.py`
- Update imports:
  ```python
  # OLD: from src.main import _get_chat_response, execute_tool
  # NEW: from src.services.chat_service import get_chat_response, execute_tool
  ```
- All test logic stays identical (just import changes)
- Add new `tests/test_api.py` for endpoint testing

**1.8 Local Testing**
- Run with: `uvicorn src.api.main:app --reload`
- Test all endpoints with Postman or curl
- Verify metrics calculations match existing CLI/Streamlit output
- Run pytest: All migrated tests should pass

**Deliverables:**
- ✅ Working FastAPI application running locally
- ✅ All metrics endpoints functional
- ✅ Basic chat endpoint working
- ✅ Pytest tests passing
- ✅ API documentation auto-generated at `/docs`

---

### Phase 2: Azure Blob Storage Integration (Week 2)

**Goal:** Migrate from local JSON file to Azure Blob Storage

#### Tasks

**2.1 Azure Storage Account Setup**
- Create Azure Storage Account in portal
- Create blob container: `factory-data`
- Get connection string from Azure Portal
- Add `AZURE_STORAGE_CONNECTION_STRING` to `.env`

**2.2 Update data.py for Blob Storage**
- Install: `azure-storage-blob`
- Modify `save_data()` to write to blob:
  ```python
  from azure.storage.blob import BlobServiceClient

  def save_data(data: Dict[str, Any]) -> None:
      blob_service_client = BlobServiceClient.from_connection_string(conn_str)
      blob_client = blob_service_client.get_blob_client(
          container="factory-data",
          blob="production.json"
      )
      blob_client.upload_blob(json.dumps(data), overwrite=True)
  ```
- Modify `load_data()` to read from blob
- Keep local file fallback for development

**2.3 Environment-based Storage**
- Add `STORAGE_MODE` config: `local` or `azure`
- Local dev: Use JSON file
- Azure deployment: Use Blob Storage
- Update `config.py` to handle both modes

**2.4 Testing**
- Test data generation to blob
- Test data loading from blob
- Verify metrics work with blob-based data
- Test fallback to local file in dev mode

**Deliverables:**
- ✅ Data persists in Azure Blob Storage
- ✅ FastAPI reads from blob in Azure mode
- ✅ Local development still works with JSON file
- ✅ Tests updated for both storage modes

---

### Phase 3: React Frontend Development (Week 2-3)

**Goal:** Build beginner-friendly React interface with split-pane layout

#### Tasks

**3.1 React Project Setup**
- Create `frontend/` directory
- Initialize with Vite: `npm create vite@latest . -- --template react-ts`
- Install dependencies:
  ```bash
  npm install @mui/material @emotion/react @emotion/styled
  npm install recharts axios react-split-pane
  npm install @types/react-split-pane --save-dev
  ```

**3.2 Core Layout Components**

**3.2.1 App.tsx (Main Layout)**
```typescript
import React from 'react';
import SplitPane from 'react-split-pane';
import DashboardPanel from './components/DashboardPanel';
import ConsolePanel from './components/ConsolePanel';

function App() {
  // Shared state: selected machine filter
  const [selectedMachine, setSelectedMachine] = useState<string | null>(null);

  return (
    <SplitPane split="vertical" defaultSize="60%">
      <DashboardPanel
        selectedMachine={selectedMachine}
        onMachineChange={setSelectedMachine}
      />
      <ConsolePanel selectedMachine={selectedMachine} />
    </SplitPane>
  );
}
```

**3.2.2 DashboardPanel.tsx (Left Pane Container)**
- Tab navigation: OEE, Availability, Quality
- Machine filter dropdown at top
- Renders child components based on active tab

**3.2.3 ConsolePanel.tsx (Right Pane Container)**
- Chat history display area
- Message input box at bottom
- Voice recorder button
- "Thinking..." indicator

**3.3 Dashboard Components (Left Pane)**

**3.3.1 OEEGauge.tsx**
- Beginner pattern with detailed comments:
```typescript
import React, { useState, useEffect } from 'react';
import { PieChart, Pie, Cell } from 'recharts';
import axios from 'axios';

interface OEEGaugeProps {
  machineId?: string;
  startDate: string;
  endDate: string;
}

export const OEEGauge: React.FC<OEEGaugeProps> = ({
  machineId,
  startDate,
  endDate
}) => {
  // State for OEE data
  const [oee, setOee] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(true);

  // Fetch OEE data when component mounts or params change
  useEffect(() => {
    const fetchOEE = async () => {
      setLoading(true);
      try {
        const params = { start_date: startDate, end_date: endDate };
        if (machineId) params.machine_name = machineId;

        const response = await axios.get('/api/metrics/oee', { params });
        setOee(response.data.oee * 100); // Convert to percentage
      } catch (error) {
        console.error('Failed to fetch OEE:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchOEE();
  }, [machineId, startDate, endDate]); // Re-fetch when these change

  // Gauge chart data (0-100 scale)
  const data = [
    { name: 'OEE', value: oee },
    { name: 'Gap', value: 100 - oee }
  ];

  // Color based on OEE value (red/yellow/green)
  const getColor = (value: number) => {
    if (value >= 75) return '#4caf50'; // Green
    if (value >= 60) return '#ffeb3b'; // Yellow
    return '#f44336'; // Red
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      <h3>Current OEE: {oee.toFixed(1)}%</h3>
      <PieChart width={200} height={200}>
        <Pie
          data={data}
          cx={100}
          cy={100}
          startAngle={180}
          endAngle={0}
          innerRadius={60}
          outerRadius={80}
          dataKey="value"
        >
          <Cell fill={getColor(oee)} />
          <Cell fill="#e0e0e0" />
        </Pie>
      </PieChart>
    </div>
  );
};
```

**3.3.2 TrendChart.tsx**
- Line chart showing daily OEE or scrap rate trends
- Uses Recharts LineChart component
- Fetches daily data for date range
- Similar useState/useEffect pattern

**3.3.3 DowntimeTable.tsx**
- Material-UI Table component
- Displays downtime events with sorting
- Color-coded by duration (>2 hours highlighted)

**3.3.4 QualityTable.tsx**
- Material-UI Table component
- Quality issues with severity badges
- Color coding: Red (High), Yellow (Medium), Green (Low)

**3.4 Console Components (Right Pane)**

**3.4.1 ChatConsole.tsx**
- Container with message list and input
- Manages conversation history state
- Handles send message action

**3.4.2 MessageList.tsx**
```typescript
interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface MessageListProps {
  messages: Message[];
}

export const MessageList: React.FC<MessageListProps> = ({ messages }) => {
  // Auto-scroll to bottom when new message arrives
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div style={{ height: '100%', overflowY: 'auto', padding: '1rem' }}>
      {messages.map((msg, idx) => (
        <MessageItem key={idx} message={msg} />
      ))}
      <div ref={messagesEndRef} />
    </div>
  );
};
```

**3.4.3 ChatInput.tsx**
- Text input with send button
- Enter key to send
- Disabled while waiting for response

**3.4.4 VoiceRecorder.tsx**
- Button to start/stop recording
- Uses browser MediaRecorder API
- Visual feedback during recording
- (Implemented in Phase 4)

**3.5 Services Layer**

**3.5.1 api.ts**
```typescript
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Metrics API
export const getOEE = (params: {
  start_date: string;
  end_date: string;
  machine_name?: string;
}) => api.get('/api/metrics/oee', { params });

export const getScrap = (params: {
  start_date: string;
  end_date: string;
  machine_name?: string;
}) => api.get('/api/metrics/scrap', { params });

// Chat API
export const sendChatMessage = (message: string, history: any[]) =>
  api.post('/api/chat', { message, history });

// ... other endpoints
```

**3.6 Local Development Testing**
- Run backend: `cd backend && uvicorn src.api.main:app --reload`
- Run frontend: `cd frontend && npm run dev`
- Test split-pane resize
- Test all dashboard tabs load data
- Test machine filter updates charts
- Test chat sends messages

**Deliverables:**
- ✅ React app running locally on port 3000
- ✅ Split-pane layout with dashboard + console
- ✅ Dashboard displays OEE gauges, charts, tables
- ✅ Console has message list and input
- ✅ All components fetch data from FastAPI backend
- ✅ Machine filter works across dashboard and chat

---

### Phase 4: Voice Feature Integration (Week 3-4)

**Goal:** Add browser-based voice recording with Azure OpenAI Whisper/TTS

**Note:** Azure OpenAI now supports both Whisper (speech-to-text) and TTS (text-to-speech) models. This keeps everything in the Azure ecosystem without needing separate OpenAI API keys.

#### Tasks

**4.1 Backend Voice Endpoints**

**4.1.1 POST /api/voice/transcribe**
```python
from fastapi import UploadFile, File
from openai import AzureOpenAI
import os
import tempfile

@router.post("/voice/transcribe")
async def transcribe_audio(audio: UploadFile = File(...)):
    """Transcribe audio using Azure OpenAI Whisper."""
    # Use same Azure OpenAI client as chat
    client = AzureOpenAI(
        azure_endpoint=os.getenv("AZURE_ENDPOINT"),
        api_key=os.getenv("AZURE_API_KEY"),
        api_version="2024-08-01-preview"
    )

    # Read audio file
    audio_bytes = await audio.read()

    # Create temporary file (Whisper needs file path)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp:
        temp.write(audio_bytes)
        temp_path = temp.name

    try:
        # Transcribe with Azure OpenAI Whisper
        with open(temp_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model=os.getenv("AZURE_WHISPER_DEPLOYMENT_NAME", "whisper"),
                file=audio_file
            )
        return {"text": transcript.text}
    finally:
        os.unlink(temp_path)
```

**4.1.2 POST /api/voice/synthesize**
```python
from pydantic import BaseModel

class TTSRequest(BaseModel):
    text: str
    voice: str = "alloy"  # alloy, echo, fable, onyx, nova, shimmer

@router.post("/voice/synthesize")
async def synthesize_speech(request: TTSRequest):
    """Generate speech from text using Azure OpenAI TTS."""
    client = AzureOpenAI(
        azure_endpoint=os.getenv("AZURE_ENDPOINT"),
        api_key=os.getenv("AZURE_API_KEY"),
        api_version="2024-08-01-preview"
    )

    response = client.audio.speech.create(
        model=os.getenv("AZURE_TTS_DEPLOYMENT_NAME", "tts"),
        voice=request.voice,
        input=request.text
    )

    # Return audio as streaming response
    return StreamingResponse(
        io.BytesIO(response.content),
        media_type="audio/mpeg"
    )
```

**4.2 Frontend Voice Components**

**4.2.1 VoiceRecorder.tsx**
```typescript
import React, { useState, useRef } from 'react';
import { Button, CircularProgress } from '@mui/material';
import MicIcon from '@mui/icons-material/Mic';
import StopIcon from '@mui/icons-material/Stop';

export const VoiceRecorder: React.FC<{onTranscript: (text: string) => void}> =
({ onTranscript }) => {
  const [recording, setRecording] = useState(false);
  const [processing, setProcessing] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  const startRecording = async () => {
    try {
      // Request microphone access
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

      // Create MediaRecorder
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      // Collect audio data
      mediaRecorder.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      // Handle recording stop
      mediaRecorder.onstop = async () => {
        // Create audio blob
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });

        // Stop all tracks (release microphone)
        stream.getTracks().forEach(track => track.stop());

        // Send to backend for transcription
        await transcribeAudio(audioBlob);
      };

      // Start recording
      mediaRecorder.start();
      setRecording(true);
    } catch (error) {
      console.error('Microphone access failed:', error);
      alert('Please allow microphone access');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && recording) {
      mediaRecorderRef.current.stop();
      setRecording(false);
      setProcessing(true);
    }
  };

  const transcribeAudio = async (audioBlob: Blob) => {
    try {
      const formData = new FormData();
      formData.append('audio', audioBlob, 'recording.wav');

      const response = await axios.post('/api/voice/transcribe', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      onTranscript(response.data.text);
    } catch (error) {
      console.error('Transcription failed:', error);
    } finally {
      setProcessing(false);
    }
  };

  return (
    <Button
      variant="contained"
      color={recording ? "secondary" : "primary"}
      onClick={recording ? stopRecording : startRecording}
      disabled={processing}
      startIcon={recording ? <StopIcon /> : <MicIcon />}
    >
      {processing ? <CircularProgress size={24} /> :
       recording ? 'Stop Recording' : 'Record Voice'}
    </Button>
  );
};
```

**4.2.2 AudioPlayer.tsx**
```typescript
export const AudioPlayer: React.FC<{text: string}> = ({ text }) => {
  const [playing, setPlaying] = useState(false);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  const playAudio = async () => {
    setPlaying(true);
    try {
      // Request TTS from backend
      const response = await axios.post('/api/voice/synthesize',
        { text },
        { responseType: 'blob' }
      );

      // Create audio URL from blob
      const audioBlob = new Blob([response.data], { type: 'audio/mpeg' });
      const audioUrl = URL.createObjectURL(audioBlob);

      // Play audio
      const audio = new Audio(audioUrl);
      audioRef.current = audio;
      audio.onended = () => {
        setPlaying(false);
        URL.revokeObjectURL(audioUrl);
      };
      audio.play();
    } catch (error) {
      console.error('TTS playback failed:', error);
      setPlaying(false);
    }
  };

  return (
    <Button onClick={playAudio} disabled={playing}>
      🔊 Play Response
    </Button>
  );
};
```

**4.3 Azure OpenAI Model Deployments (Required)**

Before implementing voice features, deploy Whisper and TTS models in your Azure OpenAI resource:

1. **Deploy Whisper model:**
   - Go to Azure OpenAI Studio → Deployments
   - Create deployment: Model = `whisper`, Deployment name = `whisper` (or custom name)
   - Set `AZURE_WHISPER_DEPLOYMENT_NAME` environment variable

2. **Deploy TTS model:**
   - Create deployment: Model = `tts-1` or `tts-1-hd`, Deployment name = `tts` (or custom name)
   - Set `AZURE_TTS_DEPLOYMENT_NAME` environment variable

**Note:** These are Azure OpenAI deployments, not separate Azure Speech service. Everything uses your existing Azure OpenAI resource.

**4.4 Integration with Chat**
- Add VoiceRecorder to ChatConsole
- When transcription completes, populate chat input
- After AI response, optionally play TTS
- Show audio waveform during recording (optional enhancement)

**4.5 Testing**
- Test microphone permission request
- Test recording and transcription with Azure Whisper
- Test TTS generation and playback with Azure TTS
- Test error handling (denied permissions, API failures)
- Verify all voice calls use Azure OpenAI (no separate OpenAI API keys needed)

**Deliverables:**
- ✅ Voice recording works in browser
- ✅ Whisper transcription accurate
- ✅ TTS plays assistant responses
- ✅ Graceful error handling
- ✅ Visual feedback during recording/processing

---

### Phase 5: Containerization & Azure Deployment (Week 4-5)

**Goal:** Deploy to Azure Container Apps with full CI/CD pipeline

#### Tasks

**5.1 Docker Configuration**

**5.1.1 Backend Dockerfile**
```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/

# Expose port
EXPOSE 8000

# Run with uvicorn
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**5.1.2 Frontend Dockerfile**
```dockerfile
# frontend/Dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci

# Copy source and build
COPY . .
RUN npm run build

# Production image with nginx
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

**5.1.3 Frontend nginx.conf**
```nginx
server {
    listen 80;
    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
    }

    # Proxy API requests to backend
    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # WebSocket support
    location /ws {
        proxy_pass http://backend:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

**5.1.4 Docker Compose (Local Development)**
```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - AZURE_ENDPOINT=${AZURE_ENDPOINT}
      - AZURE_API_KEY=${AZURE_API_KEY}
      - AZURE_DEPLOYMENT_NAME=${AZURE_DEPLOYMENT_NAME}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - AZURE_STORAGE_CONNECTION_STRING=${AZURE_STORAGE_CONNECTION_STRING}
      - STORAGE_MODE=azure
    volumes:
      - ./backend/src:/app/src
      - ./data:/app/data

  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - backend
    environment:
      - VITE_API_URL=http://localhost:8000
```

**5.2 Azure Resources Setup**

**5.2.1 Create Azure Container Registry**
```bash
# Azure CLI commands
az group create --name factory-agent-rg --location eastus

az acr create \
  --resource-group factory-agent-rg \
  --name factoryagentacr \
  --sku Basic

# Enable admin access for Container Apps
az acr update --name factoryagentacr --admin-enabled true

# Get login credentials
az acr credential show --name factoryagentacr
```

**5.2.2 Push Images to ACR**
```bash
# Login to ACR
az acr login --name factoryagentacr

# Build and tag images
docker build -t factoryagentacr.azurecr.io/backend:latest ./backend
docker build -t factoryagentacr.azurecr.io/frontend:latest ./frontend

# Push to ACR
docker push factoryagentacr.azurecr.io/backend:latest
docker push factoryagentacr.azurecr.io/frontend:latest
```

**5.2.3 Create Container Apps Environment**
```bash
az containerapp env create \
  --name factory-agent-env \
  --resource-group factory-agent-rg \
  --location eastus
```

**5.2.4 Deploy Backend Container App**
```bash
az containerapp create \
  --name factory-backend \
  --resource-group factory-agent-rg \
  --environment factory-agent-env \
  --image factoryagentacr.azurecr.io/backend:latest \
  --registry-server factoryagentacr.azurecr.io \
  --registry-username <username> \
  --registry-password <password> \
  --target-port 8000 \
  --ingress external \
  --min-replicas 0 \
  --max-replicas 3 \
  --secrets \
    azure-openai-key=$AZURE_API_KEY \
    openai-key=$OPENAI_API_KEY \
    storage-conn=$AZURE_STORAGE_CONNECTION_STRING \
  --env-vars \
    AZURE_ENDPOINT=$AZURE_ENDPOINT \
    AZURE_DEPLOYMENT_NAME=$AZURE_DEPLOYMENT_NAME \
    AZURE_API_KEY=secretref:azure-openai-key \
    OPENAI_API_KEY=secretref:openai-key \
    AZURE_STORAGE_CONNECTION_STRING=secretref:storage-conn \
    STORAGE_MODE=azure
```

**5.2.5 Deploy Frontend Container App**
```bash
az containerapp create \
  --name factory-frontend \
  --resource-group factory-agent-rg \
  --environment factory-agent-env \
  --image factoryagentacr.azurecr.io/frontend:latest \
  --registry-server factoryagentacr.azurecr.io \
  --registry-username <username> \
  --registry-password <password> \
  --target-port 80 \
  --ingress external \
  --min-replicas 1 \
  --max-replicas 2 \
  --env-vars \
    VITE_API_URL=https://<backend-url>
```

**5.3 Azure AD Authentication Setup**

**5.3.1 Register App in Azure AD**
1. Go to Azure Portal → Azure Active Directory
2. App registrations → New registration
3. Name: "Factory Agent Web App"
4. Redirect URI: `https://<frontend-url>/auth/callback`
5. Note: Application (client) ID and Directory (tenant) ID

**5.3.2 Configure MSAL in Frontend**
```typescript
// frontend/src/authConfig.ts
import { Configuration } from '@azure/msal-browser';

export const msalConfig: Configuration = {
  auth: {
    clientId: import.meta.env.VITE_AZURE_AD_CLIENT_ID,
    authority: `https://login.microsoftonline.com/${import.meta.env.VITE_AZURE_AD_TENANT_ID}`,
    redirectUri: import.meta.env.VITE_REDIRECT_URI,
  },
  cache: {
    cacheLocation: 'localStorage',
    storeAuthStateInCookie: false,
  },
};

export const loginRequest = {
  scopes: ['User.Read'],
};
```

**5.3.3 Wrap App with MSAL Provider**
```typescript
// frontend/src/main.tsx
import { MsalProvider } from '@azure/msal-react';
import { PublicClientApplication } from '@azure/msal-browser';
import { msalConfig } from './authConfig';

const msalInstance = new PublicClientApplication(msalConfig);

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <MsalProvider instance={msalInstance}>
      <App />
    </MsalProvider>
  </React.StrictMode>
);
```

**5.3.4 Add Authentication to Components**
```typescript
// frontend/src/App.tsx
import { useIsAuthenticated, useMsal } from '@azure/msal-react';
import { loginRequest } from './authConfig';

function App() {
  const isAuthenticated = useIsAuthenticated();
  const { instance } = useMsal();

  const handleLogin = () => {
    instance.loginPopup(loginRequest);
  };

  const handleLogout = () => {
    instance.logoutPopup();
  };

  if (!isAuthenticated) {
    return (
      <div>
        <h1>Factory Agent - Please Sign In</h1>
        <Button onClick={handleLogin}>Sign in with Microsoft</Button>
      </div>
    );
  }

  return (
    <div>
      <Button onClick={handleLogout}>Sign Out</Button>
      {/* Main app content */}
    </div>
  );
}
```

**5.3.5 Secure Backend with JWT Validation**
```python
# backend/src/api/auth.py
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from jwt import PyJWKClient

security = HTTPBearer()

AZURE_AD_TENANT_ID = os.getenv("AZURE_AD_TENANT_ID")
AZURE_AD_CLIENT_ID = os.getenv("AZURE_AD_CLIENT_ID")

jwks_url = f"https://login.microsoftonline.com/{AZURE_AD_TENANT_ID}/discovery/v2.0/keys"
jwks_client = PyJWKClient(jwks_url)

async def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Verify Azure AD JWT token."""
    token = credentials.credentials

    try:
        # Get signing key
        signing_key = jwks_client.get_signing_key_from_jwt(token)

        # Verify token
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=AZURE_AD_CLIENT_ID,
            issuer=f"https://login.microsoftonline.com/{AZURE_AD_TENANT_ID}/v2.0"
        )

        return payload
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

# Protect endpoints
@router.get("/api/metrics/oee", dependencies=[Depends(verify_token)])
async def get_oee(...):
    ...
```

**5.4 GitHub Actions CI/CD**

**5.4.1 Create Workflow File**
```yaml
# .github/workflows/azure-deploy.yml
name: Deploy to Azure Container Apps

on:
  push:
    branches: [main]
  workflow_dispatch:

env:
  ACR_NAME: factoryagentacr
  RESOURCE_GROUP: factory-agent-rg

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Azure Login
        uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}

      - name: Build and push backend image
        run: |
          az acr login --name ${{ env.ACR_NAME }}
          docker build -t ${{ env.ACR_NAME }}.azurecr.io/backend:${{ github.sha }} ./backend
          docker push ${{ env.ACR_NAME }}.azurecr.io/backend:${{ github.sha }}

      - name: Build and push frontend image
        run: |
          docker build -t ${{ env.ACR_NAME }}.azurecr.io/frontend:${{ github.sha }} ./frontend
          docker push ${{ env.ACR_NAME }}.azurecr.io/frontend:${{ github.sha }}

      - name: Update backend container app
        run: |
          az containerapp update \
            --name factory-backend \
            --resource-group ${{ env.RESOURCE_GROUP }} \
            --image ${{ env.ACR_NAME }}.azurecr.io/backend:${{ github.sha }}

      - name: Update frontend container app
        run: |
          az containerapp update \
            --name factory-frontend \
            --resource-group ${{ env.RESOURCE_GROUP }} \
            --image ${{ env.ACR_NAME }}.azurecr.io/frontend:${{ github.sha }}
```

**5.4.2 Configure GitHub Secrets**
- `AZURE_CREDENTIALS`: Service principal JSON
- `AZURE_OPENAI_KEY`: Azure OpenAI API key (single key for chat + Whisper + TTS)
- `AZURE_STORAGE_CONNECTION_STRING`: Blob storage connection
- `AZURE_AD_CLIENT_ID`: Azure AD application client ID
- `AZURE_AD_TENANT_ID`: Azure AD tenant ID

**5.5 Final Testing**
- Test full authentication flow
- Test all dashboard features on Azure
- Test chat functionality on Azure
- Test voice recording and playback
- Test auto-scaling (simulate load)
- Verify monitoring in Application Insights

**Deliverables:**
- ✅ Backend and frontend containerized
- ✅ Images in Azure Container Registry
- ✅ Both containers running in Azure Container Apps
- ✅ Azure AD authentication working
- ✅ CI/CD pipeline deploying on git push
- ✅ Production data in Blob Storage
- ✅ All features working in production

---

## 📁 Final Project Structure

```
factory-agent/
├── backend/
│   ├── src/
│   │   ├── api/
│   │   │   ├── main.py              # FastAPI app
│   │   │   ├── auth.py              # JWT validation
│   │   │   └── routes/
│   │   │       ├── metrics.py       # Metrics endpoints
│   │   │       ├── chat.py          # Chat endpoints
│   │   │       ├── voice.py         # Voice endpoints (Azure OpenAI)
│   │   │       └── data.py          # Data management
│   │   ├── services/
│   │   │   └── chat_service.py      # NEW: Chat logic (extracted from main.py)
│   │   ├── metrics.py               # EXISTING (unchanged)
│   │   ├── models.py                # EXISTING (unchanged)
│   │   ├── data.py                  # EXISTING (updated for Blob)
│   │   └── config.py                # EXISTING (updated)
│   ├── tests/
│   │   ├── test_metrics.py          # EXISTING
│   │   ├── test_chat_service.py     # MIGRATED (renamed from test_main.py)
│   │   ├── test_api.py              # NEW: API endpoint tests
│   │   └── test_auth.py             # NEW: Auth tests
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── layout/
│   │   │   │   └── SplitLayout.tsx
│   │   │   ├── dashboard/
│   │   │   │   ├── DashboardPanel.tsx
│   │   │   │   ├── OEEGauge.tsx
│   │   │   │   ├── TrendChart.tsx
│   │   │   │   ├── DowntimeTable.tsx
│   │   │   │   ├── QualityTable.tsx
│   │   │   │   └── MachineFilter.tsx
│   │   │   ├── console/
│   │   │   │   ├── ConsolePanel.tsx
│   │   │   │   ├── ChatConsole.tsx
│   │   │   │   ├── MessageList.tsx
│   │   │   │   ├── MessageItem.tsx
│   │   │   │   ├── ChatInput.tsx
│   │   │   │   ├── VoiceRecorder.tsx
│   │   │   │   └── AudioPlayer.tsx
│   │   │   └── auth/
│   │   │       ├── LoginButton.tsx
│   │   │       └── LogoutButton.tsx
│   │   ├── services/
│   │   │   ├── api.ts               # Axios client
│   │   │   └── websocket.ts         # WebSocket client
│   │   ├── authConfig.ts            # MSAL configuration
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── public/
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── package.json
│   ├── vite.config.ts
│   └── .env.example
├── .github/
│   └── workflows/
│       └── azure-deploy.yml         # CI/CD pipeline
├── docker-compose.yml               # Local development
├── .gitignore
├── README.md
└── implementation-plan.md           # This file
```

---

## 🛠️ Technical Stack Summary

### Frontend
- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **UI Library**: Material-UI (MUI)
- **Charts**: Recharts
- **Layout**: react-split-pane
- **Auth**: @azure/msal-react
- **HTTP**: Axios
- **State**: React hooks (useState, useEffect, useContext)

### Backend
- **Framework**: FastAPI
- **Runtime**: Python 3.11
- **ASGI Server**: Uvicorn
- **Auth**: PyJWT + Azure AD validation
- **AI**: OpenAI SDK (Azure OpenAI + OpenAI)
- **Storage**: Azure Blob Storage SDK
- **Testing**: pytest

### Azure Services
- **Hosting**: Azure Container Apps (consumption plan)
- **Registry**: Azure Container Registry (Basic tier)
- **Storage**: Azure Blob Storage
- **Auth**: Azure AD (Entra ID)
- **AI**: Azure OpenAI Service
- **Voice**: OpenAI Whisper + TTS APIs
- **Monitoring**: Application Insights (optional)
- **CI/CD**: GitHub Actions

### Development
- **Containers**: Docker + Docker Compose
- **Version Control**: Git + GitHub
- **API Testing**: Postman or curl
- **Local Dev**: Hot reload for both frontend and backend

---

## 💰 Cost Estimates

### Azure Container Apps (Monthly)
- **Container Apps**: ~$5-10 (consumption plan, low traffic)
- **Container Registry**: ~$5 (Basic tier)
- **Blob Storage**: ~$1 (minimal data)
- **Azure AD**: Free tier
- **Total Infrastructure**: ~$11-16/month

### AI Services (Usage-based)
- **Azure OpenAI**: ~$0.002 per 1K tokens
  - Typical chat: 500 tokens = $0.001
  - Active demo day (50 chats): ~$0.05
- **OpenAI Whisper**: $0.006/minute
  - 5-second recording: ~$0.0005
- **OpenAI TTS**: $15 per 1M characters
  - 200-char response: ~$0.003
- **Daily AI costs** (20 interactions): ~$0.10-0.20

### Total Estimated Cost
- **Low usage** (few demos): ~$12-20/month
- **Active testing**: ~$15-25/month

**Cost-saving tips:**
- Scale containers to 0 when not in use
- Use Azure free credits (12 months for new accounts)
- Monitor with cost alerts

---

## 🎓 Learning Outcomes

By completing this migration, you will gain hands-on experience with:

### Azure Services
- ✅ **Azure Container Apps**: Serverless container hosting
- ✅ **Azure Container Registry**: Private Docker registry
- ✅ **Azure Blob Storage**: Cloud object storage
- ✅ **Azure AD (Entra ID)**: Enterprise authentication
- ✅ **Azure OpenAI**: Managed AI services
- ✅ **Azure Portal**: Resource management
- ✅ **Azure CLI**: Infrastructure as Code

### Development Skills
- ✅ **FastAPI**: Modern Python web framework
- ✅ **React + TypeScript**: Frontend development
- ✅ **Docker**: Containerization and orchestration
- ✅ **GitHub Actions**: CI/CD pipelines
- ✅ **REST API design**: Backend architecture
- ✅ **WebSockets**: Real-time communication (optional)
- ✅ **JWT Authentication**: Token-based security
- ✅ **Browser APIs**: MediaRecorder, Web Audio

### Architecture Patterns
- ✅ **Microservices**: Separate frontend/backend
- ✅ **Container-based deployment**: Cloud-native apps
- ✅ **Stateless API design**: Scalable backends
- ✅ **Authentication flows**: MSAL + JWT
- ✅ **Cloud storage patterns**: Blob storage usage

---

## 🔍 Code Reuse Strategy

### Unchanged (100% Reused)
- **metrics.py** (285 lines): All 4 analysis functions work as-is
- **models.py** (86 lines): Pydantic models serialize to JSON automatically

### Minor Updates (90% Reused)
- **data.py** (245 lines): Add Blob Storage SDK, keep logic
- **config.py** (21 lines): Add Azure-specific environment variables

### Refactored (60-80% Logic Reused)
- **main.py** (613 lines): Split into shared services + FastAPI routes
  - Create `backend/src/services/chat_service.py`:
    - `get_chat_response()` - extracted from `_get_chat_response()` (unchanged logic)
    - `execute_tool()` - moved as-is from main.py
    - `TOOLS` constant - moved as-is
  - Create `backend/src/api/routes/chat.py`:
    - Uses `chat_service.get_chat_response()` in endpoint
  - **Tests updated**: `tests/test_chat_service.py` replaces `tests/test_main.py`
    - All existing test logic preserved
    - Import from `services.chat_service` instead of `main`
    - Same coverage, same assertions

### Replaced (New Code)
- **dashboard.py** (255 lines): Convert to React components
- **CLI commands**: No longer needed (web-only)

### New Code
- FastAPI application (~300 lines)
- React components (~800 lines)
- Docker configurations (~100 lines)
- GitHub Actions (~80 lines)

**Total Reuse**: ~60-70% of business logic preserved

---

## ✅ Success Criteria

### Functional Requirements
- ✅ Split-pane web interface (dashboard left, console right)
- ✅ All metrics displayed: OEE, scrap, quality, downtime
- ✅ Interactive charts and tables
- ✅ Machine filtering works across all views
- ✅ Chat interface with AI assistant
- ✅ Tool-calling for accurate data retrieval
- ✅ Voice recording and transcription
- ✅ Text-to-speech playback
- ✅ Azure AD authentication required
- ✅ Deployed and accessible via HTTPS

### Technical Requirements
- ✅ FastAPI backend with REST endpoints
- ✅ React frontend with TypeScript
- ✅ Both running in Azure Container Apps
- ✅ Data persisted in Azure Blob Storage
- ✅ Automatic deployment via GitHub Actions
- ✅ All tests passing (backend pytest)
- ✅ Proper error handling and logging
- ✅ Mobile-responsive layout (optional)

### Learning Requirements
- ✅ Understand Azure Container Apps concepts
- ✅ Can deploy containers to Azure independently
- ✅ Understand React component lifecycle
- ✅ Can add new dashboard widgets
- ✅ Can extend API with new endpoints
- ✅ Understand Azure AD authentication flow

---

## 🚀 Next Steps

1. **Review this plan** and ask questions about any unclear sections
2. **Set up local environment**:
   - Install Docker Desktop
   - Install Node.js 18+
   - Install Python 3.11+
   - Install Azure CLI
3. **Start Phase 1**: Backend API development
4. **Iterate phase by phase**: Test thoroughly at each stage
5. **Deploy to Azure**: Complete Phase 5 deployment

**Ready to begin? Let's start with Phase 1: Backend API Setup!**

---

## 📚 Helpful Resources

### Azure Documentation
- [Azure Container Apps](https://learn.microsoft.com/en-us/azure/container-apps/)
- [Azure AD MSAL.js](https://learn.microsoft.com/en-us/azure/active-directory/develop/msal-js-initializing-client-applications)
- [Azure Blob Storage Python SDK](https://learn.microsoft.com/en-us/azure/storage/blobs/storage-quickstart-blobs-python)

### Framework Documentation
- [FastAPI](https://fastapi.tiangolo.com/)
- [React TypeScript](https://react-typescript-cheatsheet.netlify.app/)
- [Recharts](https://recharts.org/en-US/)
- [Material-UI](https://mui.com/material-ui/getting-started/)

### Tutorials
- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)
- [React Beginner Guide](https://react.dev/learn)
- [Docker for Python Apps](https://docs.docker.com/language/python/)

---

**Document Version**: 2.0
**Last Updated**: 2025-01-01
**Author**: Migration Planning Assistant
**Status**: Ready for Implementation
