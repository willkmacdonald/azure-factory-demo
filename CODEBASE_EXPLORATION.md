# Factory Agent - Codebase Exploration Summary

## Project Overview
Factory Agent is a cloud-native AI demonstration system for factory operations analysis. It's undergoing a phased migration from Streamlit/CLI to React + Azure Container Apps.

**Current Status**: Phase 2 Complete (Backend & Azure Blob Storage)
**Next Priority**: Phase 3 (React Frontend Development)

---

## 1. Current Project Structure

### Directory Layout
```
factory-agent/
├── backend/                         # NEW: FastAPI backend (Phase 1+)
│   ├── src/api/
│   │   ├── main.py                 # FastAPI app (193 lines) - CORS, rate limiting, health check
│   │   └── routes/
│   │       ├── metrics.py          # Metrics endpoints (129 lines)
│   │       ├── data.py             # Data management endpoints (379 lines)
│   │       └── chat.py             # Chat/AI endpoints (140+ lines)
│   ├── data/production.json        # Synthetic factory data
│   └── requirements.txt
│
├── shared/                          # Shared code (used by both backends)
│   ├── config.py                   # Configuration (42 lines) - Environment variables
│   ├── models.py                   # Pydantic models - Request/response types
│   ├── data.py                     # Data layer (async + sync) - Local JSON & Azure Blob
│   ├── blob_storage.py             # Azure Blob Storage client (227 lines) - Async operations
│   ├── metrics.py                  # Analytics engine (~276 lines) - OEE, scrap, quality, downtime
│   └── chat_service.py             # Chat logic with tool calling - Reusable for CLI/API/voice
│
├── src/                             # LEGACY: Original CLI/Streamlit
│   ├── main.py                     # Typer CLI (695 lines) - setup, chat, voice, stats commands
│   ├── dashboard.py                # Streamlit web UI (225 lines)
│   ├── data.py                     # Original data layer (217 lines) - Synchronous
│   ├── metrics.py                  # Original metrics (276 lines)
│   └── config.py                   # Original config (20 lines)
│
├── tests/                          # Comprehensive test suite (79+ tests)
│   ├── test_chat_service.py        # Chat logic tests
│   ├── test_chat_api.py            # API endpoint tests
│   ├── test_chat_integration.py    # Integration tests
│   ├── test_data_async.py          # Async data layer tests (23 tests) - NEW in PR10
│   ├── test_blob_storage.py        # Azure Blob Storage tests (24 tests) - NEW in PR10
│   └── test_config.py              # Configuration tests
│
├── data/                           # Data storage directory
│   └── production.json
│
├── .claude/                        # Claude Code project config
│   ├── CLAUDE.md                   # Project-specific guidelines
│   └── agents/
│       ├── pr-reviewer.md          # Code review standards
│       ├── security-scanner.md     # Security baseline
│       └── plan-manager.md         # Planning templates
│
├── docker-compose.yml              # Local development
├── .env.example                    # Environment variables template
├── README.md                       # Main documentation
├── implementation-plan.md          # Original plan
└── ARCHITECTURE.md                # Technical documentation
```

---

## 2. Implemented Features

### Phase 1: Backend API Foundation (COMPLETE - PR6-PR8)
- ✅ FastAPI application with CORS middleware
- ✅ Rate limiting (PR7) - SlowAPI configuration
- ✅ 4 RESTful metric endpoints:
  - GET /api/metrics/oee
  - GET /api/metrics/scrap
  - GET /api/metrics/quality
  - GET /api/metrics/downtime
- ✅ Data management endpoints:
  - POST /api/setup (data generation)
  - GET /api/stats (statistics)
  - GET /api/machines (machine list)
  - GET /api/date-range (date range info)
- ✅ Chat endpoint with tool calling:
  - POST /api/chat (AI assistant with conversation history)
- ✅ Health check endpoint: GET /health
- ✅ Async/await patterns for all I/O operations
- ✅ Input validation and sanitization (Pydantic)
- ✅ Error handling with logging

### Phase 2: Azure Blob Storage Integration (COMPLETE - PR9-PR10)
- ✅ Async Azure Blob Storage client (blob_storage.py)
  - Upload/download JSON blobs
  - Retry logic for network failures
  - Comprehensive error handling
- ✅ Dual storage mode support:
  - Local: JSON file (development)
  - Azure: Blob Storage (production)
- ✅ Async data layer (data.py):
  - load_data_async() - Load from local/blob
  - save_data_async() - Save to local/blob
  - initialize_data_async() - Generate synthetic data
- ✅ Configuration via environment variables:
  - STORAGE_MODE: "local" or "azure"
  - AZURE_STORAGE_CONNECTION_STRING
  - AZURE_BLOB_CONTAINER
  - AZURE_BLOB_NAME
- ✅ Comprehensive test coverage (47 new tests in PR10):
  - 24 blob storage tests
  - 23 async data layer tests
  - All scenarios: success, failures, retries, concurrent ops

### Legacy System (Still Functional)
- ✅ Typer CLI with Rich formatting (setup, chat, voice, stats)
- ✅ Streamlit dashboard with Plotly visualizations
- ✅ Voice interface with Whisper (speech-to-text) and TTS
- ✅ Synchronous data layer

---

## 3. API Endpoints

### Metrics Endpoints
```
GET /api/metrics/oee?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD&machine=<optional>
GET /api/metrics/scrap?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD&machine=<optional>
GET /api/metrics/quality?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD&severity=<optional>&machine=<optional>
GET /api/metrics/downtime?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD&machine=<optional>
```

Response Models:
- OEEMetrics: {oee: float, availability: float, performance: float, quality: float, ...}
- ScrapMetrics: {total_scrap: int, scrap_rate: float, by_machine: {...}, ...}
- QualityIssues: {total_issues: int, by_severity: {...}, issues: [...]}
- DowntimeAnalysis: {total_downtime: float, by_reason: {...}, major_events: [...]}

### Data Management Endpoints
```
POST /api/setup (rate-limited: 5/minute)
  Request: {"days": 30}
  Response: {message, days, start_date, end_date, machines}

GET /api/stats
  Response: {exists, start_date, end_date, total_days, total_machines, total_records}

GET /api/machines
  Response: [{id, name, type, ideal_cycle_time}, ...]

GET /api/date-range
  Response: {start_date, end_date, total_days}
```

### Chat Endpoint
```
POST /api/chat (rate-limited: 10/minute)
  Request: {message: str, history: [ChatMessage]}
  Response: {response: str, history: [ChatMessage]}
  
  Features:
  - Tool calling with 4 analysis functions
  - Conversation history management
  - Input validation and sanitization
  - Streaming support (future)
```

### System Endpoints
```
GET /health
  Response: {status: "healthy"}
```

---

## 4. Core Components

### A. Configuration System (shared/config.py)
**Purpose**: Centralized environment variable management

**Key Variables**:
- Azure OpenAI: AZURE_ENDPOINT, AZURE_API_KEY, AZURE_DEPLOYMENT_NAME
- Storage: STORAGE_MODE, AZURE_STORAGE_CONNECTION_STRING, AZURE_BLOB_CONTAINER
- Security: ALLOWED_ORIGINS, RATE_LIMIT_CHAT, RATE_LIMIT_SETUP
- Features: DEBUG, FACTORY_NAME, DATA_FILE

**Note**: Uses python-dotenv for loading from .env files

### B. Metrics Engine (shared/metrics.py)
**Purpose**: Production data analysis and KPI calculations

**Functions**:
1. `calculate_oee(start_date, end_date, machine=None)` 
   - Returns: OEE breakdown (Availability × Performance × Quality)
2. `get_scrap_metrics(start_date, end_date, machine=None)`
   - Returns: Scrap rates and waste by machine
3. `get_quality_issues(start_date, end_date, severity=None, machine=None)`
   - Returns: Quality defects with severity filtering
4. `get_downtime_analysis(start_date, end_date, machine=None)`
   - Returns: Downtime reasons and major incidents (>2 hours)

**Key Features**:
- Async functions for FastAPI compatibility
- Optional machine/severity filtering
- Comprehensive error handling
- Returns Pydantic models for type safety

### C. Data Layer (shared/data.py)
**Purpose**: Factory data persistence and retrieval

**Dual Storage Mode**:
1. **Local Mode** (default):
   - Stores JSON file: data/production.json
   - Fast, no network latency
   - For development

2. **Azure Mode**:
   - Stores in Azure Blob Storage
   - Cloud-native, multi-instance compatible
   - For production

**Functions**:
- `load_data()` - Synchronous (for CLI)
- `load_data_async()` - Asynchronous (for FastAPI)
- `save_data()` - Synchronous
- `save_data_async()` - Asynchronous
- `initialize_data()` - Generate 30 days synthetic data
- `initialize_data_async()` - Async version
- `data_exists()` - Check if data is available

**Synthetic Data Structure**:
```json
{
  "start_date": "ISO format",
  "end_date": "ISO format",
  "machines": [...],
  "shifts": [...],
  "production": {
    "day_1": [
      {machine, shift, good_parts, scrap, downtime_events, ...}
    ]
  },
  "defects": [...],
  "downtime_events": [...]
}
```

### D. Azure Blob Storage Client (shared/blob_storage.py)
**Purpose**: Async Azure Blob Storage operations

**Key Features**:
- Async I/O with aiofiles and azure-storage-blob
- Retry logic for transient failures (3 retries default)
- Comprehensive error handling:
  - Authentication errors
  - Network errors (ServiceRequestError)
  - Blob not found errors
  - JSON parsing errors
- Connection string management
- Per-operation client creation

**Methods**:
- `blob_exists()` - Check blob existence
- `upload_blob(data, max_retries=3)` - Upload JSON
- `download_blob(max_retries=3)` - Download JSON
- `close()` - Clean up resources

### E. Chat Service (shared/chat_service.py)
**Purpose**: Reusable AI chat logic with tool calling

**Key Features**:
- Azure OpenAI API integration (AsyncAzureOpenAI)
- Tool calling pattern (4 analysis functions)
- Conversation history management
- Input sanitization (prompt injection prevention)
- Logging for debugging

**Tool Functions**:
1. calculate_oee
2. get_scrap_metrics
3. get_quality_issues
4. get_downtime_analysis

**Functions**:
- `build_system_prompt()` - Factory context prompt
- `get_chat_response(client, messages)` - Tool calling loop
- `execute_tool(tool_name, args)` - Route tool calls
- `sanitize_user_input(message)` - Prevent prompt injection

### F. FastAPI Application (backend/src/api/main.py)
**Purpose**: Main FastAPI server with middleware

**Key Configuration**:
1. **CORS Middleware**:
   - Allowed origins: localhost:3000, localhost:5173
   - Methods: GET, POST only
   - Headers: Content-Type, Authorization, X-Requested-With

2. **Rate Limiting (SlowAPI)**:
   - Chat endpoint: 10 requests/minute
   - Setup endpoint: 5 requests/minute
   - Key: Client IP address

3. **Debug Mode**:
   - Controlled by DEBUG environment variable
   - Exposes detailed error messages when enabled
   - Warning logged on startup if enabled

**Routers**:
- metrics.py - Metric endpoints
- data.py - Data management
- chat.py - Chat endpoint

---

## 5. Testing Infrastructure

### Test Coverage (79+ tests total)

**Test Files**:
1. `test_config.py` - Configuration loading
2. `test_chat_service.py` - Chat logic and tool calling
3. `test_chat_api.py` - Chat endpoint integration
4. `test_chat_integration.py` - Multi-turn conversations
5. `test_data_async.py` - Async data layer (23 tests) - NEW
6. `test_blob_storage.py` - Blob storage operations (24 tests) - NEW

**Key Test Scenarios**:
- ✅ Data generation and loading
- ✅ Local storage (JSON) operations
- ✅ Azure Blob Storage operations
- ✅ Blob existence checking
- ✅ Authentication error handling
- ✅ Network error retry logic
- ✅ JSON parsing validation
- ✅ Concurrent async operations
- ✅ Large data transfers (14,400+ records)
- ✅ Chat endpoint requests
- ✅ Tool calling loop
- ✅ Input validation
- ✅ Error handling

**Test Execution**:
```bash
pytest tests/ -v
pytest tests/test_blob_storage.py -v
pytest tests/test_data_async.py -v
pytest --cov=shared --cov=backend/src --cov-report=html
```

---

## 6. Key Files by Size and Purpose

| File | Lines | Purpose |
|------|-------|---------|
| src/main.py | 695 | Legacy CLI (setup, chat, voice, stats) |
| shared/metrics.py | ~276 | Analytics engine (OEE, scrap, quality, downtime) |
| src/dashboard.py | 225 | Streamlit web UI |
| shared/blob_storage.py | 227 | Azure Blob Storage client |
| src/data.py | 217 | Legacy data layer (sync) |
| backend/src/api/routes/data.py | 379 | Data management endpoints |
| backend/src/api/routes/chat.py | 140+ | Chat endpoint |
| backend/src/api/main.py | 193 | FastAPI app setup |
| backend/src/api/routes/metrics.py | 129 | Metrics endpoints |
| shared/config.py | 42 | Configuration |

---

## 7. Technology Stack

### Backend (New System)
- **Framework**: FastAPI (async, type hints, CORS, auto docs)
- **Server**: Uvicorn (ASGI server)
- **AI**: Azure OpenAI (AsyncAzureOpenAI client)
- **Data**: 
  - Local: JSON files (pathlib, json module)
  - Cloud: Azure Blob Storage (async client)
- **Validation**: Pydantic (BaseModel, Field, validators)
- **Security**: 
  - SlowAPI (rate limiting)
  - Input sanitization (prompt injection prevention)
  - CORS middleware

### Shared Code
- **Async I/O**: aiofiles (async file operations)
- **Configuration**: python-dotenv
- **Logging**: Standard logging module

### Testing
- **Framework**: pytest
- **Async**: pytest-asyncio
- **Coverage**: pytest-cov

### Legacy System
- **CLI**: Typer (command-line interface)
- **Terminal UI**: Rich (formatted output)
- **Dashboard**: Streamlit (web UI)
- **Visualization**: Plotly
- **Voice**: Whisper API (speech-to-text), TTS (text-to-speech)

---

## 8. Frontend Status

**Current State**: NOT YET IMPLEMENTED

**Plan (Phase 3)**:
- Framework: React + TypeScript
- Build Tool: Vite
- Component Library: Material-UI (MUI)
- Charting: Recharts
- HTTP Client: Axios
- Authentication: @azure/msal-react

**Planned Components**:
- Dashboard panel (OEE gauge, trend charts)
- Console panel (chat interface)
- Machine filter
- Date range selector
- Quality and downtime tables

---

## 9. Environment Configuration

### Required Variables
```bash
# Azure OpenAI (required for chat)
AZURE_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_API_KEY=your-key
AZURE_DEPLOYMENT_NAME=gpt-4

# Optional: Azure Blob Storage (for cloud deployment)
STORAGE_MODE=local  # or "azure"
AZURE_STORAGE_CONNECTION_STRING=...
AZURE_BLOB_CONTAINER=factory-data

# Optional: Security
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
RATE_LIMIT_CHAT=10/minute
RATE_LIMIT_SETUP=5/minute
DEBUG=false
```

### Generated Synthetic Data
- **Duration**: Configurable (default 30 days)
- **Machines**: 4 types (CNC, Assembly, Packaging, Testing)
- **Shifts**: Day (6-14) and Night (14-22)
- **Metrics**: Production counts, quality issues, downtime events
- **Planted Scenarios**:
  - Day 15: Quality spike on Assembly-001
  - Day 22: 4-hour bearing failure on Packaging-001
  - Progressive OEE improvement (65% → 80%)
  - Shift performance differences (5-8% gap)

---

## 10. Recent Development History

### Phase 1: Backend API Foundation
- **PR6** (2025-10-26): Async chat API, consolidated code
- **PR7** (2025-10-27): Rate limiting, CORS security
- **PR8** (2025-10-28): Conversation history validation

### Phase 2: Azure Integration
- **PR9** (2025-11-03): Async blob storage implementation
- **PR10** (2025-11-03): Comprehensive testing, dependency fixes

### Recent Commits
```
e4bebc4 fix: PR10 review fixes - dependencies, type hints, test bug
6d7a5a0 feat: Azure Blob Storage integration (PR9)
1f82151 feat: Add rate limiting and CORS security (PR7)
379277e fix: Apply critical PR7 review fixes (async/await, security, dependencies)
fa16b21 refactor: Consolidate duplicate code and improve initialize_data() (PR6 Important issues)
```

---

## 11. Next Steps (Phase 3 - Frontend)

### PR11: React Frontend Setup
- Initialize React project with Vite
- Configure TypeScript
- Install dependencies (MUI, Recharts, Axios)
- Set up project structure

### PR12: Basic Dashboard Layout
- Split-pane layout (Dashboard | Console)
- Navigation tabs (OEE, Availability, Quality)
- Machine filter component
- Date range selector

### PR13: Dashboard Components
- OEE Gauge chart
- Trend line chart
- Downtime table
- Quality issues table

### PR14: Chat Console
- Message display
- Chat input
- API integration
- Conversation history

### PR15: Azure Container Apps Deployment
- Docker configuration
- GitHub Actions CI/CD
- Azure resource setup
- Environment-specific configs

---

## 12. Architecture Decisions

### Why Async/Await?
- FastAPI is ASGI-based (async by nature)
- Azure Blob Storage requires async client for efficiency
- Allows handling multiple concurrent requests

### Why Dual Storage Mode?
- **Local** (default): Faster development, no cloud credentials needed
- **Azure**: Production-ready, multi-instance compatible, durable

### Why Shared Chat Service?
- Reusable for CLI, API, and voice interfaces
- Maintains consistency across interfaces
- Single source of truth for tool calling logic

### Why Pydantic Models?
- Built-in data validation
- Type hints for IDE support
- Auto-generated API documentation
- Automatic OpenAPI schema

### Why SlowAPI Rate Limiting?
- Simple decorator-based approach
- Works with FastAPI middleware
- IP-based tracking
- No external dependencies beyond slowapi

---

## Summary

Factory Agent is a well-architected demo/prototype with:
- ✅ Fully functional FastAPI backend (Phase 1)
- ✅ Azure Blob Storage integration (Phase 2)
- ✅ Comprehensive test coverage (79+ tests)
- ✅ Production-ready security (CORS, rate limiting, input validation)
- ✅ Dual storage mode (local JSON + Azure Blob)
- ✅ Clean, documented code following best practices
- ⏳ React frontend pending (Phase 3)

The codebase is ready for React frontend development and Azure Container Apps deployment.

