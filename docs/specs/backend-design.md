# Backend Architecture Design Specification

**Created**: 2026-01-21
**Status**: Current (Phase 6 Complete)
**Version**: 1.0

---

## Executive Summary

The Factory Agent backend is a FastAPI application providing REST APIs for factory operations monitoring, AI-powered analytics, and supply chain traceability. It integrates with Azure OpenAI, Blob Storage, AD authentication, and Key Vault for a complete enterprise solution.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Azure Container Apps                               │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                        FastAPI Application                             │  │
│  │                                                                        │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │  │
│  │  │   Metrics   │  │    Chat     │  │    Data     │  │  Traceability│  │  │
│  │  │   Router    │  │   Router    │  │   Router    │  │    Router   │  │  │
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  │  │
│  │         │                │                │                │         │  │
│  │         └────────────────┴────────────────┴────────────────┘         │  │
│  │                                   │                                   │  │
│  │  ┌────────────────────────────────┴────────────────────────────────┐ │  │
│  │  │                     Shared Modules Layer                         │ │  │
│  │  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐│ │  │
│  │  │  │ models.py│ │metrics.py│ │ data.py  │ │chat_svc  │ │memory  ││ │  │
│  │  │  │ (Pydantic│ │(Analytics│ │(Data     │ │(Azure    │ │_svc    ││ │  │
│  │  │  │  Models) │ │ Engine)  │ │ Access)  │ │ OpenAI)  │ │        ││ │  │
│  │  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └────────┘│ │  │
│  │  └────────────────────────────────────────────────────────────────┘ │  │
│  │                                   │                                  │  │
│  │  ┌────────────────────────────────┴────────────────────────────────┐│  │
│  │  │                    Infrastructure Layer                          ││  │
│  │  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  ││  │
│  │  │  │ blob_storage │  │   config.py  │  │       auth.py        │  ││  │
│  │  │  │   (Azure)    │  │  (Settings)  │  │   (Azure AD JWT)     │  ││  │
│  │  │  └──────────────┘  └──────────────┘  └──────────────────────┘  ││  │
│  │  └─────────────────────────────────────────────────────────────────┘│  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                    │                │                │
                    ▼                ▼                ▼
         ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
         │ Azure OpenAI │  │  Azure Blob  │  │  Azure Key   │
         │   Service    │  │   Storage    │  │    Vault     │
         └──────────────┘  └──────────────┘  └──────────────┘
```

---

## Technology Stack

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Framework** | FastAPI | 0.115.x | Async REST API |
| **Server** | Uvicorn | 0.32.x | ASGI web server |
| **Validation** | Pydantic | 2.10.x | Data models & validation |
| **Rate Limiting** | SlowAPI | 0.1.x | Request throttling |
| **AI/LLM** | Azure OpenAI | SDK 1.51+ | Chat with tool calling |
| **Storage** | Azure Blob Storage | SDK 12.15+ | Persistent data |
| **Auth** | Azure AD + JWT | python-jose | Token validation |
| **Secrets** | Azure Key Vault | SDK latest | Credential management |
| **Runtime** | Python | 3.11 | Language runtime |

---

## API Endpoints

### Endpoint Summary

| Category | Endpoints | Auth Required | Rate Limit |
|----------|-----------|---------------|------------|
| **Metrics** | 4 | No | 100/min |
| **Chat** | 2 | Conditional | 10/min |
| **Data** | 4 | Conditional (POST) | 5/min (POST) |
| **Traceability** | 9 | No | None |
| **Memory** | 4 | No | None |
| **Health** | 1 | No | None |

**Total: 24 endpoints**

---

### Metrics Endpoints (`/api/metrics/`)

| Method | Path | Description | Parameters |
|--------|------|-------------|------------|
| GET | `/oee` | Overall Equipment Effectiveness | `start_date`, `end_date`, `machine?` |
| GET | `/scrap` | Scrap/waste metrics | `start_date`, `end_date`, `machine?` |
| GET | `/quality` | Quality issues list | `start_date`, `end_date`, `severity?`, `machine?` |
| GET | `/downtime` | Downtime analysis | `start_date`, `end_date`, `machine?` |

**OEE Calculation:**
```
OEE = Availability × Performance × Quality

Availability = Uptime Hours / Total Hours
Performance  = OEE_PERFORMANCE_FACTOR (configurable, default 0.95)
Quality      = Good Parts / Total Parts
```

---

### Chat Endpoints (`/api/chat`)

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | `/chat` | Synchronous chat | Conditional |
| POST | `/chat/stream` | Streaming chat (SSE) | Conditional |

**Tool Calling:**

The AI can call these tools to retrieve factory data:

| Tool | Purpose | Parameters |
|------|---------|------------|
| `get_oee_metrics` | Get OEE data | start_date, end_date, machine? |
| `get_scrap_metrics` | Get scrap data | start_date, end_date, machine? |
| `get_quality_issues` | Get quality issues | start_date, end_date, severity?, machine? |
| `get_downtime_analysis` | Get downtime data | start_date, end_date, machine? |
| `save_investigation` | Create investigation | title, observation, machine_id?, supplier_id? |
| `log_action` | Log action taken | description, action_type, baseline_metrics |
| `get_pending_followups` | Get due follow-ups | None |
| `get_memory_context` | Get relevant memory | machine_id?, supplier_id? |

---

### Data Endpoints (`/api/`)

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | `/setup` | Generate synthetic data | Conditional |
| GET | `/stats` | Data statistics | No |
| GET | `/machines` | List machines | No |
| GET | `/date-range` | Available date range | No |

---

### Traceability Endpoints (`/api/`)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/suppliers` | List all suppliers |
| GET | `/suppliers/{id}` | Supplier details |
| GET | `/suppliers/{id}/impact` | Supplier quality impact |
| GET | `/batches` | List production batches |
| GET | `/batches/{batch_id}` | Batch details |
| GET | `/traceability/backward/{batch_id}` | Trace batch → materials → suppliers |
| GET | `/traceability/forward/{supplier_id}` | Trace supplier → batches → orders |
| GET | `/orders` | List customer orders |
| GET | `/orders/{order_id}` | Order details |

---

### Memory Endpoints (`/api/memory/`)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/summary` | Memory statistics |
| GET | `/investigations` | List investigations (filterable) |
| GET | `/actions` | List logged actions |
| GET | `/shift-summary` | Shift handoff summary |

---

## Data Models

### Core Production Models

```python
Machine:
  id: int
  name: str (e.g., "CNC-001")
  type: str (e.g., "CNC Machining Center")
  ideal_cycle_time: int (seconds)

ProductionRecord:
  date: str
  machine: str
  shift: int
  parts_produced: int
  good_parts: int
  scrap_parts: int
  downtime_hours: float
  downtime_reason: str
  quality_issues: List[QualityIssue]
```

### Supply Chain Models

```python
Supplier:
  id: str (SUP-001)
  name: str
  type: str
  materials_supplied: List[str]
  quality_metrics: {quality_rating, on_time_delivery_rate, defect_rate}
  status: str (Active, OnHold, Suspended)

MaterialLot:
  lot_number: str (LOT-20240115-001)
  material_id: str
  supplier_id: str
  quantity_received: float
  quantity_remaining: float
  status: str (Available, InUse, Depleted, Quarantine, Rejected)

ProductionBatch:
  batch_id: str (BATCH-20240115-CNC001-001)
  date: str
  machine_id: int
  order_id: Optional[str]
  parts_produced: int
  materials_consumed: List[MaterialUsage]  # Full traceability
  quality_issues: List[QualityIssue]
```

### Memory Models

```python
Investigation:
  id: str (INV-20241126-001)
  title: str
  machine_id: Optional[str]
  supplier_id: Optional[str]
  status: Literal["open", "in_progress", "resolved", "closed"]
  initial_observation: str
  findings: List[str]
  created_at: str

Action:
  id: str (ACT-20241126-001)
  description: str
  action_type: Literal["parameter_change", "maintenance", "process_change"]
  baseline_metrics: Dict[str, float]
  expected_impact: str
  actual_impact: Optional[str]
  follow_up_date: Optional[str]
```

---

## Security Architecture

### Authentication Flow

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  Client  │────▶│  FastAPI │────▶│  auth.py │────▶│ Azure AD │
│          │     │          │     │          │     │  (JWKS)  │
└──────────┘     └──────────┘     └──────────┘     └──────────┘
     │                │                │                │
     │ Authorization: │                │                │
     │ Bearer <token> │                │                │
     │                │  1. Extract    │                │
     │                │     token      │                │
     │                │                │  2. Fetch      │
     │                │                │     public keys│
     │                │                │◀───────────────│
     │                │  3. Validate   │                │
     │                │     signature  │                │
     │                │  4. Verify     │                │
     │                │     claims     │                │
     │◀───────────────│  5. Return     │                │
     │   Response     │     user info  │                │
     │                │                │                │
```

### Conditional Authentication

```python
REQUIRE_AUTH=false (Demo Mode)
├─ GET endpoints: Public
├─ POST endpoints: Optional token (demo user if absent)
└─ Returns: current_user=None or demo user

REQUIRE_AUTH=true (Production Mode)
├─ GET endpoints: Public
├─ POST endpoints: Require valid Azure AD JWT
└─ Returns: 401 Unauthorized if token missing/invalid
```

### Security Layers

| Layer | Implementation | Purpose |
|-------|---------------|---------|
| **Rate Limiting** | SlowAPI middleware | Prevent abuse |
| **CORS** | Restricted origins | Cross-origin protection |
| **Security Headers** | Custom middleware | OWASP compliance |
| **Input Validation** | Pydantic models | Prevent injection |
| **Prompt Sanitization** | Pattern detection | Prompt injection defense |
| **Secrets Management** | Azure Key Vault | Secure credentials |

### Security Headers (OWASP)

| Header | Value | Purpose |
|--------|-------|---------|
| X-Content-Type-Options | nosniff | Prevent MIME sniffing |
| X-Frame-Options | DENY | Prevent clickjacking |
| X-XSS-Protection | 1; mode=block | Legacy XSS filter |
| Referrer-Policy | strict-origin-when-cross-origin | Control referrer |

---

## Configuration Management

### Environment Variables

```bash
# Azure OpenAI
AZURE_ENDPOINT=https://<resource>.openai.azure.com/
AZURE_API_KEY=<key>
AZURE_DEPLOYMENT_NAME=gpt-4o
AZURE_API_VERSION=2024-08-01-preview

# Azure Storage
STORAGE_MODE=azure|local
AZURE_STORAGE_CONNECTION_STRING=<connection-string>
AZURE_BLOB_CONTAINER=factory-data
AZURE_BLOB_NAME=production.json

# Azure Key Vault
KEYVAULT_URL=https://<vault>.vault.azure.net/

# Authentication
AZURE_AD_TENANT_ID=<tenant-id>
AZURE_AD_CLIENT_ID=<client-id>
REQUIRE_AUTH=true|false

# Security
PROMPT_INJECTION_MODE=log|block
ALLOWED_ORIGINS=https://yourdomain.com

# Application
DEBUG=true|false
FACTORY_NAME=Demo Factory
OEE_PERFORMANCE_FACTOR=0.95
```

### Configuration Priority

```
1. Azure Key Vault (if KEYVAULT_URL set)
   ↓
2. Environment Variables (.env file)
   ↓
3. Default Values (built-in)
```

---

## Data Storage

### Storage Modes

| Mode | Storage | Use Case |
|------|---------|----------|
| `local` | `./data/production.json` | Local development |
| `azure` | Azure Blob Storage | Production |

### Blob Storage Configuration

```python
Container: factory-data
Blobs:
├─ production.json  # Main production data (~2-5MB)
└─ memory.json      # Agent memory (~100KB)

Retry Policy:
├─ Strategy: Exponential backoff
├─ Attempts: 3
├─ Delays: 2s → 4s → 8s
└─ Total: ~14s max

Timeouts:
├─ Connection: 30 seconds
└─ Operation: 60 seconds
```

---

## Middleware Stack

```
Request
  ↓
┌─────────────────────────────┐
│ 1. Rate Limiting (SlowAPI)  │  Check request count per IP
└─────────────────────────────┘
  ↓
┌─────────────────────────────┐
│ 2. Security Headers         │  Add OWASP headers
└─────────────────────────────┘
  ↓
┌─────────────────────────────┐
│ 3. CORS                     │  Validate origin
└─────────────────────────────┘
  ↓
┌─────────────────────────────┐
│ 4. Route Handler            │  Process request
└─────────────────────────────┘
  ↓
Response (with X-Process-Time header)
```

---

## Deployment

### Docker Container

```dockerfile
# Multi-stage build for minimal image size
FROM python:3.11-slim AS builder
# Install build dependencies, compile wheels

FROM python:3.11-slim AS runtime
# Copy only runtime dependencies
# Copy application code
EXPOSE 8000
HEALTHCHECK GET /health
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Azure Container Apps

```yaml
Container:
  image: <acr>.azurecr.io/factory-agent/backend:latest
  port: 8000
  cpu: 0.5
  memory: 1.0Gi

Scaling:
  minReplicas: 0
  maxReplicas: 5
  rules:
    - type: http
      metadata:
        concurrentRequests: 10

Health:
  liveness: GET /health (30s interval)
  readiness: GET /health (10s interval)
```

### CI/CD Pipeline

```
Push to main
  ↓
Run tests (pytest)
  ↓
Build Docker image
  ↓
Push to Azure Container Registry
  ↓
Deploy to Azure Container Apps
  ↓
Run smoke tests (/health, /api/stats)
```

---

## File Structure

```
backend/
├── src/
│   └── api/
│       ├── main.py           # FastAPI app entry point
│       ├── auth.py           # Azure AD JWT validation
│       └── routes/
│           ├── metrics.py    # /api/metrics/* endpoints
│           ├── chat.py       # /api/chat endpoints
│           ├── data.py       # /api/setup, /api/stats
│           ├── traceability.py  # Supply chain endpoints
│           └── memory.py     # /api/memory/* endpoints
├── tests/                    # pytest test suite
├── requirements.txt          # Python dependencies
└── Dockerfile                # Container build

shared/
├── models.py                 # Pydantic data models
├── config.py                 # Configuration management
├── data.py                   # Data access layer
├── metrics.py                # Analytics calculations
├── chat_service.py           # Azure OpenAI integration
├── memory_service.py         # Investigation/action memory
└── blob_storage.py           # Azure Blob client
```

---

## Error Handling

### HTTP Status Codes

| Code | Meaning | When Used |
|------|---------|-----------|
| 200 | OK | Successful request |
| 400 | Bad Request | Invalid parameters |
| 401 | Unauthorized | Missing/invalid auth token |
| 403 | Forbidden | CORS violation |
| 404 | Not Found | Resource doesn't exist |
| 422 | Unprocessable Entity | Validation error |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Unexpected error |

### Error Response Format

```json
{
  "detail": "Error message here"
}
```

### Debug Mode

| DEBUG | Behavior |
|-------|----------|
| `true` | Full stack traces, detailed errors |
| `false` | Generic error messages, no traces |

---

## Monitoring

### Health Check

```
GET /health
Response: {"status": "healthy"}

Used by:
- Container Apps health probes
- Load balancers
- Uptime monitors
```

### Observability

| Type | Implementation |
|------|----------------|
| **Logging** | Python logging module (structured) |
| **Metrics** | X-Process-Time header |
| **Tracing** | Request ID in logs |

### Key Metrics to Monitor

- Request count by endpoint
- Response time (p50, p95, p99)
- Error rate (4xx, 5xx)
- Rate limit hits (429)
- Azure OpenAI token usage
- Blob storage operations

---

## Production Checklist

### Required Configuration

- [ ] `STORAGE_MODE=azure`
- [ ] `REQUIRE_AUTH=true`
- [ ] `DEBUG=false`
- [ ] `AZURE_ENDPOINT` set
- [ ] `AZURE_API_KEY` in Key Vault
- [ ] `AZURE_STORAGE_CONNECTION_STRING` in Key Vault
- [ ] `ALLOWED_ORIGINS` restricted to production domains

### Security Verification

- [ ] No secrets in code or git history
- [ ] .env excluded from git
- [ ] Rate limiting enabled
- [ ] CORS restricted
- [ ] Security headers present
- [ ] Input validation on all endpoints

### Operational Readiness

- [ ] Health check endpoint working
- [ ] Logging configured
- [ ] Retry logic for Azure services
- [ ] Timeout configuration set
- [ ] Error handling covers all cases

---

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Azure OpenAI Service](https://learn.microsoft.com/en-us/azure/ai-services/openai/)
- [Azure Blob Storage](https://learn.microsoft.com/en-us/azure/storage/blobs/)
- [Azure Container Apps](https://learn.microsoft.com/en-us/azure/container-apps/)
- [OWASP Security Headers](https://owasp.org/www-project-secure-headers/)
