# Factory Agent - Industry 4.0 Monitoring & AI Assistant

A production-ready cloud-native application for factory operations monitoring and AI-powered insights, featuring comprehensive supply chain traceability, real-time metrics, and an intelligent chatbot. Built with React, FastAPI, and deployed on Azure Container Apps.

## 🎉 Project Status: Feature Complete & Ready for Deployment

**All core features are implemented and functional!**

- ✅ **Backend API**: 21 REST endpoints (monitoring + traceability)
- ✅ **Frontend**: 5 complete pages with Material-UI
- ✅ **AI Chat**: Azure OpenAI integration with tool calling
- ✅ **Supply Chain Traceability**: End-to-end visibility (materials → suppliers → batches → orders)
- ✅ **Material-Supplier Root Cause Linkage**: Direct traceability from defects to suppliers (PR19)
- ✅ **Security**: Rate limiting, CORS, input validation
- ✅ **Testing**: 79+ backend tests (100% passing)

**Next**: Deploy to Azure Container Apps (Phase 4)

## Features

### Core Capabilities
- **AI-Powered Chat**: Natural language queries with Azure OpenAI (GPT-4) and tool calling
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
- **Type-Safe Frontend**: React + TypeScript with Material-UI
- **Dual Storage**: Local JSON (dev) or Azure Blob Storage (production)
- **Functions-First**: Maintainable code with minimal class overhead
- **Production-Ready**: Rate limiting, error handling, comprehensive logging

## Tech Stack

### Frontend
- **React 19** + **TypeScript** - Modern UI framework
- **Material-UI (MUI)** - Component library
- **Recharts** - Data visualization
- **Axios** - HTTP client with interceptors
- **Vite** - Build tool

### Backend
- **FastAPI** - Async REST API framework
- **Python 3.11+** - Modern Python with type hints
- **Pydantic** - Data validation
- **Azure OpenAI** - AI chat with AsyncAzureOpenAI client
- **Azure Blob Storage** - Cloud data persistence

### Deployment (Phase 4 - Planned)
- **Azure Container Apps** - Serverless container hosting
- **Azure Container Registry** - Docker image storage
- **GitHub Actions** - CI/CD
- **Docker + Docker Compose** - Containerization

## Quick Start

### Using Docker Compose (Recommended)

```bash
# 1. Clone and configure
git clone <repository-url>
cd factory-agent
cp .env.example .env
# Edit .env with your Azure OpenAI credentials

# 2. Start everything
docker-compose up --build

# 3. Access the application
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
```

### Manual Setup

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
```

### Azure Configuration

Create a `.env` file (copy from `.env.example`):

```bash
# Azure OpenAI (Required for AI chat)
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_KEY=your-api-key
AZURE_DEPLOYMENT_NAME=gpt-4

# Storage (Optional - defaults to local JSON)
STORAGE_MODE=local  # or 'azure' for cloud storage
AZURE_STORAGE_CONNECTION_STRING=<your-connection-string>
AZURE_BLOB_CONTAINER=factory-data

# Application
DEBUG=false  # Set to 'true' for detailed error messages
```

**Getting Azure credentials:**
1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to your Azure OpenAI resource
3. Go to "Keys and Endpoint" section
4. Copy endpoint URL and API key

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

Open your browser to **http://localhost:5173** (dev) or **http://localhost:3000** (production)

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
- `GET /api/suppliers` - List suppliers
- `GET /api/suppliers/{id}/impact` - Supplier quality impact
- `GET /api/batches` - List production batches
- `GET /api/traceability/backward/{batch_id}` - Backward trace
- `GET /api/traceability/forward/{supplier_id}` - Forward trace
- `GET /api/orders` - List customer orders

**Data Management:**
- `POST /api/setup` - Generate synthetic data
- `GET /api/stats` - Data statistics
- `GET /api/machines` - List machines

**AI Chat:**
- `POST /api/chat` - AI-powered chat with tool calling
  ```json
  {
    "message": "What was the OEE last week?",
    "history": []
  }
  ```

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
│   └── requirements.txt
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
│   │       └── api.ts         # TypeScript interfaces
│   └── package.json
│
├── shared/                     # Shared Python modules
│   ├── models.py              # Pydantic data models
│   ├── metrics.py             # Analysis functions
│   ├── data.py                # Data storage (JSON + Azure Blob)
│   ├── data_generator.py      # Synthetic data generation
│   ├── chat_service.py        # Azure OpenAI integration
│   ├── blob_storage.py        # Azure Blob Storage client
│   └── config.py              # Environment configuration
│
├── tests/                      # Test suite (79+ tests)
│   ├── test_chat_service.py
│   ├── test_blob_storage.py
│   └── test_traceability.py
│
├── docs/                       # Documentation
│   ├── DEPLOYMENT.md          # Deployment guide
│   ├── INSTALL.md             # Installation instructions
│   ├── ROADMAP.md             # Project roadmap
│   └── archive/               # Historical documentation
│
├── scripts/                    # Utility scripts
│   ├── build-local.sh
│   ├── deploy.sh
│   └── legacy/
│       └── run_dashboard.py   # Legacy Streamlit wrapper
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
      → Azure OpenAI (AsyncAzureOpenAI)
        → Tool Calling (AI selects tools)
          → execute_tool() routes to metrics functions
            → Data retrieval from storage
              → Tool results back to Azure OpenAI
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
- Docker Compose for local testing
- Backend on port 8000, frontend on port 3000/5173
- Local JSON storage or Azure Blob Storage

### Phase 4 (Planned): Azure Container Apps
- **Infrastructure**: Bicep templates for Azure resources
- **CI/CD**: GitHub Actions for automated deployments
- **Containers**: Separate containers for frontend + backend
- **Scaling**: Auto-scale based on HTTP traffic
- **Storage**: Azure Blob Storage for production data
- **Authentication**: Azure AD with MSAL (optional)

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for deployment guide.

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

**Status**: Feature-complete and ready for deployment. See [implementation-plan.md](implementation-plan.md) for remaining work (Phase 4: Deployment, Phase 5: Polish).
