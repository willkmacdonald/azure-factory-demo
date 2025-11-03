# Factory Agent Codebase Exploration Summary

## Executive Summary

The Factory Agent is a well-structured hybrid Python application with:
- **FastAPI backend** (`backend/src/api/`) with production-ready patterns
- **Shared business logic** (`shared/`) used by both CLI and API
- **Complete async/await implementation** for FastAPI routes
- **Azure OpenAI integration** with tool calling support
- **Security features**: CORS, rate limiting, input sanitization
- **Synthetic test data** generation with planted scenarios

The codebase is ready for FastAPI frontend development with:
- 9 REST endpoints already implemented
- 4 AI tools callable via chat endpoint
- Comprehensive Pydantic data models
- Dual sync/async data access patterns
- Full environment-based configuration

---

## Current Backend Architecture

### REST API Endpoints (9 Total)

**Metrics Endpoints** (Read-only, GET):
- `GET /api/metrics/oee` - Overall Equipment Effectiveness
- `GET /api/metrics/scrap` - Scrap and waste metrics
- `GET /api/metrics/quality` - Quality issues and defects
- `GET /api/metrics/downtime` - Downtime analysis

**Data Management** (Setup & Info, POST + GET):
- `POST /api/setup` - Generate synthetic test data (rate-limited)
- `GET /api/stats` - Data file statistics
- `GET /api/machines` - List all machines
- `GET /api/date-range` - Available data date range

**Chat/AI** (Conversational, POST):
- `POST /api/chat` - AI assistant with tool calling (rate-limited)

**Health Check**:
- `GET /health` - Service health status

### Technology Stack

| Layer | Technology | Details |
|-------|-----------|---------|
| **Web Framework** | FastAPI 0.104+ | ASGI, async/await, auto-docs |
| **Server** | Uvicorn 0.24+ | ASGI server, production-ready |
| **Data Validation** | Pydantic 2.0+ | Type-safe models, validation |
| **LLM Integration** | Azure OpenAI SDK | Tool calling, streaming support |
| **File I/O** | aiofiles 25.0+ | Async file operations |
| **Rate Limiting** | SlowAPI | IP-based request throttling |
| **Configuration** | python-dotenv | Environment variable management |
| **CLI** | Typer 0.9+ | Command-line interface (legacy) |

---

## Code Organization

### File Structure Summary

```
shared/                          [SHARED BUSINESS LOGIC]
├── config.py                    - Environment variables (8 configs)
├── models.py                    - Pydantic models (8 models)
├── data.py                      - Data access (sync + async)
├── metrics.py                   - Calculations (4 async functions)
└── chat_service.py              - LLM integration (4 tools)

backend/src/api/                 [FASTAPI APPLICATION]
├── main.py                      - App setup, middleware, registration
└── routes/
    ├── metrics.py               - 4 metric endpoints
    ├── data.py                  - 4 data management endpoints
    └── chat.py                  - 1 chat endpoint
```

### Module Dependencies

```
Minimal coupling, clean separation:
- config.py (standalone) -> loaded by all modules
- models.py (no dependencies) -> used by all modules
- data.py (uses: config) -> used by metrics, chat_service
- metrics.py (uses: data, models) -> used by chat_service, routes
- chat_service.py (uses: config, data, metrics, OpenAI SDK)
- routes/* (use: config, models, metrics, chat_service, FastAPI)
- main.py (imports all routes)
```

---

## Key Components Deep Dive

### 1. Configuration System (`shared/config.py`)

**Approach**: Environment variable-based with sensible defaults

**Key Variables**:
- `AZURE_ENDPOINT`, `AZURE_API_KEY` - LLM credentials (required)
- `AZURE_DEPLOYMENT_NAME` - Model deployment (default: "gpt-4")
- `FACTORY_NAME` - Display name (default: "Demo Factory")
- `DATA_FILE` - JSON path (default: "./data/production.json")
- `ALLOWED_ORIGINS` - CORS whitelist (default: localhost:3000, localhost:5173)
- `RATE_LIMIT_CHAT`, `RATE_LIMIT_SETUP` - Request limits

**Design**: Single import point for entire app, no hard-coded values

### 2. Data Models (`shared/models.py`)

**8 Pydantic Models with Field Validation**:

```python
OEEMetrics          # 7 fields: oee, availability, performance, quality, parts
ScrapMetrics        # 4 fields: scrap counts, rates, machine breakdown
QualityIssue        # 6 fields: type, description, affected parts, severity, date, machine
QualityIssues       # Collection: issues list + aggregated stats
DowntimeEvent       # Single event: reason, description, hours
MajorDowntimeEvent  # Events > 2 hours
DowntimeAnalysis    # Collection: events + breakdown by reason
```

**Benefits**:
- Automatic JSON serialization
- Type validation on input/output
- Auto-generated API docs
- IDE autocomplete support

### 3. Data Access Layer (`shared/data.py`)

**Dual Implementation Pattern**:
- **Sync**: For CLI tools (`load_data()`)
- **Async**: For FastAPI routes (`load_data_async()`)

**Key Functions**:
- `load_data()` / `load_data_async()` - Load JSON production data
- `save_data()` - Write data to JSON
- `initialize_data(days)` - Generate synthetic data with scenarios
- `generate_production_data(days)` - Synthetic data generator

**Synthetic Data Includes**:
- 30 days of data (configurable)
- 4 machines, 2 shifts
- Planted scenarios (quality spike, breakdown, improvement trend)
- Realistic metrics (OEE, scrap rate, downtime, defects)

### 4. Metrics Calculations (`shared/metrics.py`)

**4 Async Functions** (all use `load_data_async()`):

```python
calculate_oee()           # OEE = Availability × Performance × Quality
get_scrap_metrics()       # Scrap counts, rates, machine breakdown
get_quality_issues()      # Defects with severity, machine, date filtering
get_downtime_analysis()   # Downtime events, reasons, major incidents (>2h)
```

**Pattern**:
- All async to support FastAPI concurrent requests
- Date range aggregation (sum across days/machines)
- Optional machine name filtering
- Error handling: return `{"error": "message"}` on failure
- Pydantic validation: return typed models or error dicts

### 5. Chat Service (`shared/chat_service.py`)

**Azure OpenAI Tool Calling Integration**:

**4 AI Tools Defined**:
1. `calculate_oee` - Get OEE metrics
2. `get_scrap_metrics` - Get scrap data
3. `get_quality_issues` - Get quality defects (filters: severity, machine)
4. `get_downtime_analysis` - Get downtime events

**Key Functions**:
- `build_system_prompt()` - Dynamic prompt with factory context
- `get_chat_response()` - Tool calling loop (call LLM, execute tools, return response)
- `execute_tool()` - Execute single tool, return results
- `sanitize_user_input()` - Prevent prompt injection

**Tool Calling Loop**:
1. Send message to Azure OpenAI with available tools
2. If LLM requests tools: extract tool names and arguments
3. Execute requested tools locally
4. Send results back to LLM
5. Repeat until LLM provides final response
6. Return response + updated conversation history

### 6. FastAPI Application (`backend/src/api/main.py`)

**3 Middleware Layers**:

1. **Rate Limiting** (SlowAPI)
   - IP-based client identification
   - Per-endpoint limits (configurable)
   - Returns 429 Too Many Requests when exceeded

2. **CORS** (Cross-Origin Resource Sharing)
   - Whitelist origins (from ALLOWED_ORIGINS config)
   - Allow methods: GET, POST only
   - Allow headers: Content-Type, Authorization, X-Requested-With
   - Credentials enabled for auth headers

3. **Route Registration**
   - Include routers from metrics.py, data.py, chat.py
   - Each router has its own prefix and tags

**Health Check Endpoint**:
- Simple GET /health returning `{"status": "healthy"}`
- Used by load balancers, monitoring, container orchestration

---

## Key Patterns & Best Practices

### Async/Await Pattern (CRITICAL)

```python
# FastAPI Routes: ALL async with await for I/O
@router.get("/api/endpoint")
async def endpoint(param: str) -> Model:
    data = await load_data_async()      # REQUIRED await
    result = await metric_func()        # REQUIRED await
    return result

# Metrics Functions: ALWAYS async
async def calculate_metric(...) -> Model:
    data = await load_data_async()
    # Process and return

# Chat Service: ALWAYS async
async def get_chat_response(client: AsyncAzureOpenAI, ...):
    response = await client.chat.completions.create(...)
    ...
```

**Why**: FastAPI is ASGI-based; blocking I/O defeats concurrent request handling

### Error Handling Pattern

```python
try:
    # Attempt operation
    result = await external_io()
except ValueError as e:
    # Known error type: return specific status code
    raise HTTPException(status_code=400, detail=str(e))
except Exception as e:
    # Unknown error: log and return generic error
    logger.error(f"Operation failed: {e}", exc_info=True)
    raise HTTPException(status_code=500, detail="Internal error")
```

### Request Validation Pattern

```python
class MyRequest(BaseModel):
    message: str = Field(
        min_length=1,
        max_length=2000,
        description="User message"
    )
    history: List[Message] = Field(
        max_length=50,
        description="Conversation history"
    )
    
    @field_validator('history')
    @classmethod
    def validate_size(cls, v):
        total = sum(len(m.content) for m in v)
        if total > 50000:
            raise ValueError("History too large")
        return v
```

### Dependency Injection Pattern

```python
async def get_openai_client() -> AsyncAzureOpenAI:
    # Validate configuration
    if not AZURE_ENDPOINT:
        raise HTTPException(status_code=500, detail="Not configured")
    # Create and return client
    return AsyncAzureOpenAI(...)

@router.post("/api/chat")
async def chat(
    client: AsyncAzureOpenAI = Depends(get_openai_client)
):
    # Client injected automatically
    ...
```

---

## Current State Assessment

### Strengths
1. **Complete API Implementation** - 9 endpoints with proper patterns
2. **Production-Ready Security** - CORS, rate limiting, input validation
3. **Async Throughout** - Proper async/await for concurrent handling
4. **Clean Architecture** - Clear separation of concerns
5. **Reusable Code** - Shared logic between CLI and API
6. **Type Safety** - Complete type hints, Pydantic validation
7. **Documentation** - Comprehensive docstrings, auto-generated API docs

### Areas for Enhancement
1. **Missing SlowAPI in pyproject.toml** - Add `slowapi>=0.1.9`
2. **No database** - Using JSON files (acceptable for demo)
3. **No authentication** - Public endpoints (ready for Azure AD integration)
4. **Limited monitoring** - No logging aggregation (basic logging in place)
5. **No API versioning** - Single version (acceptable for demo)

### Ready For
- React/Vue/Angular frontend development
- Azure Container Apps deployment
- Production monitoring integration
- Frontend auth integration (Azure AD)

---

## Files for FastAPI Implementation

### Must-Know Files

| Rank | File | Lines | Purpose |
|------|------|-------|---------|
| 1 | `backend/src/api/main.py` | 177 | App initialization |
| 2 | `shared/models.py` | 86 | Data models |
| 3 | `shared/config.py` | 33 | Configuration |
| 4 | `backend/src/api/routes/metrics.py` | 129 | Metric endpoints |
| 5 | `backend/src/api/routes/chat.py` | 212 | Chat endpoint |
| 6 | `backend/src/api/routes/data.py` | 381 | Data endpoints |
| 7 | `shared/metrics.py` | 285 | Calculations |
| 8 | `shared/data.py` | 283 | Data access |
| 9 | `shared/chat_service.py` | 368 | LLM integration |

**Total lines of production code**: ~1,954 lines (very manageable)

---

## Quick Start Guide

### 1. Environment Setup
```bash
cp .env.example .env
# Edit .env with:
# AZURE_ENDPOINT=https://your-instance.openai.azure.com/
# AZURE_API_KEY=your-api-key
```

### 2. Generate Test Data
```bash
python -c "from shared.data import initialize_data; initialize_data()"
```

### 3. Run API
```bash
uvicorn backend.src.api.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Access Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health: http://localhost:8000/health

### 5. Test Endpoints
```bash
# Metrics
curl "http://localhost:8000/api/metrics/oee?start_date=2025-10-03&end_date=2025-11-02"

# Chat (requires Azure credentials)
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"What is the OEE?","history":[]}'
```

---

## Summary

The Factory Agent backend is a **production-ready FastAPI application** with:
- Clean, maintainable code structure
- Proper async/await patterns throughout
- Comprehensive error handling and validation
- Security features (CORS, rate limiting, input sanitization)
- Complete Azure OpenAI integration with tool calling
- Synthetic test data with realistic scenarios
- Auto-generated API documentation

You're ready to implement:
1. A React/Vue frontend connecting to these endpoints
2. Azure AD authentication
3. Advanced monitoring and logging
4. Database persistence (replace JSON)
5. Additional metrics and calculations

All endpoints follow consistent patterns, making it easy to extend with new functionality.

