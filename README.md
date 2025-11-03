# Factory Operations Chatbot

A cloud-native AI demonstration system for factory operations analysis, featuring an AI-powered chatbot (text and voice) and interactive web dashboard. Built with Azure AI Foundry for LLM capabilities, React for the frontend, FastAPI for the backend, and deployed on Azure Container Apps.

## 🚀 Migration Status

**This project is undergoing a phased migration from Streamlit/CLI to React + Azure Container Apps.**

- **Legacy System**: Streamlit dashboard + Typer CLI (fully functional)
- **New System**: React frontend + FastAPI backend + Azure Container Apps (in development)
- **Migration Plan**: See [implementation-plan.md](implementation-plan.md) for the phased approach

**Current Progress:**
- ✅ **Phase 1: Backend API Foundation** (Complete - PR6, PR7, PR8)
  - PR6: Production hardening (async/sync fixes, error handling)
  - PR7: Security (rate limiting, CORS, input validation)
  - PR8: Environment configuration (DEBUG mode, error verbosity)
- ✅ **Phase 2: Azure Blob Storage Integration** (Complete - PR9, PR10)
  - Azure Storage Account created (`factoryagentdata`)
  - Blob container ready (`factory-data`)
  - PR9: Async blob storage implementation (2025-11-03)
  - PR10: Storage configuration & comprehensive testing (2025-11-03)
    - 47 new tests added (24 blob storage + 23 async data layer)
    - Storage mode switching validated
    - Migration guide in README
- 🚧 **Phase 3: React Frontend Development** (In Progress - 1/7 PRs)
  - ✅ PR11: Core API Client & Data Models (2025-11-03)
    - TypeScript API types matching all backend Pydantic models
    - Enterprise-grade Axios API client with interceptors and error handling
    - Reusable React hooks for async operations (useAsyncData, useAsyncCallback)
    - API health check component demonstrating integration
    - Full type safety for frontend-backend communication

Both systems currently coexist and share the same metrics engine and data layer.

## Features

- **AI-Powered Chatbot** using Azure AI Foundry (GPT-4 or other deployed models)
- **Production-Ready FastAPI Backend** with rate limiting, CORS security, and input validation
- **Azure Blob Storage Support** for cloud data persistence (Phase 2)
- **Dual Storage Mode**: Local JSON (development) or Azure Blob Storage (production)
- **Voice Interface** with OpenAI Whisper (speech-to-text) and TTS (text-to-speech)
- **Interactive Web Dashboard** with Streamlit for visual analytics
- **Manufacturing Metrics**: OEE, scrap, quality, downtime analysis
- **30 days of synthetic factory data** with interesting planted scenarios
- **Beautiful CLI** built with Typer and Rich
- **Interactive natural language queries** with tool-calling
- **4 analysis tools** for accurate data retrieval
- **Visual dashboards** with Plotly charts for OEE, availability, and quality metrics

## Tech Stack

### New Architecture (React + Azure)
- **Frontend**:
  - React + TypeScript
  - Material-UI (MUI) - Component library
  - Recharts - Data visualization
  - Vite - Build tool
  - Axios - HTTP client
  - @azure/msal-react - Azure AD authentication

- **Backend**:
  - FastAPI - Async REST API framework with CORS
  - Python 3.11+
  - Pydantic - Data validation and response models
  - Azure AI Foundry - GPT-4 with async tool-calling
  - Azure OpenAI - AsyncAzureOpenAI client for chat
  - Comprehensive logging (debug, info, warning, error levels)

- **Cloud & Deployment**:
  - Azure Container Apps - Serverless container hosting
  - Azure Blob Storage - Cloud data storage
  - Azure Container Registry - Docker image storage
  - Azure AD - Authentication
  - Docker + Docker Compose - Containerization

### Legacy System (Streamlit + CLI)
- **Typer** - CLI framework with Rich output
- **Rich** - Beautiful terminal formatting
- **Streamlit** - Interactive web dashboard (legacy)
- **Plotly** - Visualization (legacy)
- **PyAudio** - Audio recording
- **pygame** - Audio playback

## Installation

### Option 1: New System (React + FastAPI + Docker)

1. **Clone and setup environment**:
```bash
git clone <repository-url>
cd factory-agent
cp .env.example .env
# Edit .env with your Azure credentials (see below)
```

2. **Run with Docker Compose** (recommended):
```bash
docker-compose up --build
```
- Backend API: http://localhost:8000
- Frontend: http://localhost:3000
- API docs: http://localhost:8000/docs

3. **Or run manually**:

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev  # Development server on port 5173
# Or: npm run build && npm run preview  # Production build on port 3000
```

### Option 2: Legacy System (Streamlit + CLI)

1. **Setup Python environment**:
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure environment**:
```bash
cp .env.example .env
# Edit .env with your Azure credentials
```

### Azure Configuration (Both Systems)

**Edit `.env` and add**:

#### Required for AI Chat:
- `AZURE_ENDPOINT`: Your Azure OpenAI endpoint (e.g., https://your-resource.openai.azure.com/)
- `AZURE_API_KEY`: Your Azure API key from Azure Portal → Keys and Endpoint
- `AZURE_DEPLOYMENT_NAME`: Your model deployment name (e.g., gpt-4)
- `OPENAI_API_KEY`: From https://platform.openai.com/api-keys (optional, for voice interface)

#### Optional for Cloud Storage (Phase 2):
- `AZURE_STORAGE_CONNECTION_STRING`: Connection string for Azure Blob Storage (leave empty for local development)
- `STORAGE_MODE`: `local` (default, uses JSON files) or `azure` (uses Blob Storage)
- `AZURE_BLOB_CONTAINER`: Container name (default: `factory-data`)

**Note**: Local storage mode is the default. No Azure Storage setup is required for development. See [AZURE_STORAGE_SETUP.md](AZURE_STORAGE_SETUP.md) for cloud storage configuration.

### Switching from Local to Azure Blob Storage

The application supports two storage backends for production data:
1. **Local Mode** (default): Stores `production.json` in the `data/` directory
2. **Azure Mode**: Stores `production.json` in Azure Blob Storage

**To switch from local to Azure storage:**

1. **Create Azure Storage Account** (if not already done):
   ```bash
   # Using Azure CLI
   az storage account create \
     --name factoryagentdata \
     --resource-group factory-agent-rg \
     --location eastus \
     --sku Standard_LRS \
     --kind StorageV2

   # Create blob container
   az storage container create \
     --name factory-data \
     --account-name factoryagentdata
   ```

2. **Get Connection String**:
   ```bash
   # Using Azure CLI
   az storage account show-connection-string \
     --name factoryagentdata \
     --resource-group factory-agent-rg \
     --output tsv

   # Or get from Azure Portal:
   # Storage Account → Access Keys → Connection String
   ```

3. **Update `.env` file**:
   ```bash
   # Change storage mode from local to azure
   STORAGE_MODE=azure

   # Add connection string (from step 2)
   AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=factoryagentdata;AccountKey=...

   # Container name (default: factory-data)
   AZURE_BLOB_CONTAINER=factory-data
   ```

4. **Restart the application**:
   - The application will automatically use Azure Blob Storage
   - If `production.json` blob doesn't exist, it will be auto-generated on first access
   - All FastAPI endpoints will now read from/write to Azure Blob Storage

**Testing the migration:**
```bash
# 1. Verify storage mode (check logs)
tail -f logs/app.log | grep "Loading data in"
# Should show: "Loading data in azure storage mode"

# 2. Generate test data (will upload to blob)
curl -X POST http://localhost:8000/api/setup

# 3. Verify blob was created
az storage blob list \
  --container-name factory-data \
  --account-name factoryagentdata \
  --output table

# 4. Test data retrieval (will download from blob)
curl http://localhost:8000/api/stats
```

**Migrating existing data from local to Azure:**
```bash
# Option 1: Let the app auto-generate (easiest)
# Just switch STORAGE_MODE=azure and run /api/setup

# Option 2: Upload existing data manually
az storage blob upload \
  --container-name factory-data \
  --name production.json \
  --file data/production.json \
  --account-name factoryagentdata
```

**Rolling back to local storage:**
```bash
# In .env file, change:
STORAGE_MODE=local

# Restart the application
# It will now read from data/production.json again
```

**Getting Azure credentials**:
1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to your Azure OpenAI resource
3. Go to "Keys and Endpoint" section
4. Copy your endpoint URL and one of the API keys
5. Note your model deployment name from the "Deployments" section

## Usage

### New System (React + FastAPI)

#### 1. Generate Test Data
First, generate synthetic factory data (required for all interfaces):
```bash
# Using the new backend API
curl -X POST http://localhost:8000/api/setup

# Or using legacy CLI
python -m src.main setup
```

This creates 30 days of production data with planted scenarios.

#### 2. Access the Web Dashboard
Open your browser to:
- **Frontend**: http://localhost:5173 (dev) or http://localhost:3000 (production)
- **API Documentation**: http://localhost:8000/docs (interactive Swagger UI)
- **Health Check**: http://localhost:8000/health

#### 3. Backend API Endpoints

The FastAPI backend provides the following REST endpoints:

**Metrics:**
- `GET /api/metrics/oee?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD&machine=<name>` - OEE metrics
- `GET /api/metrics/scrap?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD&machine=<name>` - Scrap analysis
- `GET /api/metrics/quality?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD&severity=<level>` - Quality issues
- `GET /api/metrics/downtime?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD&machine=<name>` - Downtime analysis

**Data Management:**
- `POST /api/setup` - Generate synthetic data
- `GET /api/stats` - Data statistics
- `GET /api/machines` - List available machines
- `GET /api/date-range` - Get available data date range

**AI Chat:**
- `POST /api/chat` - AI-powered chat with tool calling and conversation history
  - Request: `{"message": "What was the OEE in October?", "history": []}`
  - Response: `{"response": "The OEE was 89.2%...", "history": [...]}`
  - Features: Natural language queries, automatic tool selection, maintains context

**Voice (Coming Soon - PR12):**
- `POST /api/voice/transcribe` - Speech-to-text (Azure OpenAI Whisper)
- `POST /api/voice/synthesize` - Text-to-speech (Azure OpenAI TTS)

#### 4. Frontend Development

The React frontend is built with TypeScript and Material-UI:

```bash
cd frontend
npm run dev        # Start development server (http://localhost:5173)
npm run build      # Build for production
npm run preview    # Preview production build
npm run lint       # Run ESLint
```

**Key Features:**
- Split-pane layout (Dashboard | Console)
- OEE gauge and trend charts
- Downtime and quality tables
- Interactive chat console
- Machine filtering
- Date range selection

**API Integration (PR11):**
The frontend now includes a complete API client foundation:

```typescript
import apiService from './services/api';

// Type-safe API calls with automatic error handling
const machines = await apiService.getMachines();
const oee = await apiService.getOEE({
  start_date: '2024-10-01',
  end_date: '2024-10-31'
});

// React hooks for async operations
const { data, loading, error, refetch } = useAsyncData(
  async () => await apiService.getMachines()
);
```

**Available API Methods:**
- `checkHealth()` - API health check
- `generateData()` - Generate test data
- `getStats()` - Data statistics
- `getMachines()` - List available machines
- `getDateRange()` - Get available data date range
- `getOEE(params?)` - OEE metrics
- `getScrap(params?)` - Scrap analysis
- `getQuality(params?)` - Quality issues
- `getDowntime(params?)` - Downtime analysis
- `sendChatMessage(request)` - AI chat

All methods are fully typed with TypeScript interfaces matching backend Pydantic models.

---

### Legacy System (CLI + Streamlit)

#### Setup
Generate synthetic factory data:
```bash
python -m src.main setup
```

This creates 30 days of production data with planted scenarios and saves it to `data/production.json`.

#### Chat Interface (Legacy)
Launch the interactive AI chatbot:
```bash
python -m src.main chat
```

Ask questions in natural language. The chatbot uses Azure AI's tool-calling capabilities to retrieve accurate data.

**Example interaction**:
```
You: What was our OEE this week?
Assistant: [Uses calculate_oee tool to retrieve data and provides analysis]

You: Show me quality issues from day 15
Assistant: [Uses get_quality_issues tool and explains the quality spike]
```

Type `exit`, `quit`, or press Ctrl+C to end the chat session.

#### Voice Interface (Legacy)
Launch the voice-based chatbot:
```bash
python -m src.main voice
```

The voice interface provides the same functionality as the text chat, but with audio input/output:

- Press Enter to record your question (5 seconds)
- Whisper API transcribes your speech to text
- Azure AI processes your question using the same tool-calling logic
- TTS API generates natural-sounding speech response
- Audio plays while text is displayed

**Requirements**:
- OpenAI API key (set `OPENAI_API_KEY` in `.env`)
- Working microphone
- Audio output (speakers/headphones)

**Installation Notes**:
- **macOS**: `brew install portaudio && pip install -r requirements.txt`
- **Windows**: `pip install -r requirements.txt` (PyAudio wheel includes PortAudio)

**Cost Estimates** (OpenAI APIs):
- Whisper: $0.006/minute of audio
- TTS: $15 per 1M characters (~$0.015 per typical response)
- Typical demo session (20 questions): ~$0.50

**Example Voice Questions**:
Same as text chat:
- "What was our OEE this week?"
- "Show me quality issues from day 15"
- "Which machine had the most downtime?"

#### Web Dashboard (Legacy - Streamlit)
Launch the interactive web dashboard:
```bash
python run_dashboard.py
```

Or directly with Streamlit:
```bash
streamlit run src/dashboard.py
```

The dashboard opens automatically in your browser at `http://localhost:8501` and provides:

- **OEE Dashboard**: Gauge chart showing current OEE percentage and trend line over 30 days
- **Availability Dashboard**: Downtime analysis by reason and major downtime events table
- **Quality Dashboard**: Scrap rate trends and quality issues with severity highlighting

Use the sidebar to filter metrics by specific machines or view all machines combined.

#### Stats (Legacy CLI)
View data statistics:
```bash
python -m src.main stats
```

Displays a summary table with date range, number of days, machines, and shifts.

## Example Questions (Chatbot Interface)

- "What was our OEE this week?"
- "Show me quality issues from day 15"
- "Which machine had the most downtime?"
- "Compare day shift vs night shift performance"
- "What happened on day 22?"
- "Analyze scrap rates for Assembly-001"

## Dashboard Features

The web dashboard provides three interactive tabs:

### OEE Tab
- **Gauge Chart**: Current OEE percentage with color-coded performance zones (red: 0-60%, yellow: 60-75%, green: 75-100%)
- **Trend Chart**: 30-day OEE performance trend line showing improvement over time

### Availability Tab
- **Downtime Bar Chart**: Total downtime hours aggregated by reason (changeover, maintenance, breakdown, etc.)
- **Major Events Table**: Detailed view of significant downtime events (>2 hours) including the Day 22 bearing failure

### Quality Tab
- **Scrap Rate Trend**: Daily scrap rate percentage over 30 days with area fill
- **Quality Issues Table**: Comprehensive list of defects with severity color-coding (High: red, Medium: yellow, Low: green)

## Analysis Tools

The chatbot has access to 4 analysis tools:

1. **calculate_oee** - Overall Equipment Effectiveness metrics with availability, performance, and quality breakdown
2. **get_scrap_metrics** - Scrap rates and waste analysis by machine
3. **get_quality_issues** - Defect tracking with severity filtering
4. **get_downtime_analysis** - Downtime reasons, duration, and major incidents

All tools support optional machine filtering and date range selection.

## Planted Scenarios

The synthetic data includes interesting scenarios for demonstration:

1. **Quality Spike** (Day 15): Elevated defects on Assembly-001 - excellent for testing quality issue queries
2. **Machine Breakdown** (Day 22): 4-hour critical bearing failure on Packaging-001 - demonstrates downtime analysis
3. **Performance Improvement**: OEE increases from 65% to 80% over 30 days - shows trend analysis
4. **Shift Differences**: Night shift consistently 5-8% lower performance - enables shift comparison

## Deployment

### Docker (Local Development)

Run both frontend and backend with Docker Compose:

```bash
docker-compose up --build
```

This starts:
- **Backend**: http://localhost:8000 (FastAPI + Uvicorn)
- **Frontend**: http://localhost:3000 (React + Nginx)

### Azure Container Apps (Production)

**Coming Soon** - See [implementation-plan-prs.md](implementation-plan-prs.md) for deployment roadmap (PR14-PR15).

The production deployment will include:
- Azure Container Registry for Docker images
- Azure Container Apps for serverless hosting
- Azure Blob Storage for data persistence (Phase 2 complete - PR9, PR10)
- Azure AD for authentication
- GitHub Actions for CI/CD

**Phase 2 Status**: Azure Storage Account (`factoryagentdata`) and blob container (`factory-data`) have been created and configured. The application supports dual storage modes (local JSON and Azure Blob Storage), with 47 comprehensive tests validating both backends. Local JSON is the default for development.

---

## Project Structure

```
factory-agent/
├── backend/                         # NEW: FastAPI backend
│   ├── src/
│   │   ├── api/
│   │   │   ├── main.py             # FastAPI app with CORS
│   │   │   └── routes/
│   │   │       ├── metrics.py      # Metrics endpoints
│   │   │       ├── data.py         # Data management endpoints
│   │   │       └── chat.py         # AI chat endpoint
│   │   ├── services/
│   │   │   └── chat_service.py     # Shared chat logic
│   │   ├── metrics.py              # Analysis functions (shared)
│   │   ├── models.py               # Pydantic models (shared)
│   │   ├── data.py                 # Data storage (shared, Azure Blob support)
│   │   └── config.py               # Configuration (shared)
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
│
├── frontend/                        # NEW: React frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── dashboard/
│   │   │   │   ├── OEEGauge.tsx
│   │   │   │   ├── TrendChart.tsx
│   │   │   │   ├── DowntimeTable.tsx
│   │   │   │   ├── QualityTable.tsx
│   │   │   │   └── MachineFilter.tsx
│   │   │   ├── console/
│   │   │   │   ├── ChatConsole.tsx
│   │   │   │   ├── MessageList.tsx
│   │   │   │   ├── MessageItem.tsx
│   │   │   │   └── ChatInput.tsx
│   │   │   ├── ApiHealthCheck.tsx  # PR11: Health check component
│   │   │   ├── DashboardPanel.tsx
│   │   │   └── ConsolePanel.tsx
│   │   ├── services/
│   │   │   └── api.ts              # PR11: Axios API client with interceptors
│   │   ├── types/
│   │   │   └── api.ts              # PR11: TypeScript API interfaces
│   │   ├── utils/
│   │   │   └── async.ts            # PR11: React hooks & async utilities
│   │   ├── App.tsx                 # Main app with split-pane
│   │   └── main.tsx                # Entry point
│   ├── package.json
│   ├── vite.config.ts
│   ├── Dockerfile
│   └── nginx.conf
│
├── src/                             # LEGACY: Original CLI/Streamlit
│   ├── __init__.py
│   ├── config.py                   # Configuration (20 lines)
│   ├── data.py                     # Data storage (217 lines)
│   ├── metrics.py                  # Analysis functions (276 lines)
│   ├── main.py                     # CLI interface (695 lines)
│   └── dashboard.py                # Streamlit dashboard (225 lines)
│
├── tests/
│   ├── test_chat_service.py        # Chat service tests
│   ├── test_api.py                 # API endpoint tests
│   └── test_config.py              # Configuration tests
│
├── data/
│   └── production.json             # Generated synthetic data
│
├── docs/                           # Deployment documentation
│   └── AZURE_STORAGE_SETUP.md      # Azure Blob Storage setup guide (Phase 2)
│
├── .github/
│   └── workflows/
│       └── azure-deploy.yml        # NEW: CI/CD pipeline
│
├── docker-compose.yml              # NEW: Local development
├── .env.example
├── .gitignore
├── requirements.txt                # Legacy dependencies
├── implementation-plan.md          # Original plan
├── implementation-plan-prs.md      # NEW: 15-PR migration plan
└── README.md                       # This file
```

**Legacy System**: ~1,434 lines across 5 modules + 222 lines of tests
**New System**: In development (see implementation-plan-prs.md for progress)

## How It Works

### New Architecture (React + FastAPI)

1. **Frontend (React)**:
   - Split-pane layout with Dashboard and Console panels
   - Material-UI components for consistent design
   - Recharts for data visualization
   - Type-safe API client with full error handling (PR11)
   - Reusable React hooks for async operations (useAsyncData, useAsyncCallback)
   - Real-time chat interface

2. **Backend (FastAPI)**:
   - RESTful API endpoints for metrics, data, and chat
   - Async request handling
   - Pydantic models for validation
   - CORS enabled for frontend communication
   - Automatic API documentation (Swagger UI)

3. **Shared Metrics Engine** (`backend/src/metrics.py`):
   - Provides 4 analysis functions (OEE, scrap, quality, downtime)
   - Reused by both legacy and new systems
   - No changes from original implementation

4. **AI Chat Service** (`shared/chat_service.py`):
   - Async tool-calling pattern with Azure AI Foundry (AsyncAzureOpenAI)
   - Maintains conversation history across turns
   - Routes tool calls to metrics functions
   - Comprehensive logging for debugging
   - Shared by CLI, voice, and web chat interfaces
   - Configuration via environment variables

5. **Data Layer** (`backend/src/data.py`):
   - Dual storage mode: local JSON files (default) or Azure Blob Storage
   - Configurable via `STORAGE_MODE` environment variable
   - Local mode: Fast, no network latency, works offline (development)
   - Azure mode: Cloud persistence, durable, multi-instance compatible (production)
   - Generates synthetic factory data (30 days with planted scenarios)

### Legacy Architecture (Streamlit + CLI)

1. **Data Generation** (`src/data.py`): Creates 30 days of realistic factory data with planted scenarios
2. **Metrics Engine** (`src/metrics.py`): Provides 4 analysis functions that process the data
3. **CLI Interface** (`src/main.py`): Typer-based commands with Rich formatting and reusable chat functions
4. **Web Dashboard** (`src/dashboard.py`): Streamlit app with Plotly visualizations
5. **Tool-Calling Pattern**: AI receives tool definitions, calls them with arguments, and synthesizes responses
6. **Conversation Loop**: Maintains history and handles multi-turn tool calling

### Reusable Chat Functions (PR #3)

The chatbot logic has been extracted into 3 reusable functions for sharing with voice interface:

- `_build_system_prompt()`: Constructs system prompt with factory context
- `_get_chat_response()`: Manages Claude API tool-calling loop, returns text and updated history
- `execute_tool()`: Routes tool calls to metric functions

These functions enable both text and voice interfaces to share the same chat logic.

### Architecture Flow

**New System (React + FastAPI):**
```
React Frontend → Axios HTTP Client → FastAPI Backend → Metrics Functions → JSON/Azure Blob → Response

API Client Layer (PR11):
TypeScript Component → useAsyncData/useAsyncCallback Hook → apiService Method →
Axios Request Interceptor → Backend Endpoint → Response Interceptor → Error Handler → Component State

Chat Flow:
User Message → POST /api/chat → Chat Service → Azure AI (tool-calling) →
Metrics Functions → JSON Data → AI Response → Frontend

Dashboard Flow:
Component Mount → GET /api/metrics/* → Metrics Functions → JSON Data → Recharts Visualization
```

**Legacy System (CLI + Streamlit):**
```
Text Chat Interface:
User Question → Azure AI → Tool Selection → Metrics Functions → JSON Data → Response

Voice Chat Interface:
Audio Input → Whisper API → Text → Azure AI → Tool Selection →
Metrics Functions → JSON Data → Response → TTS API → Audio Output

Dashboard Interface:
User Interaction → Streamlit UI → Metrics Functions → JSON Data → Plotly Charts
```

All interfaces (new and legacy) share the same underlying metrics engine and data storage, ensuring consistency.

## Development Notes

### Migration Philosophy

This project is being migrated from a simple demo to a cloud-native application while maintaining:
- **Phased approach**: 15 small PRs instead of one big rewrite
- **Backward compatibility**: Legacy system remains functional during migration
- **Shared core logic**: Metrics engine reused across all interfaces
- **Incremental value**: Each PR delivers testable functionality

### Legacy System Design (Streamlit + CLI)

Built following simplicity-first principles for rapid prototyping:
- **JSON files** instead of database (easier to inspect and debug)
- **Synchronous I/O** (appropriate for single-user demos)
- **Smoke test coverage** (6 tests, 100% coverage of core chat functions)
- **Shared metrics layer** (both interfaces use the same analysis functions)
- **Streamlit for dashboards** (Python-native, zero JavaScript required)
- **~1,100 lines total** (compact and maintainable)

### New System Design (React + FastAPI + Azure)

Production-ready architecture with modern best practices:
- **Async FastAPI backend** (scalable, high performance)
- **Production hardening** (rate limiting, CORS, input validation - PR7)
- **Environment configuration** (DEBUG mode, error verbosity - PR8)
- **React + TypeScript frontend** (type-safe, component-based)
- **Type-safe API client** (PR11 - Complete type coverage, error handling, React hooks)
  - TypeScript interfaces matching backend Pydantic models
  - Axios client with request/response interceptors
  - Reusable React hooks (useAsyncData, useAsyncCallback)
  - Centralized error handling and user-friendly messages
- **Azure Blob Storage** (cloud-native data persistence - Phase 2 complete)
- **Dual storage mode** (local JSON for dev, Azure Blob for production)
- **Docker containerization** (portable, reproducible deployments)
- **Azure Container Apps** (serverless, auto-scaling)
- **Azure AD authentication** (enterprise-grade security)
- **CI/CD with GitHub Actions** (automated deployments)

## 📚 Documentation

### Root Directory
- **[README.md](README.md)** - Main project documentation (you are here)
- **[implementation-plan.md](implementation-plan.md)** - Complete migration roadmap with PR breakdown
- **[INSTALL.md](INSTALL.md)** - Installation and setup instructions
- **[PR11_IMPLEMENTATION.md](PR11_IMPLEMENTATION.md)** - Latest PR implementation details

### Reference Documentation (`docs/reference/`)
- **[ARCHITECTURE.md](docs/reference/ARCHITECTURE.md)** - Complete technical architecture
- **[QUICK_REFERENCE.md](docs/reference/QUICK_REFERENCE.md)** - Quick lookup for common tasks
- **[CODEBASE_GUIDE.md](docs/reference/CODEBASE_GUIDE.md)** - Guide to navigating the codebase
- **[BACKEND_API_REFERENCE.md](docs/reference/BACKEND_API_REFERENCE.md)** - API endpoint documentation
- **[AZURE_STORAGE_SETUP.md](docs/reference/AZURE_STORAGE_SETUP.md)** - Azure Blob Storage setup guide
- **[WORKFLOW.md](docs/reference/WORKFLOW.md)** - Development workflow and best practices

### Historical Documentation (`docs/archive/`)
Historical planning documents and implementation summaries from the migration process.

### Testing

**Backend tests:**
```bash
cd backend
pytest tests/ -v
```

**Frontend tests:**
```bash
cd frontend
npm run test
```

**Coverage**:
- Legacy: 6 smoke tests covering core chat functions
- New system: API endpoint tests, chat service tests (expanding with each PR)

### Design Philosophy

**Multi-Interface Approach:**
- **Web dashboard (React)**: Visual analysis and at-a-glance metrics
- **Chat interface**: Exploratory analysis and natural language queries
- **Voice interface**: Hands-free operation and accessibility
- **REST API**: Programmatic access for integrations

All interfaces provide complementary ways to interact with the same factory data.

## License

MIT
