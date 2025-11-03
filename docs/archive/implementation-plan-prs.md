# Azure Migration: PR-Sized Implementation Plan
## Factory Agent: Streamlit/CLI → React + Azure Container Apps

**Version:** 2.1 (PR Breakdown)
**Created:** 2025-01-01
**Updated:** 2025-01-02
**Target Timeline:** 4-5 weeks (15 PRs across 4 parallel tracks)
**Architecture:** Azure Container Apps + FastAPI + React

---

## 🎯 Overview

This document breaks down the [original implementation plan](implementation-plan.md) into **15 PR-sized chunks** organized across **4 parallel tracks**. Each PR is:
- **Reviewable in 30-60 minutes** (~100-400 LOC)
- **Independently testable**
- **Delivers incremental value**
- **Has clear dependencies**

---

## 📊 PR Breakdown Summary

| Track | PRs | Focus | Duration | Dependencies |
|-------|-----|-------|----------|--------------|
| **Track 1: Backend Foundation** | PR1-PR5 | FastAPI API setup | Weeks 1-2 | Sequential |
| **Track 2: Frontend Development** | PR6-PR9 | React UI implementation | Weeks 2-4 | After PR2 |
| **Track 3: Cloud Infrastructure** | PR10-PR11 | Azure & Docker setup | Week 3 | After PR3, parallel with Track 2 |
| **Track 4: Advanced Features** | PR12-PR13 | Voice & Auth | Week 4-5 | After PR5, PR9 |
| **Deployment** | PR14-PR15 | Azure deployment | Week 5 | After all tracks |

**Total:** 15 PRs, ~2,900-4,400 LOC, **72-98 developer-hours** (active coding time per developer, not parallelized wall-clock time)

---

## 🔄 Track 1: Backend Foundation (Sequential)

### PR1: FastAPI Project Setup & Health Check
**Goal:** Establish FastAPI project structure with basic health endpoint

**Estimated Effort:** 2-4 hours | **LOC:** ~100-150

**Tasks:**
- Create `backend/` directory structure:
  ```
  backend/
  ├── src/
  │   └── api/
  │       └── main.py
  ├── requirements.txt
  └── .env.example
  ```
- Set up FastAPI app in `backend/src/api/main.py`
- Configure CORS for local React development
- Add `GET /health` endpoint
- Create `requirements.txt` with FastAPI, uvicorn, python-dotenv
- Add `.env.example` with placeholder variables

**Testing:**
```bash
cd backend
uvicorn src.api.main:app --reload
curl http://localhost:8000/health
```

**Deliverable:**
- ✅ FastAPI app runs on port 8000
- ✅ Health check returns `{"status": "healthy"}`
- ✅ CORS configured for localhost:3000

**Files Changed:**
- `backend/src/api/main.py` (new)
- `backend/requirements.txt` (new)
- `backend/.env.example` (new)

---

### PR2: Metrics API Endpoints
**Goal:** Implement REST endpoints for OEE, scrap, quality, and downtime metrics

**Estimated Effort:** 4-6 hours | **LOC:** ~150-200

**Dependencies:** PR1

**Tasks:**
- Copy `src/metrics.py` → `backend/src/metrics.py` (unchanged)
- Copy `src/models.py` → `backend/src/models.py` (unchanged)
- Copy `src/data.py` → `backend/src/data.py` (unchanged)
- Copy `src/config.py` → `backend/src/config.py` (minor updates)
- Create `backend/src/api/routes/metrics.py`:
  ```python
  GET /api/metrics/oee?start_date=X&end_date=Y&machine=Z
  GET /api/metrics/scrap?start_date=X&end_date=Y&machine=Z
  GET /api/metrics/quality?start_date=X&end_date=Y&severity=X&machine=Z
  GET /api/metrics/downtime?start_date=X&end_date=Y&machine=Z
  ```
- Wire up routes in `main.py`
- Update `requirements.txt` with pydantic

**Testing:**
```bash
# Generate test data first (using old CLI)
python -m src.main setup

# Test endpoints
curl "http://localhost:8000/api/metrics/oee?start_date=2024-01-01&end_date=2024-01-31"
```

**Deliverable:**
- ✅ All 4 metrics endpoints return JSON
- ✅ Query parameters work (date filters, machine filters)
- ✅ Pydantic models auto-serialize
- ✅ No changes to original `metrics.py` logic

**Files Changed:**
- `backend/src/api/routes/metrics.py` (new)
- `backend/src/metrics.py` (copied)
- `backend/src/models.py` (copied)
- `backend/src/data.py` (copied)
- `backend/src/config.py` (copied with minor updates)
- `backend/src/api/main.py` (updated)
- `backend/requirements.txt` (updated)

---

### PR3: Data Management Endpoints
**Goal:** Add endpoints for data generation and metadata queries

**Estimated Effort:** 3-4 hours | **LOC:** ~100-150

**Dependencies:** PR2

**Tasks:**
- Create `backend/src/api/routes/data.py`
- Implement endpoints:
  ```python
  POST /api/setup          # Generate synthetic data
  GET  /api/stats          # Get data statistics
  GET  /api/machines       # List available machines
  GET  /api/date-range     # Get available data date range
  ```
- Wire up routes in `main.py`

**Testing:**
```bash
# Generate data via API
curl -X POST http://localhost:8000/api/setup

# Verify stats
curl http://localhost:8000/api/stats
curl http://localhost:8000/api/machines
```

**Deliverable:**
- ✅ Can generate test data via API
- ✅ Can query data metadata
- ✅ All endpoints return proper JSON responses

**Files Changed:**
- `backend/src/api/routes/data.py` (new)
- `backend/src/api/main.py` (updated)

---

### PR4: Extract Chat Service (Refactoring)
**Goal:** Refactor chat logic from CLI into reusable service layer

**Estimated Effort:** 4-6 hours | **LOC:** ~250 (mostly moving code)

**Dependencies:** PR3

**Tasks:**
- Create `backend/src/services/chat_service.py`
- Move from `src/main.py`:
  - `_get_chat_response()` → `get_chat_response()` (remove underscore, no logic changes)
  - `execute_tool()` (move as-is)
  - `TOOLS` constant (move as-is)
  - `_build_system_prompt()` → `build_system_prompt()`
- Rename `tests/test_main.py` → `tests/test_chat_service.py`
- Update test imports:
  ```python
  # OLD: from src.main import _get_chat_response, execute_tool
  # NEW: from src.services.chat_service import get_chat_response, execute_tool
  ```
- Update `src/main.py` to import from `chat_service`
- Verify CLI still works

**Testing:**
```bash
# CRITICAL: First update test imports before running pytest!
# Edit tests/test_chat_service.py and change:
#   from src.main import _get_chat_response, execute_tool
# To:
#   from src.services.chat_service import get_chat_response, execute_tool

# Then run tests (should all pass)
pytest tests/test_chat_service.py

# Verify CLI still works
python -m src.main chat
```

**Deliverable:**
- ✅ Chat service extracted to backend/src/services/chat_service.py
- ✅ Tests renamed and imports updated
- ✅ All tests pass after import updates
- ✅ CLI chat command still works
- ✅ Code is DRY (shared between CLI and API)
- ✅ No logic changes, pure refactoring

**CI/CD Note:** This PR will break CI until test imports are updated. The refactoring and test updates must be in the same commit to avoid breaking builds.

**Files Changed:**
- `backend/src/services/chat_service.py` (new)
- `tests/test_chat_service.py` (renamed from test_main.py)
- `src/main.py` (updated to use chat_service)

---

### PR5: Chat API Endpoint (UPDATED for PR4 Option 2)
**Goal:** Add async REST endpoint for AI chat using shared.chat_service

**Estimated Effort:** 6-8 hours | **LOC:** ~200-250

**Dependencies:** PR4 (Option 2 - shared package structure)

**Important Changes from Original Plan:**
- PR4 was refactored to use proper shared package structure
- Chat service now in `shared/chat_service.py` (not `backend/src/services/`)
- Must convert chat_service to async/await (critical for FastAPI)
- Must add logging throughout
- Must fix type hints and remove `# type: ignore`

**Tasks:**

**Phase 1: Make Chat Service Async (Critical)**
- Convert `shared/chat_service.py` to async:
  ```python
  from openai import AsyncAzureOpenAI  # Use async client

  async def build_system_prompt() -> str:
      """Build system prompt with factory context..."""
      data = await load_data()  # Make load_data async
      # ... rest of implementation

  async def execute_tool(tool_name: str, tool_args: Dict[str, Any]) -> Dict[str, Any]:
      """Execute a tool function and return results as dictionary."""
      if tool_name == "calculate_oee":
          result = await calculate_oee(**tool_args)  # Make metrics async
      # ... rest of implementation

  async def get_chat_response(
      client: AsyncAzureOpenAI,  # Use async client
      system_prompt: str,
      conversation_history: List[Dict[str, Any]],
      user_message: str,
  ) -> Tuple[str, List[Dict[str, Any]]]:
      """Get Azure OpenAI response with tool calling."""
      # ... setup ...

      while True:
          response = await client.chat.completions.create(  # await async call
              model=AZURE_DEPLOYMENT_NAME,  # Use config (not hardcoded)
              messages=messages,
              tools=TOOLS,
              tool_choice="auto",
          )
          # ... rest of implementation
  ```

**Phase 2: Add Logging**
- Add logging to `shared/chat_service.py`:
  ```python
  import logging

  logger = logging.getLogger(__name__)

  async def get_chat_response(...):
      logger.info(f"Processing chat message: {user_message[:50]}...")
      # ... implementation with debug/error logging

  async def execute_tool(tool_name: str, tool_args: Dict[str, Any]):
      logger.info(f"Executing tool: {tool_name} with args: {tool_args}")
      try:
          # ... tool execution
          logger.debug(f"Tool {tool_name} completed successfully")
      except Exception as e:
          logger.error(f"Error executing tool {tool_name}: {e}", exc_info=True)
          return {"error": f"Tool execution failed: {str(e)}"}
  ```

**Phase 3: Fix Configuration**
- Move hardcoded model name to config:
  ```python
  # In shared/config.py
  AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o")

  # In shared/chat_service.py
  from shared.config import AZURE_OPENAI_DEPLOYMENT_NAME

  response = await client.chat.completions.create(
      model=AZURE_OPENAI_DEPLOYMENT_NAME,  # Use config instead of hardcoded
      # ...
  )
  ```

**Phase 4: Create Chat API Endpoint**
- Create `backend/src/api/routes/chat.py`:
  ```python
  from typing import List, Dict, Any
  from fastapi import APIRouter, HTTPException, Depends
  from pydantic import BaseModel
  from openai import AsyncAzureOpenAI

  from shared.chat_service import get_chat_response, build_system_prompt
  from shared.config import AZURE_ENDPOINT, AZURE_API_KEY, AZURE_DEPLOYMENT_NAME

  router = APIRouter(prefix="/api", tags=["Chat"])

  # Request/Response models
  class ChatMessage(BaseModel):
      role: str
      content: str

  class ChatRequest(BaseModel):
      message: str
      history: List[Dict[str, Any]] = []

  class ChatResponse(BaseModel):
      response: str
      history: List[Dict[str, Any]]

  # Dependency: Get Azure OpenAI client
  async def get_openai_client() -> AsyncAzureOpenAI:
      return AsyncAzureOpenAI(
          azure_endpoint=AZURE_ENDPOINT,
          api_key=AZURE_API_KEY,
          api_version="2024-08-01-preview",
      )

  @router.post("/chat", response_model=ChatResponse)
  async def chat(
      request: ChatRequest,
      client: AsyncAzureOpenAI = Depends(get_openai_client)
  ):
      """Chat endpoint with AI assistant using tool calling."""
      try:
          system_prompt = await build_system_prompt()
          response_text, updated_history = await get_chat_response(
              client=client,
              system_prompt=system_prompt,
              conversation_history=request.history,
              user_message=request.message
          )
          return ChatResponse(response=response_text, history=updated_history)
      except Exception as e:
          logger.error(f"Chat endpoint error: {e}", exc_info=True)
          raise HTTPException(status_code=500, detail=str(e))
  ```

**Phase 5: Update Tests**
- Update `tests/test_chat_service.py` for async functions:
  ```python
  import pytest

  @pytest.mark.anyio
  async def test_build_system_prompt_async():
      """Test async build_system_prompt."""
      # ... test implementation

  @pytest.mark.anyio
  async def test_get_chat_response_async():
      """Test async get_chat_response."""
      # ... test implementation
  ```
- Create `tests/test_chat_api.py` for endpoint testing:
  ```python
  from fastapi.testclient import TestClient
  from backend.src.api.main import app

  client = TestClient(app)

  def test_chat_endpoint():
      response = client.post(
          "/api/chat",
          json={"message": "What is the OEE?", "history": []}
      )
      assert response.status_code == 200
      data = response.json()
      assert "response" in data
      assert "history" in data
  ```

**Phase 6: Wire Up Routes**
- Update `backend/src/api/main.py`:
  ```python
  from .routes import metrics, data, chat  # Add chat

  app.include_router(chat.router)
  ```

**Testing:**
```bash
# Test chat endpoint
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the OEE for January 2024?", "history": []}'

# Test with conversation history
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "And what about scrap?", "history": [...]}'

# Run all tests
pytest tests/test_chat_service.py tests/test_chat_api.py -v
```

**Deliverable:**
- ✅ Chat service converted to async/await
- ✅ Logging added throughout chat service
- ✅ Configuration moved from hardcoded values
- ✅ Type hints cleaned up (removed `# type: ignore`)
- ✅ Chat endpoint returns AI responses
- ✅ Tool-calling works (calls metrics functions)
- ✅ Conversation history maintained
- ✅ Tests updated for async functions
- ✅ New tests for chat API endpoint

**Files Changed:**
- `shared/chat_service.py` (updated: async, logging, config)
- `shared/config.py` (updated: added AZURE_OPENAI_DEPLOYMENT_NAME)
- `backend/src/api/routes/chat.py` (new)
- `backend/src/api/main.py` (updated: wire up chat router)
- `tests/test_chat_service.py` (updated: async tests)
- `tests/test_chat_api.py` (new)
- `pyproject.toml` (updated: pytest-anyio for async tests)

**Technical Debt Resolved:**
- ✅ Async/await patterns implemented (was CRITICAL issue)
- ✅ Logging added (was MAJOR issue)
- ✅ Hardcoded model name fixed (was MODERATE issue)
- ✅ Type hints cleaned up (was MAJOR issue)

**Milestone:** 🎉 **Backend API Complete** - All endpoints functional, async, with logging

---

## 🎨 Track 2: Frontend Development (Sequential, starts after PR2)

### PR6: React Project Setup & Layout
**Goal:** Initialize React app with split-pane layout structure

**Estimated Effort:** 4-6 hours | **LOC:** ~200-250

**Dependencies:** PR2 (needs metrics endpoints to test against)

**Tasks:**
- Create `frontend/` directory
- Initialize Vite + React + TypeScript:
  ```bash
  cd frontend
  npm create vite@latest . -- --template react-ts
  ```
- Install dependencies:
  ```bash
  npm install @mui/material @emotion/react @emotion/styled
  npm install recharts axios react-split-pane
  npm install @types/react-split-pane --save-dev
  ```
- Create `App.tsx` with SplitPane layout
- Create placeholder `DashboardPanel.tsx` and `ConsolePanel.tsx`
- Create `services/api.ts` with axios configuration
- Add `.env.example` with `VITE_API_URL`

**File Structure:**
```
frontend/
├── src/
│   ├── components/
│   │   ├── DashboardPanel.tsx (placeholder)
│   │   └── ConsolePanel.tsx (placeholder)
│   ├── services/
│   │   └── api.ts
│   ├── App.tsx
│   └── main.tsx
├── package.json
├── vite.config.ts
└── .env.example
```

**Testing:**
```bash
cd frontend
npm run dev
# Visit http://localhost:5173 - should see split layout with placeholders
```

**Deliverable:**
- ✅ React app runs on port 5173
- ✅ Split-pane layout renders
- ✅ Left/right panes show placeholder content
- ✅ Axios configured to call backend API

**Files Changed:**
- `frontend/` (new directory with full React setup)

---

### PR7: Dashboard OEE Components
**Goal:** Implement OEE gauge and trend chart with real data

**Estimated Effort:** 6-8 hours | **LOC:** ~250-300

**Dependencies:** PR6

**Tasks:**
- Create `frontend/src/components/dashboard/OEEGauge.tsx`
  - Beginner-friendly with detailed comments
  - Uses Recharts PieChart
  - Fetches from `GET /api/metrics/oee`
  - Color-coded (red/yellow/green based on OEE value)
- Create `frontend/src/components/dashboard/TrendChart.tsx`
  - Line chart showing daily OEE or scrap trends
  - Uses Recharts LineChart
  - Date range selection
- Update `DashboardPanel.tsx`:
  - Tab navigation (OEE, Availability, Quality)
  - Date range picker
  - Renders OEEGauge and TrendChart
- Update `services/api.ts` with typed endpoints:
  ```typescript
  export const getOEE = (params: {
    start_date: string;
    end_date: string;
    machine_name?: string;
  }) => api.get('/api/metrics/oee', { params });

  export const getScrap = (params: {...}) =>
    api.get('/api/metrics/scrap', { params });
  ```

**Testing:**
- Run backend and frontend together
- Verify OEE gauge loads and displays correct percentage
- Verify trend chart shows data over time
- Test date range filtering

**Deliverable:**
- ✅ OEE gauge displays with color coding
- ✅ Trend chart shows historical data
- ✅ Data fetches from backend API
- ✅ Loading states and error handling

**Files Changed:**
- `frontend/src/components/dashboard/OEEGauge.tsx` (new)
- `frontend/src/components/dashboard/TrendChart.tsx` (new)
- `frontend/src/components/DashboardPanel.tsx` (updated)
- `frontend/src/services/api.ts` (updated)

---

### PR8: Dashboard Table Components
**Goal:** Add downtime and quality tables with filtering

**Estimated Effort:** 6-8 hours | **LOC:** ~250-300

**Dependencies:** PR7

**Tasks:**
- Create `frontend/src/components/dashboard/DowntimeTable.tsx`
  - Material-UI Table component
  - Displays downtime events with sorting
  - Color-coded by duration (>2 hours highlighted red)
  - Fetches from `GET /api/metrics/downtime`
- Create `frontend/src/components/dashboard/QualityTable.tsx`
  - Material-UI Table component
  - Quality issues with severity badges
  - Color coding: Red (High), Yellow (Medium), Green (Low)
  - Fetches from `GET /api/metrics/quality`
- Create `frontend/src/components/dashboard/MachineFilter.tsx`
  - Dropdown to select machine or "All Machines"
  - Fetches machine list from `GET /api/machines`
- Update `DashboardPanel.tsx`:
  - Add MachineFilter component
  - Pass selected machine to all child components
  - Add Quality and Downtime tabs

**Testing:**
- Verify tables load data
- Test sorting functionality
- Test machine filter updates all components
- Test severity filtering in quality table

**Deliverable:**
- ✅ Downtime table shows events with color coding
- ✅ Quality table shows issues with severity badges
- ✅ Machine filter works across all dashboard components
- ✅ Proper loading states and empty states

**Files Changed:**
- `frontend/src/components/dashboard/DowntimeTable.tsx` (new)
- `frontend/src/components/dashboard/QualityTable.tsx` (new)
- `frontend/src/components/dashboard/MachineFilter.tsx` (new)
- `frontend/src/components/DashboardPanel.tsx` (updated)
- `frontend/src/services/api.ts` (updated)

---

### PR9: Console Chat Components
**Goal:** Implement chat interface with AI conversation

**Estimated Effort:** 6-8 hours | **LOC:** ~250-300

**Dependencies:** PR5 (needs chat endpoint)

**Tasks:**
- Create `frontend/src/components/console/ChatConsole.tsx`
  - Container component managing conversation state
  - Handles send message action
- Create `frontend/src/components/console/MessageList.tsx`
  - Scrollable message history
  - Auto-scroll to bottom on new messages
  - useRef + useEffect pattern
- Create `frontend/src/components/console/MessageItem.tsx`
  - Individual message bubble
  - User vs Assistant styling
  - Timestamp display
- Create `frontend/src/components/console/ChatInput.tsx`
  - Text input with send button
  - Enter key to send
  - Disabled while waiting for response
  - "Thinking..." indicator
- Update `ConsolePanel.tsx` to render ChatConsole
- Update `services/api.ts`:
  ```typescript
  export const sendChatMessage = (message: string, history: any[]) =>
    api.post('/api/chat', { message, history });
  ```

**Testing:**
- Send chat message and verify response
- Test conversation history persistence
- Test "thinking" indicator
- Test Enter key to send
- Test tool-calling (ask about metrics)

**Deliverable:**
- ✅ Chat interface functional
- ✅ Messages display in conversation history
- ✅ AI responses work with tool-calling
- ✅ Auto-scroll and loading states work
- ✅ Clean, intuitive UX

**Files Changed:**
- `frontend/src/components/console/ChatConsole.tsx` (new)
- `frontend/src/components/console/MessageList.tsx` (new)
- `frontend/src/components/console/MessageItem.tsx` (new)
- `frontend/src/components/console/ChatInput.tsx` (new)
- `frontend/src/components/ConsolePanel.tsx` (updated)
- `frontend/src/services/api.ts` (updated)

**Milestone:** 🎉 **Core Web App Complete** - Functional dashboard + chat interface

---

## ☁️ Track 3: Cloud Infrastructure (Parallel with Track 2)

### PR10: Azure Blob Storage Integration
**Goal:** Add cloud storage support with local fallback

**Estimated Effort:** 4-6 hours | **LOC:** ~150-200

**Dependencies:** PR3 (needs data endpoints)

**Tasks:**
- Update `backend/requirements.txt` with `azure-storage-blob`
- Update `backend/src/data.py`:
  ```python
  from azure.storage.blob import BlobServiceClient

  def save_data(data: Dict[str, Any]) -> None:
      if STORAGE_MODE == "azure":
          # Upload to Azure Blob Storage
          blob_service_client = BlobServiceClient.from_connection_string(conn_str)
          blob_client = blob_service_client.get_blob_client(
              container="factory-data",
              blob="production.json"
          )
          blob_client.upload_blob(json.dumps(data), overwrite=True)
      else:
          # Local file storage (existing logic)
          path = get_data_path()
          with open(path, "w") as f:
              json.dump(data, f, indent=2)
  ```
- Update `backend/src/config.py`:
  - Add `STORAGE_MODE` config (local/azure)
  - Add `AZURE_STORAGE_CONNECTION_STRING` config
- Update tests to support both storage modes
- Add documentation: `docs/azure-blob-setup.md`

**Azure Setup (manual steps, documented):**
1. Create Azure Storage Account
2. Create container: `factory-data`
3. Get connection string
4. Add to `.env`: `AZURE_STORAGE_CONNECTION_STRING=...`
5. Set `STORAGE_MODE=azure`

**Testing:**
```bash
# Test local mode (default)
STORAGE_MODE=local python -m pytest

# Test Azure mode (requires Azure account)
STORAGE_MODE=azure python -m pytest
```

**Deliverable:**
- ✅ Data persists in Azure Blob Storage
- ✅ Local development still works (default mode)
- ✅ Tests pass for both modes
- ✅ Documentation for Azure setup

**Files Changed:**
- `backend/src/data.py` (updated)
- `backend/src/config.py` (updated)
- `backend/requirements.txt` (updated)
- `tests/test_data.py` (updated)
- `docs/azure-blob-setup.md` (new)

---

### PR11: Docker Configuration
**Goal:** Containerize frontend and backend for deployment

**Estimated Effort:** 3-4 hours | **LOC:** ~100-150

**Dependencies:** PR10 (optional), PR6 (needs frontend)

**Tasks:**
- Create `backend/Dockerfile`:
  ```dockerfile
  FROM python:3.11-slim
  WORKDIR /app
  COPY requirements.txt .
  RUN pip install --no-cache-dir -r requirements.txt
  COPY src/ ./src/
  EXPOSE 8000
  CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
  ```
- Create `frontend/Dockerfile` (multi-stage):
  ```dockerfile
  # Build stage
  FROM node:18-alpine AS builder
  WORKDIR /app
  COPY package*.json ./
  RUN npm ci
  COPY . .
  RUN npm run build

  # Production stage
  FROM nginx:alpine
  COPY --from=builder /app/dist /usr/share/nginx/html
  COPY nginx.conf /etc/nginx/conf.d/default.conf
  EXPOSE 80
  CMD ["nginx", "-g", "daemon off;"]
  ```
- Create `frontend/nginx.conf` with API proxy
- Create `docker-compose.yml` for local development
- Add `.dockerignore` files

**Testing:**
```bash
# Build and run with Docker Compose
docker-compose up --build

# Verify:
# - Backend: http://localhost:8000/health
# - Frontend: http://localhost:3000
# - Frontend can call backend API
```

**Deliverable:**
- ✅ Backend containerized
- ✅ Frontend containerized with nginx
- ✅ Docker Compose works for local development
- ✅ Environment variables configured properly

**Files Changed:**
- `backend/Dockerfile` (new)
- `backend/.dockerignore` (new)
- `frontend/Dockerfile` (new)
- `frontend/nginx.conf` (new)
- `frontend/.dockerignore` (new)
- `docker-compose.yml` (new)

**Milestone:** 🎉 **Cloud-Ready** - App runs in containers

---

## 🚀 Track 4: Advanced Features

### PR12: Voice Recording & Transcription
**Goal:** Add browser-based voice chat with Azure OpenAI

**Estimated Effort:** 6-8 hours | **LOC:** ~300-350

**Dependencies:** PR5 (needs chat endpoint), PR9 (needs chat UI)

**Tasks:**
- Create `backend/src/api/routes/voice.py`
  - `POST /api/voice/transcribe` (Azure OpenAI Whisper)
  - `POST /api/voice/synthesize` (Azure OpenAI TTS)
- Update `backend/requirements.txt` (no new deps, uses existing Azure OpenAI SDK)
- Update `backend/src/config.py`:
  - Add `AZURE_WHISPER_DEPLOYMENT_NAME`
  - Add `AZURE_TTS_DEPLOYMENT_NAME`
- Create `frontend/src/components/console/VoiceRecorder.tsx`:
  - Button to start/stop recording
  - Uses browser MediaRecorder API
  - Visual feedback during recording
  - Uploads audio to `/api/voice/transcribe`
  - Populates chat input with transcription
- Create `frontend/src/components/console/AudioPlayer.tsx`:
  - Button to play TTS response
  - Fetches audio from `/api/voice/synthesize`
  - Plays with HTML5 Audio API
- Integrate with `ChatConsole.tsx`

**Azure Setup (manual, documented):**
1. Deploy Whisper model in Azure OpenAI Studio
   - Model: `whisper` (for speech-to-text)
   - API: `/openai/deployments/{name}/audio/transcriptions`
2. Deploy TTS model in Azure OpenAI Studio
   - Model: `tts-1` or `tts-1-hd` (for text-to-speech)
   - API: `/openai/deployments/{name}/audio/speech`
3. Update `.env` with deployment names

**Important:** This PR uses **Azure OpenAI audio API** (NOT Azure Speech Service). Azure OpenAI provides Whisper and TTS models through the `/audio` endpoints as of 2025. See: https://learn.microsoft.com/en-us/azure/ai-foundry/openai/concepts/audio

**Testing:**
- Test microphone permission request
- Test recording and transcription with Azure OpenAI Whisper
- Test TTS generation and playback with Azure OpenAI TTS
- Test error handling (denied permissions, API failures)
- Verify audio API endpoints work (check deployment status in Azure Portal)

**Deliverable:**
- ✅ Voice recording works in browser
- ✅ Whisper transcription accurate
- ✅ TTS plays assistant responses
- ✅ Graceful error handling
- ✅ Visual feedback during recording/processing

**Files Changed:**
- `backend/src/api/routes/voice.py` (new)
- `backend/src/config.py` (updated)
- `frontend/src/components/console/VoiceRecorder.tsx` (new)
- `frontend/src/components/console/AudioPlayer.tsx` (new)
- `frontend/src/components/console/ChatConsole.tsx` (updated)
- `docs/azure-voice-setup.md` (new)

---

### PR13: Azure AD Authentication
**Goal:** Add Microsoft account login with JWT validation

**Estimated Effort:** 6-8 hours | **LOC:** ~250-300

**Dependencies:** PR9 (needs frontend), PR5 (needs backend endpoints)

**Tasks:**
- **Frontend:**
  - Install `@azure/msal-react` and `@azure/msal-browser`
  - Create `frontend/src/authConfig.ts` with MSAL configuration
  - Update `frontend/src/main.tsx` to wrap App with MsalProvider
  - Create `frontend/src/components/auth/LoginButton.tsx`
  - Create `frontend/src/components/auth/LogoutButton.tsx`
  - Update `App.tsx` to show login screen if not authenticated
  - Update `services/api.ts` to include Bearer token in requests

- **Backend:**
  - Install `PyJWT` and `cryptography`
  - Create `backend/src/api/auth.py`:
    - `verify_token()` dependency
    - JWT validation using Azure AD public keys
  - Update all protected endpoints:
    ```python
    @router.get("/api/metrics/oee", dependencies=[Depends(verify_token)])
    ```
  - Update `backend/src/config.py`:
    - Add `AZURE_AD_TENANT_ID`
    - Add `AZURE_AD_CLIENT_ID`

- **Azure Setup (manual, documented):**
  1. Register app in Azure AD
  2. Configure redirect URI
  3. Get client ID and tenant ID
  4. Update `.env` files

**Testing:**
- Test login flow
- Test logout flow
- Test token validation on backend
- Test unauthorized access (should return 401)
- Test token expiration handling

**Deliverable:**
- ✅ App requires Microsoft login
- ✅ Backend validates JWT tokens
- ✅ Tokens refresh automatically
- ✅ Logout works properly
- ✅ Documentation for Azure AD setup

**Files Changed:**
- `frontend/package.json` (updated)
- `frontend/src/authConfig.ts` (new)
- `frontend/src/main.tsx` (updated)
- `frontend/src/components/auth/LoginButton.tsx` (new)
- `frontend/src/components/auth/LogoutButton.tsx` (new)
- `frontend/src/App.tsx` (updated)
- `frontend/src/services/api.ts` (updated)
- `backend/requirements.txt` (updated)
- `backend/src/api/auth.py` (new)
- `backend/src/api/routes/*.py` (updated with auth)
- `backend/src/config.py` (updated)
- `docs/azure-ad-setup.md` (new)

**Milestone:** 🎉 **Feature Complete** - All features implemented

---

## 🌐 Deployment Track

### PR14: Azure Infrastructure Setup
**Goal:** Configure Azure resources and CI/CD pipeline

**Estimated Effort:** 4-6 hours | **LOC:** ~200-250 (YAML + docs)

**Dependencies:** PR11 (needs Docker), PR13 (needs auth)

**Tasks:**
- Create `.github/workflows/azure-deploy.yml`:
  - Build and push Docker images to ACR
  - Update Container Apps with new images
  - Trigger on push to `main` branch
- Create `docs/azure-deployment.md`:
  - Azure CLI commands for setup
  - Container Registry creation
  - Container Apps environment creation
  - Secrets configuration
  - Custom domain setup (optional)
- Create `scripts/deploy.sh`:
  - Automated deployment script
  - Environment validation
- Update `README.md` with deployment instructions

**Azure Setup (manual, one-time):**
```bash
# Create resource group
az group create --name factory-agent-rg --location eastus

# Create Container Registry
az acr create --resource-group factory-agent-rg \
  --name factoryagentacr --sku Basic

# Create Container Apps environment
az containerapp env create --name factory-agent-env \
  --resource-group factory-agent-rg --location eastus

# Create backend Container App
az containerapp create --name factory-backend \
  --resource-group factory-agent-rg \
  --environment factory-agent-env \
  --image factoryagentacr.azurecr.io/backend:latest \
  --target-port 8000 --ingress external \
  --secrets azure-openai-key=$AZURE_API_KEY \
  --env-vars AZURE_ENDPOINT=$AZURE_ENDPOINT ...

# Create frontend Container App
az containerapp create --name factory-frontend \
  --resource-group factory-agent-rg \
  --environment factory-agent-env \
  --image factoryagentacr.azurecr.io/frontend:latest \
  --target-port 80 --ingress external
```

**GitHub Secrets Configuration:**
- `AZURE_CREDENTIALS` - Service principal JSON
- `AZURE_OPENAI_KEY`
- `AZURE_STORAGE_CONNECTION_STRING`
- `AZURE_AD_CLIENT_ID`
- `AZURE_AD_TENANT_ID`

**Testing:**
- Test CI/CD pipeline (push to main)
- Verify images build and push to ACR
- Verify Container Apps update automatically

**Deliverable:**
- ✅ CI/CD pipeline configured
- ✅ Infrastructure-as-code documented
- ✅ Deployment scripts ready
- ✅ GitHub Actions workflow functional

**Files Changed:**
- `.github/workflows/azure-deploy.yml` (new)
- `docs/azure-deployment.md` (new)
- `scripts/deploy.sh` (new)
- `README.md` (updated)

---

### PR15: Production Deployment & Final Testing
**Goal:** Deploy to Azure and verify full functionality

**Estimated Effort:** 4-6 hours + testing | **LOC:** ~100-150 (docs)

**Dependencies:** PR14

**Tasks:**
- Execute Azure deployment:
  - Deploy backend Container App with all secrets
  - Deploy frontend Container App with backend URL
  - Configure environment variables
  - Verify health checks pass
- Configure Application Insights (optional):
  - Enable monitoring
  - Set up alerts
  - Configure log analytics
- Update documentation:
  - Add production URLs to README
  - Document monitoring and troubleshooting
  - Add operational runbook
- Create end-to-end testing checklist:
  - ✅ Authentication flow works
  - ✅ Dashboard loads all metrics
  - ✅ Chat functionality works
  - ✅ Voice recording and playback work
  - ✅ Machine filtering works
  - ✅ Data persists in Blob Storage
  - ✅ Auto-scaling works (test load)
  - ✅ HTTPS and custom domain work
- Performance testing:
  - Load test chat endpoint
  - Monitor response times
  - Verify auto-scaling triggers

**Testing Checklist:**
1. Open production URL
2. Login with Microsoft account
3. Verify dashboard loads
4. Test all metric tabs
5. Send chat message about metrics
6. Test voice recording
7. Test TTS playback
8. Verify data persistence
9. Test on mobile device (responsive)
10. Check Application Insights logs

**Deliverable:**
- ✅ App running in Azure production
- ✅ All features working end-to-end
- ✅ Monitoring configured
- ✅ Documentation complete
- ✅ Operational runbook ready

**Files Changed:**
- `README.md` (updated with production URLs)
- `docs/operations.md` (new)
- `docs/troubleshooting.md` (new)

**Milestone:** 🎉 **MIGRATION COMPLETE** - Fully deployed to Azure!

---

## 📋 PR Dependency Graph

```
Track 1: Backend Foundation (Sequential)
PR1 (FastAPI Setup)
  └─> PR2 (Metrics Endpoints)
       └─> PR3 (Data Endpoints)
            ├─> PR4 (Extract Chat Service)
            │    └─> PR5 (Chat Endpoint)
            │
            └─> PR10 (Blob Storage) ────┐
                                         │
Track 2: Frontend (Sequential)          │
PR2 ──> PR6 (React Setup)                │
         └─> PR7 (OEE Components)        │
              └─> PR8 (Tables)           │
                   └─> PR9 (Chat UI) ────┤
                                         │
Track 3: Cloud (Parallel)                │
PR3 ──> PR10 (Blob Storage) ────┐        │
PR6 ──> PR11 (Docker) ──────────┼────────┤
                                │        │
Track 4: Advanced Features      │        │
PR5 + PR9 ──> PR12 (Voice) ─────┤        │
PR9 ──────────> PR13 (Auth) ────┤        │
                                │        │
Deployment Track                │        │
PR11 + PR13 ──> PR14 (Infra) ───┴────────┘
                   └─> PR15 (Deploy)
```

---

## ⏱️ Estimated Timeline

### Sequential Execution (5 weeks)
- **Week 1:** PR1-PR3 (Backend basics)
- **Week 2:** PR4-PR5 (Backend chat) + PR6-PR7 (Frontend starts)
- **Week 3:** PR8-PR9 (Frontend complete) + PR10-PR11 (Cloud setup)
- **Week 4:** PR12-PR13 (Advanced features)
- **Week 5:** PR14-PR15 (Deployment)

### Parallel Execution (3-4 weeks)
- **Week 1:** PR1-PR3 (Backend basics)
- **Week 2:**
  - PR4-PR5 (Backend chat)
  - PR6-PR7 (Frontend) - parallel
- **Week 3:**
  - PR8-PR9 (Frontend chat)
  - PR10-PR11 (Cloud) - parallel
- **Week 4:**
  - PR12-PR13 (Advanced) - parallel
  - PR14 (Infra setup)
- **Week 5:** PR15 (Final deployment + testing)

### Individual PR Times
| PR | Estimated Time | Complexity |
|----|---------------|------------|
| PR1 | 2-4 hours | Low |
| PR2 | 4-6 hours | Medium |
| PR3 | 3-4 hours | Low |
| PR4 | 4-6 hours | Medium (refactoring) |
| PR5 | 4-6 hours | Medium |
| PR6 | 4-6 hours | Medium |
| PR7 | 6-8 hours | Medium-High |
| PR8 | 6-8 hours | Medium-High |
| PR9 | 6-8 hours | Medium-High |
| PR10 | 4-6 hours | Medium |
| PR11 | 3-4 hours | Low-Medium |
| PR12 | 6-8 hours | High |
| PR13 | 6-8 hours | High |
| PR14 | 4-6 hours | Medium |
| PR15 | 4-6 hours + testing | Medium |

**Total:** ~72-98 hours (9-12 working days)

---

## ✅ Review Checklist (for each PR)

Use this checklist when reviewing each PR:

### Code Quality
- [ ] Code follows project style guide (Black formatting)
- [ ] Type hints present for all functions
- [ ] No hardcoded secrets or credentials
- [ ] Error handling implemented
- [ ] Logging added where appropriate

### Testing
- [ ] Tests written for new functionality
- [ ] All tests pass (`pytest`)
- [ ] Manual testing completed
- [ ] Edge cases considered

### Documentation
- [ ] README updated if needed
- [ ] Docstrings added to new functions
- [ ] Comments explain complex logic
- [ ] .env.example updated with new variables

### Security
- [ ] No sensitive data in code
- [ ] Input validation present
- [ ] SQL injection prevented (if applicable)
- [ ] XSS prevented (if applicable)
- [ ] Authentication/authorization correct (if applicable)

### Performance
- [ ] No obvious performance issues
- [ ] Database queries optimized (if applicable)
- [ ] Large files not committed

### Integration
- [ ] PR builds successfully
- [ ] No merge conflicts
- [ ] Dependencies updated in requirements.txt/package.json
- [ ] Backward compatibility maintained (or breaking changes documented)

---

## 🎯 Success Criteria

### After PR5 (Backend Complete)
- ✅ All metrics endpoints return data
- ✅ Chat endpoint responds with AI
- ✅ Tests pass (>90% coverage)
- ✅ API documentation available at `/docs`

### After PR9 (Frontend Complete)
- ✅ Dashboard displays all metrics
- ✅ Chat interface functional
- ✅ Split-pane layout works
- ✅ Machine filtering works

### After PR11 (Cloud Ready)
- ✅ Docker containers build
- ✅ docker-compose runs full stack
- ✅ Data persists in Azure Blob

### After PR13 (Features Complete)
- ✅ Voice recording works
- ✅ Authentication enforced
- ✅ All features integrated

### After PR15 (Deployed)
- ✅ App accessible via HTTPS
- ✅ All features work in production
- ✅ Monitoring enabled
- ✅ Documentation complete

---

## 📚 Additional Resources

### Documentation Created
- `docs/azure-blob-setup.md` - Blob Storage configuration
- `docs/azure-voice-setup.md` - Voice model deployment
- `docs/azure-ad-setup.md` - Authentication setup
- `docs/azure-deployment.md` - Full deployment guide
- `docs/operations.md` - Operational runbook
- `docs/troubleshooting.md` - Common issues

### Reference Links
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [React TypeScript Cheatsheet](https://react-typescript-cheatsheet.netlify.app/)
- [Azure Container Apps Docs](https://learn.microsoft.com/en-us/azure/container-apps/)
- [Azure OpenAI Service Docs](https://learn.microsoft.com/en-us/azure/ai-services/openai/)
- [MSAL.js Docs](https://learn.microsoft.com/en-us/azure/active-directory/develop/msal-js-initializing-client-applications)

---

## 🔄 Migration Notes

### Code Reuse
- **Unchanged:** `metrics.py`, `models.py` (100% reused)
- **Minor updates:** `data.py`, `config.py` (90% reused)
- **Refactored:** `main.py` chat logic (60-80% logic reused)
- **Replaced:** `dashboard.py` (new React components)

### Backward Compatibility
- Original CLI remains functional through PR4
- Streamlit dashboard can run alongside new app
- Both use same data file until PR10
- Gradual migration, no "big bang" cutover

### Rollback Strategy
Each PR is independently deployable:
- If PR fails review, can be abandoned without affecting previous work
- Can revert individual PRs if issues found
- Docker tags allow rolling back to previous versions

---

**Document Version:** 2.1 (PR Breakdown)
**Last Updated:** 2025-01-02
**Status:** Ready for Implementation
**Next Step:** Begin PR1 - FastAPI Project Setup
