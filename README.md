# Factory Agent - Industry 4.0 Monitoring & AI Assistant

A production-ready cloud-native application for factory operations monitoring and AI-powered insights, featuring comprehensive supply chain traceability, real-time metrics, and an intelligent chatbot. Built with React, FastAPI, and deployed on Azure Container Apps.

## 🎉 Project Status: Feature Complete & Infrastructure Ready

**All core features are implemented and functional!**

- ✅ **Backend API**: 20 REST endpoints (19 API + 1 health check)
- ✅ **Frontend**: 5 complete pages with Material-UI
- ✅ **AI Chat**: Azure AI Foundry integration with tool calling
- ✅ **Supply Chain Traceability**: End-to-end visibility (materials → suppliers → batches → orders)
- ✅ **Material-Supplier Root Cause Linkage**: Direct traceability from defects to suppliers (PR19)
- ✅ **Security**: Rate limiting, CORS, input validation
- ✅ **Testing**: 79+ backend tests (100% passing)
- ✅ **Infrastructure**: Bicep templates, Docker, CI/CD ready

**Next**: Execute Azure deployment (Phase 4 - Infrastructure ready)

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
- **React 19.1** + **TypeScript 5.9** - Modern UI framework
- **Material-UI 7.3** - Component library
- **Recharts 3.3** - Data visualization
- **Axios 1.13** - HTTP client with interceptors
- **Vite 7.1** - Build tool
- **React Router 7.9** - Client-side routing

### Backend
- **FastAPI 0.104+** - Async REST API framework
- **Python 3.11+** - Modern Python with type hints
- **Pydantic 2.0+** - Data validation
- **Azure AI Foundry** - AI chat with AsyncAzureOpenAI client
- **Azure Blob Storage** - Cloud data persistence
- **SlowAPI** - Rate limiting

### Deployment
- **Azure Container Apps** - Infrastructure ready for deployment
- **Azure Container Registry** - Docker image storage
- **GitHub Actions** - CI/CD workflows configured
- **Docker + Docker Compose** - Containerization
- **Azure Bicep** - Infrastructure as Code

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
# Format: https://<resource>.services.ai.azure.com/api/projects/<projectName>
AZURE_ENDPOINT=https://your-resource.services.ai.azure.com/api/projects/yourProject
AZURE_API_KEY=your-api-key
AZURE_DEPLOYMENT_NAME=gpt-4
AZURE_API_VERSION=2024-08-01-preview

# Storage (Optional - defaults to local JSON)
STORAGE_MODE=local  # or 'azure' for cloud storage
AZURE_STORAGE_CONNECTION_STRING=<your-connection-string>
AZURE_BLOB_CONTAINER=factory-data

# Application
DEBUG=false  # Set to 'true' for detailed error messages
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

**Getting Azure AI Foundry credentials:**
1. Go to [Azure AI Foundry Portal](https://ai.azure.com)
2. Navigate to your project
3. Go to **Project Settings**
4. Copy **Endpoint** (format: `https://<resource>.services.ai.azure.com/api/projects/<projectName>`)
5. Go to **Keys** section and copy an API key
6. Set your **Deployment Name** (e.g., `gpt-4`, `gpt-4o`, `gpt-35-turbo`)

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
- `POST /api/setup` - Generate synthetic data
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
pytest tests/ -v
pytest --cov=src --cov-report=html  # With coverage
```

**Frontend:**
```bash
cd frontend
npm run test
npm run lint
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

### Current: Local Development
- Docker Compose for backend only
- Frontend runs separately with `npm run dev` on port 5173
- Backend on port 8000
- Local JSON storage or Azure Blob Storage

### Phase 4: Azure Container Apps (Infrastructure Ready)
- ✅ **Bicep Templates**: Infrastructure defined in `infra/main.bicep`
- ✅ **Dockerfiles**: Both frontend and backend ready
- ✅ **CI/CD**: GitHub Actions workflows configured
- ✅ **Container Apps**: Frontend + backend configuration complete
- ⏳ **Needs**: Local testing, deployment execution

**Deployment Steps**:
1. Test Dockerfiles locally
2. Deploy infrastructure with `az deployment group create`
3. Push code to trigger GitHub Actions CI/CD
4. Validate all features in cloud

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed deployment guide.

## Documentation

- **[implementation-plan.md](implementation-plan.md)** - Complete project roadmap
- **[docs/INSTALL.md](docs/INSTALL.md)** - Detailed installation guide
- **[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)** - Deployment instructions
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

**Status**: Feature-complete with infrastructure ready for deployment. See [implementation-plan.md](implementation-plan.md) for deployment steps (Phase 4) and polish work (Phase 5).
