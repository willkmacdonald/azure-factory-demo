# Factory Agent - Industry 4.0 Monitoring & AI Assistant

A production-ready cloud-native application for factory operations monitoring and AI-powered insights, featuring comprehensive supply chain traceability, real-time metrics, and an intelligent chatbot. Built with React, FastAPI, and deployed on Azure Container Apps.

## 🎉 Project Status: Deployed to Azure (Phase 4 - Reliability Work In Progress)

**All core features are implemented and deployed to Azure Container Apps!**

- ✅ **Backend API**: 21 REST endpoints (20 functional + 1 health check)
- ✅ **Frontend**: 5 complete pages with Material-UI v7
- ✅ **AI Chat**: Azure AI Foundry integration with tool calling
- ✅ **Supply Chain Traceability**: End-to-end visibility (materials → suppliers → batches → orders)
- ✅ **Material-Supplier Root Cause Linkage**: Direct traceability from defects to suppliers (PR19)
- ✅ **Authentication**: Azure AD JWT validation for admin endpoints (PR3 - 2025-11-17)
- ✅ **Security**: Rate limiting, CORS, input validation, Azure AD auth, prompt injection mitigation
- ✅ **Testing**: Comprehensive test suite (100% passing)
- ✅ **Infrastructure**: Bicep templates, Docker, manually deployed to Azure
- ⚠️ **Known Issue**: Intermittent Azure Blob Storage connectivity (see [Known Issues](#known-issues))

**Current Phase**: Phase 4 deployed with authentication complete. Working on reliability improvements (retry logic + timeout configuration).

## Features

### Core Capabilities
- **AI-Powered Chat**: Natural language queries with Azure AI Foundry (GPT-4, GPT-4o) and tool calling
- **Real-Time Dashboards**: OEE, downtime, quality metrics with interactive charts
- **Supply Chain Traceability**:
  - Backward trace: Batch → Materials → Suppliers
  - Forward trace: Supplier → Batches → Orders
  - Material-supplier root cause linkage for quality issues
- **Machine Monitoring**: Status, performance, OEE metrics
- **Quality Management**: Defect tracking with material/supplier linkage
- **Production Tracking**: Batch tracking, order fulfillment status

### Manufacturing Metrics
- **OEE (Overall Equipment Effectiveness)**: Availability × Performance × Quality
- **Scrap Analysis**: Scrap rates by machine, defect breakdown
- **Quality Issues**: Severity-based filtering with root cause analysis
- **Downtime Analysis**: Downtime by reason, major event tracking

### Architecture Highlights
- **Async-First Backend**: FastAPI with async/await for scalability
- **Type-Safe Frontend**: React 19 + TypeScript with Material-UI v7
- **Dual Storage**: Local JSON (dev) or Azure Blob Storage (production)
- **Functions-First**: Maintainable code with minimal class overhead
- **Production-Ready**: Rate limiting, error handling, comprehensive logging

## Tech Stack

### Frontend
- **React 19.1** + **TypeScript 5.9** - Modern UI framework with strict mode
- **Material-UI 7.3** - Comprehensive component library (beginner-friendly)
- **Recharts 3.3** - Data visualization library
- **Axios 1.13** - HTTP client with request/response interceptors
- **Vite 7.1** - Lightning-fast build tool (replaces Create React App)
- **React Router 7.9** - Client-side routing with nested routes

### Backend
- **FastAPI 0.115+** - Async REST API framework with auto-generated docs
- **Python 3.11+** - Modern Python with type hints
- **Pydantic 2.10+** - Data validation and serialization
- **Azure OpenAI SDK 1.51+** - AI chat with AsyncAzureOpenAI client
- **Azure Blob Storage 12.15+** - Cloud data persistence (async client)
- **SlowAPI 0.1+** - Rate limiting middleware
- **python-jose 3.3+** - JWT token validation for Azure AD auth
- **httpx 0.24+** - Async HTTP client for JWKS fetching
- **aiofiles 24.1+** - Async file I/O
- **pytest 7.4+** - Testing framework

### Deployment
- **Azure Container Apps** - Currently deployed (manual deployment)
- **Azure Container Registry** - Docker image storage
- **GitHub Actions** - CI/CD workflows (configured but not active)
- **Docker + Docker Compose** - Multi-stage containerization
- **Azure Bicep** - Infrastructure as Code templates
- **Nginx 1.27** - Frontend static file server (production)

## Quick Start

### Using Docker Compose (Recommended for Backend)

```bash
# 1. Clone and configure
git clone <repository-url>
cd factory-agent
cp .env.example .env
# Edit .env with your Azure AI Foundry credentials

# 2. Start backend
docker-compose up --build

# 3. Start frontend separately (in another terminal)
cd frontend
npm install
npm run dev

# 4. Access the application
# - Frontend: http://localhost:5173
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
```

**Note**: Docker Compose currently only runs the backend. Frontend must be run separately with `npm run dev`.

### Manual Setup

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Generate test data
python -c "import asyncio; from shared.data_generator import generate_production_data; asyncio.run(generate_production_data(30))"

# Start server
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev  # Development server on port 5173
```

### Azure AI Foundry Configuration

Create a `.env` file (copy from `.env.example`):

```bash
# Azure AI Foundry (Required for AI chat)
# IMPORTANT: Use .cognitiveservices.azure.com endpoint (NOT .services.ai.azure.com)
AZURE_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
AZURE_API_KEY=your-api-key
AZURE_DEPLOYMENT_NAME=gpt-4o  # or gpt-4, gpt-35-turbo
AZURE_API_VERSION=2024-08-01-preview

# Storage (Optional - defaults to local JSON)
STORAGE_MODE=local  # Use 'local' for development, 'azure' for production
AZURE_STORAGE_CONNECTION_STRING=<your-connection-string>
AZURE_BLOB_CONTAINER=factory-data

# Azure AD Authentication (Optional - for POST /api/setup endpoint)
AZURE_AD_TENANT_ID=your-azure-ad-tenant-id
AZURE_AD_CLIENT_ID=your-app-registration-client-id

# Application
DEBUG=false  # Set to 'true' for detailed error messages (development only)
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:5174
RATE_LIMIT_CHAT=10/minute
RATE_LIMIT_SETUP=5/minute
```

**Getting Azure AD credentials (Optional):**
1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to **Azure Active Directory** → **App registrations**
3. Create a new app registration or select existing
4. Copy **Directory (tenant) ID** → use as `AZURE_AD_TENANT_ID`
5. Copy **Application (client) ID** → use as `AZURE_AD_CLIENT_ID`
6. Configure **Authentication** → Add platform → Single-page application → Add `http://localhost:5173` as redirect URI

**Note**: Authentication is only required for the `POST /api/setup` endpoint (data generation). All GET endpoints work without authentication.

**Getting Azure AI Foundry credentials:**
1. Go to [Azure AI Foundry Portal](https://ai.azure.com)
2. Navigate to your project
3. Go to **Project Settings**
4. Copy **Endpoint** - Use the `.cognitiveservices.azure.com` format (the OpenAI SDK requires Cognitive Services endpoint)
5. Go to **Keys** section and copy an API key
6. Set your **Deployment Name** (e.g., `gpt-4o`, `gpt-4`, `gpt-35-turbo`)

**Important**: The endpoint format should be `https://<resource>.cognitiveservices.azure.com/` (NOT the AI Foundry portal URL ending in `.services.ai.azure.com`).

## Usage

### 1. Generate Test Data

First time setup - generate 30 days of synthetic factory data:

```bash
# Using the API
curl -X POST http://localhost:8000/api/setup

# Or specify custom days
curl -X POST http://localhost:8000/api/setup -H "Content-Type: application/json" -d '{"days": 30}'
```

This creates realistic production data with planted scenarios for demonstration.

### 2. Access the Web Interface

Open your browser to **http://localhost:5173**

**5 Available Pages:**
1. **Dashboard** - OEE gauges, downtime charts, quality metrics
2. **Machines** - Machine status cards with performance metrics
3. **Alerts** - Quality issues with material/supplier root cause linkage
4. **Traceability** - 3-tab interface:
   - Batch Lookup: Trace materials and suppliers
   - Supplier Impact: Analyze supplier quality impact
   - Order Status: Track order fulfillment
5. **Chat** - AI assistant for natural language queries

### 3. API Endpoints

**Metrics:**
- `GET /api/metrics/oee` - OEE metrics
- `GET /api/metrics/scrap` - Scrap analysis
- `GET /api/metrics/quality` - Quality issues with material linkage
- `GET /api/metrics/downtime` - Downtime analysis

**Traceability:**
- `GET /api/suppliers` - List suppliers with quality metrics
- `GET /api/suppliers/{id}` - Supplier details
- `GET /api/suppliers/{id}/impact` - Supplier quality impact analysis
- `GET /api/batches` - List production batches
- `GET /api/batches/{id}` - Batch details with materials
- `GET /api/traceability/backward/{batch_id}` - Backward trace (batch → suppliers)
- `GET /api/traceability/forward/{supplier_id}` - Forward trace (supplier → orders)
- `GET /api/orders` - List customer orders
- `GET /api/orders/{id}` - Order details
- `GET /api/orders/{id}/batches` - Order batches with production summary

**Data Management:**
- `POST /api/setup` - Generate synthetic data (requires Azure AD authentication)
- `GET /api/stats` - Data statistics
- `GET /api/machines` - List machines
- `GET /api/date-range` - Data date range

**AI Chat:**
- `POST /api/chat` - AI-powered chat with tool calling
  ```json
  {
    "message": "What was the OEE last week?",
    "history": []
  }
  ```

**System:**
- `GET /health` - Health check endpoint

**Full API documentation:** http://localhost:8000/docs

### 4. Example Chat Queries

The AI assistant can answer questions like:
- "What was our OEE this week?"
- "Which supplier caused quality issues on Day 15?"
- "Show me all materials from ComponentTech Industries"
- "Which machine had the most downtime?"
- "Trace batch BATCH-20251015-003 to its suppliers"
- "What orders are delayed?"

## Project Structure

```
factory-agent/
├── backend/                    # FastAPI backend
│   ├── src/
│   │   └── api/
│   │       ├── main.py        # App entry, CORS, rate limiting
│   │       ├── auth.py        # Azure AD JWT validation (NEW - PR3)
│   │       └── routes/        # API endpoints
│   │           ├── metrics.py      # OEE, scrap, quality, downtime
│   │           ├── chat.py         # AI chat with tool calling
│   │           ├── traceability.py # Supply chain endpoints
│   │           └── data.py         # Data management
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── pages/             # 5 main pages
│   │   │   ├── DashboardPage.tsx
│   │   │   ├── MachinesPage.tsx
│   │   │   ├── AlertsPage.tsx
│   │   │   ├── TraceabilityPage.tsx
│   │   │   └── ChatPage.tsx
│   │   ├── components/        # Reusable UI components
│   │   ├── api/
│   │   │   └── client.ts      # Type-safe API client
│   │   └── types/
│   │   │       └── api.ts         # TypeScript interfaces
│   ├── package.json
│   └── Dockerfile
│
├── shared/                     # Shared Python modules
│   ├── models.py              # Pydantic data models
│   ├── metrics.py             # Analysis functions
│   ├── data.py                # Data storage (JSON + Azure Blob)
│   ├── data_generator.py      # Synthetic data generation
│   ├── chat_service.py        # Azure AI Foundry integration
│   ├── blob_storage.py        # Azure Blob Storage client
│   └── config.py              # Environment configuration
│
├── tests/                      # Test suite (79+ tests)
│   ├── test_chat_service.py
│   ├── test_blob_storage.py
│   └── test_traceability.py
│
├── infra/                      # Infrastructure as Code
│   ├── main.bicep             # Azure Container Apps template
│   └── main.bicepparam        # Deployment parameters
│
├── .github/workflows/          # CI/CD automation
│   ├── deploy-backend.yml     # Backend deployment
│   └── deploy-frontend.yml    # Frontend deployment
│
├── docs/                       # Documentation
│   ├── DEPLOYMENT.md          # Deployment guide
│   ├── INSTALL.md             # Installation instructions
│   ├── ROADMAP.md             # Project roadmap
│   └── archive/               # Historical documentation
│
├── docker-compose.yml         # Local development setup
├── implementation-plan.md     # Project implementation plan
└── README.md                  # This file
```

## Data Flow

### Frontend → Backend → AI
```
React Component
  → API Client (Axios)
    → FastAPI Endpoint
      → Pydantic Validation
        → Business Logic (shared/metrics.py)
          → Data Layer (JSON or Azure Blob)
            → Response (Pydantic model)
              → JSON Serialization
                → React Component State
                  → Material-UI Visualization
```

### AI Chat Flow
```
User Message
  → POST /api/chat
    → chat_service.py
      → Azure AI Foundry (AsyncAzureOpenAI)
        → Tool Calling (AI selects tools)
          → execute_tool() routes to metrics functions
            → Data retrieval from storage
              → Tool results back to Azure AI Foundry
                → AI synthesizes response
                  → Updated conversation history
                    → Response to frontend
```

## Key Features Explained

### Material-Supplier Root Cause Linkage (PR19)

Quality issues now link directly to materials and suppliers:

```json
{
  "type": "material",
  "description": "Material quality",
  "severity": "High",
  "date": "2025-10-15",
  "machine": "Assembly-001",
  "material_id": "MAT-008",
  "lot_number": "LOT-20251023-019",
  "supplier_id": "SUP-004",
  "supplier_name": "ComponentTech Industries",
  "root_cause": "supplier_quality"
}
```

**Benefits:**
- Instant root cause identification
- Quarantine decisions based on supplier quality
- Demonstrable workflow: "This defect was caused by Lot X from Supplier Y"

### Supply Chain Traceability

**Backward Trace** (Batch → Materials → Suppliers):
- View all materials used in a production batch
- Identify which suppliers provided materials
- Highlight materials linked to quality issues

**Forward Trace** (Supplier → Batches → Orders):
- Track which batches used materials from a specific supplier
- Identify affected customer orders
- Calculate impact (defects, cost estimates)

### Dual Storage Mode

**Local Mode** (default):
- Stores `production.json` in `data/` directory
- Fast, no network latency
- Works offline
- Perfect for development

**Azure Mode**:
- Stores `production.json` in Azure Blob Storage
- Cloud persistence, durable
- Multi-instance compatible
- Production-ready

Switch modes via environment variable: `STORAGE_MODE=local` or `STORAGE_MODE=azure`

## Planted Scenarios

The synthetic data includes demonstration scenarios:

1. **Material Quality Issues** (Various Days): Defects linked to specific material lots and suppliers
2. **Machine Downtime Events**: Breakdowns, maintenance, changeovers
3. **Order Fulfillment Tracking**: On-time, delayed, completed orders
4. **Supplier Quality Variations**: Different suppliers with varying defect rates

## Development

### Running Tests

**Backend:**
```bash
cd backend
pytest tests/ -v                      # Run all 164 test functions
pytest --cov=src --cov-report=html    # With coverage report
pytest tests/test_traceability.py -v  # Run specific test file
```

**Test Coverage:**
- 164 test functions across 9 test files
- 3,331 lines of test code
- 100% passing

**Frontend:**
```bash
cd frontend
npm run lint           # ESLint type checking
npm run build          # TypeScript type checking
```

### Code Quality

**Backend:**
```bash
black src/ tests/      # Format code
mypy src/              # Type checking
```

**Frontend:**
```bash
npm run lint           # ESLint
npm run build          # Type checking via TypeScript
```

### Development Workflow

1. **Backend changes**: Auto-reload with `uvicorn --reload`
2. **Frontend changes**: Hot module replacement with Vite
3. **Data changes**: Regenerate with `POST /api/setup`
4. **Test changes**: Run `pytest` or `npm test`

## Deployment

### Current: Azure Container Apps (Manual Deployment)

**Status**: Both frontend and backend are deployed to Azure Container Apps using manual deployment process.

**Deployment Method**:
- **Frontend**: Manually deployed via `az containerapp up`
- **Backend**: Manually deployed via `az containerapp up`
- **CI/CD**: GitHub Actions workflows configured but not currently active
- **Storage**: Azure Blob Storage (STORAGE_MODE=azure)

**Known Deployment Notes**:
- Initial Azure deployments may have a 24-48 hour DNS/propagation delay (hypothesis under investigation)
- Manual deployment used as workaround while investigating GitHub Actions issues

### Local Development

For local development and testing:
- Docker Compose for backend only
- Frontend runs separately with `npm run dev` on port 5173
- Backend on port 8000
- Can use local JSON storage (`STORAGE_MODE=local`) or Azure Blob Storage (`STORAGE_MODE=azure`)

**Local Development Steps**:
```bash
# Backend (Docker Compose)
docker-compose up --build

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed deployment guide and troubleshooting.

## Known Issues

### Intermittent "Server error - please try again later" Messages

**Symptom**: Occasional error messages when using the application, particularly with AI chat or data-heavy pages.

**Root Cause**: Transient Azure Blob Storage connectivity issues when `STORAGE_MODE=azure`. This can occur due to:
- Network latency/timeouts
- Azure service throttling (rare)
- Connection pool exhaustion during high traffic

**Workarounds**:
1. **For Local Development**: Set `STORAGE_MODE=local` in `.env` to eliminate network dependency
2. **Refresh the page**: Intermittent errors usually resolve on retry
3. **Enable DEBUG mode**: Set `DEBUG=true` in `.env` to see detailed error messages

**Planned Fix**: PR22 will implement retry logic with exponential backoff and timeout configuration (3-4 hours of work). See [implementation-plan.md](implementation-plan.md) for details.

**Progress**: Under investigation. See implementation plan for current status.

## Documentation

- **[implementation-plan.md](implementation-plan.md)** - Complete project roadmap with current phase status
- **[docs/INSTALL.md](docs/INSTALL.md)** - Detailed installation guide
- **[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)** - Deployment instructions and troubleshooting
- **[docs/ROADMAP.md](docs/ROADMAP.md)** - Project roadmap and future plans
- **[docs/archive/](docs/archive/)** - Historical documentation

## Design Philosophy

**Functions Over Classes**:
- Default to functions for stateless operations
- Use classes only for: data models (Pydantic), stateful clients (Azure SDK), framework patterns

**Async/Sync Split**:
- FastAPI routes: `async def` with `await` for ALL I/O operations
- CLI commands: Synchronous operations for simplicity
- Shared utilities: Match the calling context

**Type Safety**:
- Python: Type hints on all functions, Pydantic models
- TypeScript: Strict mode, no `any` types
- End-to-end type safety: TypeScript interfaces match Pydantic models

**Demo Simplicity**:
- JSON files for data (not database)
- Consolidated modules (avoid over-engineering)
- Clear > clever

## Contributing

This is a demonstration project. Key conventions:

1. **Type hints required** on all Python functions
2. **Async for FastAPI**, sync for CLI
3. **Functions first**, classes only when needed
4. **Test critical paths** (not 100% coverage)
5. **Update docs** when adding features

## License

MIT

---

**Status**: Deployed to Azure Container Apps (Phase 4 complete). **Latest**: Azure AD authentication module complete (PR3 - 2025-11-17). Currently working on reliability improvements to address intermittent Azure Blob Storage connectivity. See [implementation-plan.md](implementation-plan.md) for current phase status and next steps (PR22: Retry Logic + Timeout Configuration).

**Recent Updates:**
- **2025-11-17**: Azure AD JWT authentication for admin endpoints (PR3) - Fixed async/await patterns, type hints, added httpx dependency
- **2025-11-17**: Implementation plan optimized for context window efficiency (13.4% reduction, 487 lines)
