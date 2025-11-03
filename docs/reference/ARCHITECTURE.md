# Factory Agent Backend Architecture Summary

## Project Overview
Factory Agent is a hybrid Python project with:
- **CLI Interface**: Typer-based command-line tool for setup, chat, and voice commands
- **Web API**: FastAPI-based REST API for browser/frontend integration
- **Shared Logic**: Common modules used by both CLI and API (metrics, data, models, chat service)
- **Async/Sync Pattern**: Async for FastAPI, sync for CLI, dual implementations where needed

---

## Directory Structure

```
factory-agent/
├── backend/
│   └── src/
│       ├── api/
│       │   ├── main.py              # FastAPI app initialization, CORS, rate limiting
│       │   └── routes/
│       │       ├── metrics.py        # Metrics endpoints (OEE, scrap, quality, downtime)
│       │       ├── chat.py           # Chat endpoint with tool calling
│       │       └── data.py           # Data management endpoints (setup, stats, machines)
│       └── __init__.py
├── shared/                           # Core business logic (CLI + API)
│   ├── config.py                     # Configuration management (env vars)
│   ├── models.py                     # Pydantic data models
│   ├── data.py                       # Data access layer (sync + async)
│   ├── metrics.py                    # Metrics calculations (async for API use)
│   ├── chat_service.py               # Azure OpenAI integration, tool calling
│   └── __init__.py
├── src/                              # CLI tools (legacy, not used for API)
│   ├── main.py                       # Typer CLI entry point
│   ├── dashboard.py                  # Streamlit UI (legacy)
│   └── metrics_sync.py               # Sync metrics wrapper
├── data/
│   └── production.json               # Demo production data (generated)
├── tests/
│   ├── test_config.py
│   ├── test_chat_service.py
│   └── __init__.py
├── requirements.txt                  # Dependencies (legacy)
└── pyproject.toml                    # Modern project configuration
```

---

## Key Components

### 1. Configuration Management (`shared/config.py`)

**Purpose**: Load environment variables and provide application configuration

**Key Variables**:
- `AZURE_ENDPOINT`: Azure OpenAI endpoint URL
- `AZURE_API_KEY`: Azure OpenAI API key
- `AZURE_DEPLOYMENT_NAME`: Model deployment name (default: "gpt-4")
- `FACTORY_NAME`: Factory display name (default: "Demo Factory")
- `DATA_FILE`: Path to production data JSON (default: "./data/production.json")
- `ALLOWED_ORIGINS`: CORS allowed origins (env var or default localhost:3000, localhost:5173)
- `RATE_LIMIT_CHAT`: Rate limit for chat endpoint (default: "10/minute")
- `RATE_LIMIT_SETUP`: Rate limit for setup endpoint (default: "5/minute")

**Pattern**: Uses `python-dotenv` to load `.env` file at module import time

---

### 2. Data Models (`shared/models.py`)

**Pydantic Models** (all with field validation):

**OEEMetrics**
- `oee`: float (0-1) - Overall Equipment Effectiveness
- `availability`: float (0-1) - Machine uptime ratio
- `performance`: float (0-1) - Performance efficiency
- `quality`: float (0-1) - Quality component
- `total_parts`: int - Total parts produced
- `good_parts`: int - Parts meeting quality standards
- `scrap_parts`: int - Defective parts

**ScrapMetrics**
- `total_scrap`: int
- `total_parts`: int
- `scrap_rate`: float (percentage)
- `scrap_by_machine`: Dict[str, int] (optional, only when not filtered by machine)

**QualityIssue** (single issue)
- `type`: str - Defect type
- `description`: str
- `parts_affected`: int
- `severity`: str (Low, Medium, High)
- `date`: str (YYYY-MM-DD)
- `machine`: str

**QualityIssues** (collection with stats)
- `issues`: List[QualityIssue]
- `total_issues`: int
- `total_parts_affected`: int
- `severity_breakdown`: Dict[str, int]

**DowntimeAnalysis**
- `total_downtime_hours`: float
- `downtime_by_reason`: Dict[str, float]
- `major_events`: List[MajorDowntimeEvent] (>2 hours)

---

### 3. Data Access Layer (`shared/data.py`)

**Purpose**: Load/save JSON production data, generate synthetic test data

**Key Functions**:

```python
# Sync functions (CLI use)
def load_data() -> Optional[Dict[str, Any]]
def save_data(data: Dict[str, Any]) -> None
def data_exists() -> bool
def initialize_data(days: int = 30) -> Dict[str, Any]
def generate_production_data(days: int = 30) -> Dict[str, Any]

# Async functions (FastAPI use)
async def load_data_async() -> Optional[Dict[str, Any]]
```

**Data Constants**:
- `MACHINES`: List of 4 machines (CNC-001, Assembly-001, Packaging-001, Testing-001)
- `SHIFTS`: Day (6am-2pm) and Night (2pm-10pm)
- `DEFECT_TYPES`: Dictionary of defect categories with severity
- `DOWNTIME_REASONS`: Dictionary of downtime reason codes

**Data Structure** (JSON):
```json
{
  "generated_at": "2025-11-02T...",
  "start_date": "2025-10-03T...",
  "end_date": "2025-11-02T...",
  "machines": [...],
  "shifts": [...],
  "production": {
    "2025-10-03": {
      "CNC-001": {
        "parts_produced": 850,
        "good_parts": 825,
        "scrap_parts": 25,
        "scrap_rate": 2.94,
        "uptime_hours": 15.8,
        "downtime_hours": 0.2,
        "downtime_events": [...],
        "quality_issues": [...],
        "shifts": {...}
      },
      ...
    }
  }
}
```

**Synthetic Data Scenarios**:
- Day 15, Assembly-001: Quality spike (12% defect rate)
- Day 22, Packaging-001: Major breakdown (4 hours downtime)
- Performance improvement: 65% → 80% OEE over 30 days
- Night shift: 5-8% lower performance than day shift

---

### 4. Metrics Calculations (`shared/metrics.py`)

**Purpose**: Calculate factory metrics from production data (async for FastAPI)

**Key Functions** (all async, all use `load_data_async()`):

```python
async def calculate_oee(
    start_date: str,
    end_date: str,
    machine_name: Optional[str] = None
) -> OEEMetrics | Dict[str, str]

async def get_scrap_metrics(
    start_date: str,
    end_date: str,
    machine_name: Optional[str] = None
) -> ScrapMetrics | Dict[str, str]

async def get_quality_issues(
    start_date: str,
    end_date: str,
    severity: Optional[str] = None,
    machine_name: Optional[str] = None
) -> QualityIssues | Dict[str, str]

async def get_downtime_analysis(
    start_date: str,
    end_date: str,
    machine_name: Optional[str] = None
) -> DowntimeAnalysis | Dict[str, str]

def get_date_range(start_date: str, end_date: str) -> List[str]
```

**Key Patterns**:
- Date aggregation: Iterate over date range, sum metrics for all machines/dates
- Machine filtering: Optional parameter filters to single machine
- Pydantic validation: Returns typed Pydantic models or error dicts
- Error handling: Returns `{"error": "message"}` for invalid inputs

---

### 5. Chat Service (`shared/chat_service.py`)

**Purpose**: Azure OpenAI integration with tool calling for both CLI and API

**Key Features**:
- **Tool Calling**: Defines 4 tools (OEE, scrap, quality, downtime)
- **System Prompt**: Built dynamically with factory context, date range, machine list
- **Input Sanitization**: Prevents prompt injection attacks
- **Tool Execution**: `execute_tool()` function calls metric functions
- **Conversation Management**: Returns updated history for multi-turn conversations

**Main Functions**:

```python
async def build_system_prompt() -> str
    # Builds context prompt with factory data and machine list

async def get_chat_response(
    client: AsyncAzureOpenAI,
    system_prompt: str,
    conversation_history: List[Dict[str, Any]],
    user_message: str
) -> Tuple[str, List[Dict[str, Any]]]
    # Tool calling loop: call LLM, execute tools, return response + history

async def execute_tool(tool_name: str, tool_args: Dict[str, Any]) -> Dict[str, Any]
    # Execute one tool function, return results as dict

def sanitize_user_input(user_message: str) -> str
    # Prevent prompt injection attacks
```

**Tool Definitions**:
- `calculate_oee`: Get OEE metrics for date range
- `get_scrap_metrics`: Get scrap metrics
- `get_quality_issues`: Get quality defects (with optional severity/machine filters)
- `get_downtime_analysis`: Get downtime events

---

### 6. FastAPI Application (`backend/src/api/main.py`)

**Purpose**: Initialize FastAPI app, configure middleware, register routes

**Key Components**:

**Rate Limiting** (via SlowAPI):
- `Limiter` instance with IP-based key function
- Exception handler for 429 Too Many Requests responses
- Per-endpoint limits via `@limiter.limit()` decorator

**CORS Middleware** (PR7 security hardening):
- Origins: From `ALLOWED_ORIGINS` config (not wildcard)
- Methods: GET, POST only (not PUT/DELETE/PATCH)
- Headers: Specific list, not wildcard
- Credentials: True (allows auth headers)

**Routes** (registered via include_router):
- `/api/metrics/*`: OEE, scrap, quality, downtime
- `/api/*`: Setup, stats, machines, date-range, chat
- `/health`: Health check endpoint

**Endpoints**:
```python
GET  /health                          # Simple status check
GET  /api/metrics/oee                # OEE metrics
GET  /api/metrics/scrap              # Scrap metrics
GET  /api/metrics/quality            # Quality issues
GET  /api/metrics/downtime           # Downtime analysis
POST /api/setup                      # Generate data (rate-limited)
GET  /api/stats                      # Data statistics
GET  /api/machines                   # List machines
GET  /api/date-range                 # Data date range
POST /api/chat                       # Chat with AI (rate-limited)
```

---

### 7. Routes Implementation

#### **Metrics Routes** (`backend/src/api/routes/metrics.py`)

```python
@router.get("/api/metrics/oee")
async def get_oee(
    start_date: str = Query(...),
    end_date: str = Query(...),
    machine: Optional[str] = Query(None)
) -> Union[OEEMetrics, Dict[str, str]]

@router.get("/api/metrics/scrap")
async def get_scrap(...)

@router.get("/api/metrics/quality")
async def get_quality(...)

@router.get("/api/metrics/downtime")
async def get_downtime(...)
```

**Pattern**: Simple wrapper around async metrics functions from `shared.metrics`

#### **Data Routes** (`backend/src/api/routes/data.py`)

```python
@router.post("/api/setup")
@limiter.limit(RATE_LIMIT_SETUP)
async def setup_data(request: Request, setup_request: SetupRequest)
    # Generate synthetic data, return metadata

@router.get("/api/stats")
async def get_stats()
    # Return data statistics (date range, record counts)

@router.get("/api/machines")
async def get_machines()
    # Return list of machines

@router.get("/api/date-range")
async def get_date_range()
    # Return available data date range
```

**Models**:
- `SetupRequest`: `days: int = 30`
- `SetupResponse`: metadata about generated data
- `StatsResponse`: exists, start_date, end_date, total_days, total_machines, total_records
- `MachineInfo`: id, name, type, ideal_cycle_time
- `DateRangeResponse`: start_date, end_date, total_days

#### **Chat Routes** (`backend/src/api/routes/chat.py`)

```python
@router.post("/api/chat")
@limiter.limit(RATE_LIMIT_CHAT)
async def chat(
    request: Request,
    chat_request: ChatRequest,
    client: AsyncAzureOpenAI = Depends(get_openai_client)
) -> ChatResponse
```

**Request/Response Models**:
- `ChatMessage`: role, content (with max_length validation)
- `ChatRequest`: message, history (with validator for total size)
- `ChatResponse`: response, history

**Key Features**:
- Dependency injection for Azure OpenAI client
- Request validation with Pydantic validators
- Rate limiting for abuse prevention
- Structured logging with request IDs
- Timing information in logs
- Complete error handling (RuntimeError, HTTPException)

---

## Async/Sync Patterns

### FastAPI Routes (ASYNC - REQUIRED)
```python
# metrics.py
async def calculate_oee(...) -> OEEMetrics
    data = await load_data_async()  # Async file I/O
    
# metrics.py
async def get_scrap_metrics(...) -> ScrapMetrics
    data = await load_data_async()  # Async file I/O

# chat.py
async def chat(...):
    client = await get_openai_client()  # Dependency injection
    response = await client.chat.completions.create(...)  # Async API call
```

### Data Layer (BOTH - Dual Implementation)
```python
# Sync version for CLI
def load_data() -> Optional[Dict[str, Any]]:
    with open(path, "r") as f:
        return json.load(f)

# Async version for FastAPI
async def load_data_async() -> Optional[Dict[str, Any]]:
    async with aiofiles.open(path, "r") as f:
        content = await f.read()
        return json.loads(content)
```

### Chat Service (ASYNC - Shared by API)
```python
async def build_system_prompt() -> str
async def execute_tool(tool_name: str, tool_args: Dict[str, Any])
async def get_chat_response(client: AsyncAzureOpenAI, ...)
```

---

## Key Architecture Patterns

### 1. **Dependency Injection** (FastAPI)
```python
async def get_openai_client() -> AsyncAzureOpenAI:
    if not AZURE_ENDPOINT:
        raise HTTPException(status_code=500, detail="...")
    return AsyncAzureOpenAI(...)

@router.post("/api/chat")
async def chat(client: AsyncAzureOpenAI = Depends(get_openai_client)):
    ...
```

### 2. **Rate Limiting** (SlowAPI)
```python
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@router.post("/api/chat")
@limiter.limit("10/minute")
async def chat(request: Request, ...):
    ...
```

### 3. **Request Validation** (Pydantic)
```python
class ChatRequest(BaseModel):
    message: str = Field(max_length=2000, min_length=1)
    history: List[ChatMessage] = Field(max_length=50)
    
    @field_validator('history')
    @classmethod
    def validate_total_history_size(cls, v):
        total_chars = sum(len(msg.content) for msg in v)
        if total_chars > 50000:
            raise ValueError("Total history too large")
        return v
```

### 4. **Error Handling**
```python
try:
    result = await metric_function(...)
    return result
except RuntimeError as e:
    raise HTTPException(status_code=400, detail=str(e))
except Exception as e:
    logger.error(f"Error: {e}", exc_info=True)
    raise HTTPException(status_code=500, detail="Internal server error")
```

### 5. **Tool Calling Pattern** (Azure OpenAI)
```python
while True:
    response = await client.chat.completions.create(
        model=AZURE_DEPLOYMENT_NAME,
        messages=messages,
        tools=TOOLS,
        tool_choice="auto"
    )
    
    if not response.choices[0].message.tool_calls:
        break  # Final response, no more tools to call
    
    for tool_call in response.choices[0].message.tool_calls:
        result = await execute_tool(tool_call.function.name, ...)
        messages.append({"role": "tool", "content": json.dumps(result)})
```

---

## Dependencies

**Core**:
- `fastapi>=0.104.0` - Web framework
- `uvicorn>=0.24.0` - ASGI server
- `pydantic>=2.0.0` - Data validation
- `openai>=1.0.0` - Azure OpenAI client
- `python-dotenv>=1.0.0` - Environment variables
- `typer>=0.9.0` - CLI framework
- `rich>=13.0.0` - Terminal output

**Additional**:
- `aiofiles>=25.0.0` - Async file I/O
- `azure-storage-blob>=12.19.0` - Azure storage (future)
- `slowapi` - Rate limiting (in requirements.txt as slowapi, installed with PyPI)
- `pytest>=7.4.0` - Testing

**Missing in pyproject.toml**: `slowapi` for rate limiting (used in code but not listed)

---

## Common Issues & Considerations

### 1. Missing SlowAPI Dependency
**Issue**: `slowapi` is used in `backend/src/api/main.py` but not listed in `pyproject.toml`
**Solution**: Add `slowapi>=0.1.9` to dependencies

### 2. Async/Sync Consistency
**Pattern**: 
- FastAPI routes MUST be `async def` with `await` for all I/O
- Metrics functions are `async def` to support API routes
- Data layer has both sync (CLI) and async (API) implementations
- Chat service is fully async

### 3. Error Handling
**Pattern**: All external I/O (API calls, file reads) must have try/except
- Metrics functions return `Dict[str, str]` with error key on failure
- Chat/data routes use HTTPException with appropriate status codes
- All errors are logged with context

### 4. Type Hints
**Pattern**: Complete type hints on all functions
- Parameter types and return types required
- Union types for error cases (e.g., `Union[OEEMetrics, Dict[str, str]]`)
- Pydantic models for all request/response bodies

---

## File Dependencies

```
FastAPI Routes (backend/src/api/routes/)
    ├── Imports: shared.metrics, shared.models, shared.config
    └── Imports: FastAPI, Pydantic, SlowAPI

Main App (backend/src/api/main.py)
    ├── Imports: All routes
    ├── Imports: shared.config
    └── Imports: FastAPI middleware components

Shared Modules (shared/)
    ├── metrics.py imports: data.py, models.py
    ├── data.py imports: config.py
    ├── chat_service.py imports: config.py, data.py, metrics.py, OpenAI
    └── config.py imports: dotenv (standalone, no inter-dependencies)

Models (shared/models.py)
    └── No internal dependencies (only Pydantic)
```

---

## To Run FastAPI Locally

```bash
# Install dependencies
pip install -r requirements.txt  # or: pip install -e ".[dev]"

# Generate data
python -c "from shared.data import initialize_data; initialize_data()"

# Run API server
uvicorn backend.src.api.main:app --reload --host 0.0.0.0 --port 8000

# Access API
curl http://localhost:8000/health
curl http://localhost:8000/api/metrics/oee?start_date=2025-10-03&end_date=2025-11-02
```

---

## Key Files for FastAPI Implementation

| File | Purpose | Key Content |
|------|---------|-------------|
| `backend/src/api/main.py` | App initialization | FastAPI instance, CORS, rate limiting, health check |
| `backend/src/api/routes/metrics.py` | Metric endpoints | OEE, scrap, quality, downtime GET endpoints |
| `backend/src/api/routes/data.py` | Data endpoints | Setup, stats, machines, date-range |
| `backend/src/api/routes/chat.py` | Chat endpoint | POST /api/chat with tool calling |
| `shared/config.py` | Configuration | Env vars, rate limits, CORS origins |
| `shared/models.py` | Pydantic models | Data validation for requests/responses |
| `shared/data.py` | Data layer | Dual sync/async functions, CRUD operations |
| `shared/metrics.py` | Business logic | Async calculations (OEE, scrap, etc.) |
| `shared/chat_service.py` | LLM integration | Tool definitions, prompt building, tool calling |

