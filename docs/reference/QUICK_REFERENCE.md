# Factory Agent - Quick Reference Guide

## Project Structure at a Glance

```
backend/src/api/          # FastAPI application
  ├── main.py             # FastAPI app, middleware, routes registration
  └── routes/
      ├── metrics.py      # GET /api/metrics/* endpoints
      ├── data.py         # POST /api/setup, GET /api/*, /date-range
      └── chat.py         # POST /api/chat with tool calling

shared/                   # Shared business logic (CLI + API)
  ├── config.py           # Load environment variables
  ├── models.py           # Pydantic models for validation
  ├── data.py             # Data access (sync + async versions)
  ├── metrics.py          # Metric calculations (all async)
  └── chat_service.py     # Azure OpenAI integration + tools
```

## Key Files to Know

| File | What It Does | When You Need It |
|------|---|---|
| `backend/src/api/main.py` | FastAPI app setup, CORS, rate limiting | Adding/configuring endpoints |
| `shared/config.py` | Load .env variables | Adding new config option |
| `shared/models.py` | Pydantic validation models | Changing data schema |
| `shared/data.py` | Load/save JSON data | Modifying data access |
| `shared/metrics.py` | Calculate OEE, scrap, etc. | Changing metric calculations |
| `shared/chat_service.py` | Azure OpenAI tool calling | Modifying AI behavior |

## Common Tasks

### Add New API Endpoint

1. **Create route in `backend/src/api/routes/`**:
```python
@router.get("/api/new-endpoint")
async def new_endpoint(param: str = Query(...)) -> ResponseModel:
    """Endpoint description."""
    return await some_async_function()
```

2. **Key patterns**:
   - Use `async def` for all routes
   - Use `await` for all I/O (file, API, database)
   - Return Pydantic models or HTTPException
   - Add type hints to all parameters and return

3. **Import route in `backend/src/api/main.py`**:
```python
app.include_router(new_routes.router)
```

### Add Calculation Function

1. **Add async function to `shared/metrics.py`**:
```python
async def calculate_metric(
    start_date: str,
    end_date: str
) -> MetricModel | Dict[str, str]:
    data = await load_data_async()
    if not data:
        return {"error": "No data"}
    # Calculate and return MetricModel or error dict
```

2. **Add to TOOLS in `shared/chat_service.py`** if AI should use it:
```python
{
    "type": "function",
    "function": {
        "name": "calculate_metric",
        "description": "...",
        "parameters": {...}
    }
}
```

3. **Add case to `execute_tool()` in chat_service.py**:
```python
elif tool_name == "calculate_metric":
    result = await calculate_metric(**tool_args)
```

### Add Data Model

1. **Add Pydantic model to `shared/models.py`**:
```python
from pydantic import BaseModel, Field

class NewModel(BaseModel):
    field1: str = Field(description="Field description")
    field2: int = Field(ge=0, description="Non-negative integer")
```

2. **Use in route**:
```python
@router.get("/api/endpoint")
async def endpoint() -> NewModel:
    return NewModel(field1="value", field2=42)
```

## Development Workflow

### Setup
```bash
# Clone repo and enter directory
cd factory-agent

# Install dependencies
pip install -r requirements.txt
# or
pip install -e ".[dev]"

# Create .env file from .env.example
cp .env.example .env
# Edit .env with your Azure credentials
```

### Run API
```bash
# Generate test data (one-time)
python -c "from shared.data import initialize_data; initialize_data()"

# Start API server
uvicorn backend.src.api.main:app --reload --host 0.0.0.0 --port 8000

# Access at http://localhost:8000
# Docs at http://localhost:8000/docs (Swagger)
```

### Test API
```bash
# Health check
curl http://localhost:8000/health

# Get OEE metrics
curl "http://localhost:8000/api/metrics/oee?start_date=2025-10-03&end_date=2025-11-02"

# Chat endpoint (requires AZURE_ENDPOINT and AZURE_API_KEY)
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"What is the OEE?", "history":[]}'
```

## Important Patterns

### Async/Await Rule
- **FastAPI routes**: ALWAYS `async def` with `await` for I/O
- **Metrics functions**: ALWAYS async (use `load_data_async()`)
- **Data layer**: Async and sync versions available
- **Chat service**: ALWAYS async

### Error Handling
```python
try:
    result = await some_operation()
    return result
except ValueError as e:
    raise HTTPException(status_code=400, detail=str(e))
except Exception as e:
    logger.error(f"Operation failed: {e}", exc_info=True)
    raise HTTPException(status_code=500, detail="Internal error")
```

### Type Hints Required
```python
# Good
async def process(data: Dict[str, Any]) -> ResponseModel:
    ...

# Bad (missing return type)
async def process(data: Dict[str, Any]):
    ...

# Bad (missing parameter type)
async def process(data):
    ...
```

### Request/Response Models
```python
# Define request model
class MyRequest(BaseModel):
    param1: str = Field(description="What is this?")
    param2: int = Field(ge=0, description="Must be positive")

# Use in route
@router.post("/api/endpoint")
async def endpoint(request: MyRequest) -> MyResponse:
    # FastAPI validates automatically
    return MyResponse(...)
```

## File Locations

**Where to add...**

| Item | File | Location |
|------|------|----------|
| New endpoint | `backend/src/api/routes/*.py` | Create file or add to existing |
| Calculation logic | `shared/metrics.py` | Add async function |
| Data model | `shared/models.py` | Add Pydantic class |
| Config option | `shared/config.py` | Add `VARIABLE_NAME = os.getenv("...")` |
| AI tool definition | `shared/chat_service.py` | Add to TOOLS list and execute_tool() |
| Middleware | `backend/src/api/main.py` | Use app.add_middleware() |

## Rate Limiting

**Configuration** (in `shared/config.py`):
```python
RATE_LIMIT_CHAT = os.getenv("RATE_LIMIT_CHAT", "10/minute")
RATE_LIMIT_SETUP = os.getenv("RATE_LIMIT_SETUP", "5/minute")
```

**Apply to endpoint** (in route file):
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/api/endpoint")
@limiter.limit("20/minute")
async def endpoint(request: Request, ...):
    ...
```

## CORS Configuration

**Allowed origins** (in `shared/config.py`):
```python
ALLOWED_ORIGINS = [
    "http://localhost:3000",    # Create React App
    "http://localhost:5173",    # Vite
]
```

**Change via environment variable**:
```bash
export ALLOWED_ORIGINS="http://localhost:3000,https://myapp.com"
```

## Logging

Use `logging` module (not print):
```python
import logging

logger = logging.getLogger(__name__)

logger.debug("Debug info")      # Development
logger.info("Operation complete")    # Normal flow
logger.warning("Unusual condition")  # Something odd
logger.error("Operation failed", exc_info=True)  # Error with traceback
```

## Testing

```bash
# Run all tests
pytest

# Run specific file
pytest tests/test_metrics.py

# Run with coverage
pytest --cov=shared --cov-report=html

# View coverage report
open htmlcov/index.html
```

## Environment Variables

**Required for Azure OpenAI**:
```bash
AZURE_ENDPOINT=https://your-instance.openai.azure.com/
AZURE_API_KEY=your-api-key
AZURE_DEPLOYMENT_NAME=gpt-4
AZURE_API_VERSION=2024-08-01-preview
```

**Optional**:
```bash
FACTORY_NAME=My Factory
DATA_FILE=./data/production.json
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
RATE_LIMIT_CHAT=10/minute
RATE_LIMIT_SETUP=5/minute
```

## Troubleshooting

**"No module named shared"**
- Make sure you're running from project root
- Check PYTHONPATH includes project root

**"AZURE_ENDPOINT not set"**
- Create `.env` file with Azure credentials
- See `.env.example` for template

**"No data available"**
- Run `python -c "from shared.data import initialize_data; initialize_data()"`
- This generates test data in `./data/production.json`

**Rate limit exceeded (429)**
- API is rate limited by IP address
- Wait for time window to reset
- Change limit in config or .env

**Port 8000 already in use**
- Use different port: `uvicorn backend.src.api.main:app --port 8001`
- Or kill process on port 8000

