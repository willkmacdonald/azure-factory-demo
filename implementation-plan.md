# Factory Agent - Integrated Implementation Plan

**Last Updated**: 2025-11-15
**Phase**: Phase 2 - Backend Integration (Traceability + Azure Migration)
**Architecture**: React + FastAPI + Azure Container Apps + Supply Chain Traceability

---

## Overview

Factory Agent is a comprehensive demo combining:
1. **Azure Migration**: Streamlit/CLI → React + FastAPI + Azure Container Apps
2. **Supply Chain Traceability**: End-to-end visibility from suppliers to customer orders

**Goal**: One integrated demo showcasing full-stack development (data models → API → UI → deployment) with demonstrable Industry 4.0 capabilities.

---

## Current Status

**Completed Work**:
- ✅ **Phase 1**: Backend API complete (FastAPI with all monitoring endpoints)
- ✅ **Phase 2**: Azure infrastructure complete (Bicep, Container Apps, CI/CD)
- ✅ **Phase 3**: React foundation complete (navigation, layout, API client, TypeScript types, metrics dashboard)
- ✅ **Traceability Backend**: Models merged (Supplier, MaterialLot, Order, ProductionBatch on feature branch)
- ✅ **Phase 2 - Part 1**: Merge traceability + add API endpoints (COMPLETED - 9 endpoints implemented)

**Next Up**:
- 🚧 **Phase 2 - Part 2**: Testing & verification (1-2 hours)
- ⏸️ **Phase 3**: Complete React pages with traceability integration (18-24 hours)
- ⏸️ **Phase 4**: Deploy frontend to Azure (6-8 hours)
- ⏸️ **Phase 5**: Polish with demonstrable scenarios (8-12 hours)

**Reference**: See `ARCHIVE-completed-prs.md` for detailed specs of PR6-PR13 (completed work)

---

## Phase 2: Backend Integration (NEXT - 8-12 hours)

### Overview
Merge supply chain traceability models into main and add REST API endpoints for traceability queries.

### PR: Backend Traceability Integration

**Priority**: High
**Estimated Effort**: 8-12 hours
**Dependencies**: Feature branch `feature/pr15-aggregation` ready to merge

#### Tasks

**1. Merge Feature Branch** (2-3 hours) ✅ COMPLETED
- ✅ Create branch `feature/integrated-traceability` from main
- ✅ Cherry-pick traceability commits (models, generation, aggregation)
- ✅ Preserve deployment infrastructure (DO NOT cherry-pick deleted files)
- ✅ See `MERGE-STRATEGY.md` for detailed merge instructions
- ✅ Run tests: `pytest tests/ -v`
- ✅ Verify data generation: `python -m src.main setup`

**2. Add Traceability API Endpoints** (6-8 hours) ✅ COMPLETED
Created `backend/src/api/routes/traceability.py` with 10 async endpoints:

- ✅ `GET /api/suppliers` - List all suppliers with quality metrics
  - Response: List[Supplier] with quality ratings, on-time delivery, defect rates
  - Supports status filtering

- ✅ `GET /api/suppliers/{supplier_id}` - Supplier details
  - Response: Supplier with full contact and certification info

- ✅ `GET /api/suppliers/{supplier_id}/impact` - Quality issues by supplier
  - Query params: start_date, end_date
  - Response: Quality issues linked to supplier's materials, cost impact

- ✅ `GET /api/batches` - List production batches
  - Query params: machine_id, start_date, end_date, order_id, limit
  - Response: List[ProductionBatch] with pagination

- ✅ `GET /api/batches/{batch_id}` - Batch details with full traceability
  - Response: ProductionBatch with materials consumed, supplier info, order info

- ✅ `GET /api/traceability/backward/{batch_id}` - Backward trace
  - Response: Batch → Materials → Suppliers (root cause analysis)

- ✅ `GET /api/traceability/forward/{supplier_id}` - Forward trace
  - Query params: start_date, end_date
  - Response: Supplier → Batches → Quality issues → Orders affected

- ✅ `GET /api/orders` - List customer orders
  - Query params: status (Pending, InProgress, Completed, Shipped, Delayed), limit
  - Response: List[Order] with production status

- ✅ `GET /api/orders/{order_id}` - Order details
  - Response: Order with assigned batches, quality issues, delivery status

- ✅ `GET /api/orders/{order_id}/batches` - Order batches with production summary
  - Response: Order with assigned batches and production progress

**3. Enhance Existing Endpoints** (1 hour) ✅ COMPLETED
Updated `backend/src/api/routes/data.py`:

- ✅ `GET /api/stats` - Enhanced with traceability counts:
  - Added supplier_count
  - Added material_lot_count
  - Added order_count
  - Added batch_count

**4. Testing** (1 hour) ⏳ PENDING
- [ ] Write pytest tests for all new endpoints
- [ ] Test backward trace: batch → materials → supplier
- [ ] Test forward trace: supplier → batches → quality issues
- [ ] Test query parameter filtering
- [ ] Run full suite: `pytest tests/ -v --cov=backend --cov=shared`

#### Deliverables
- ✅ Feature branch merged into main
- ✅ 10 new traceability API endpoints (1 more than planned)
- ✅ Enhanced stats endpoints with traceability counts
- ⏳ Tests pending (next task)
- ✅ API documentation (FastAPI /docs auto-generated)

---

## Phase 3: Frontend Complete (18-24 hours)

### Overview
Complete all React pages with integrated monitoring + traceability features.

### PR14: Machine Status & Alerts (3-4 hours)

**Status**: Partially complete (skeleton pages exist)
**Priority**: Medium

#### Tasks
- Relocate API service to `frontend/src/api/client.ts` (5 min)
- Create machine list view with MUI DataGrid (1.5 hours)
  - Status indicators (Green/Yellow/Red)
  - Sortable columns: Name, Status, OEE, Last Updated
  - Click to navigate to detail view
- Build alert notification system (1.5 hours)
  - Alert cards with severity colors
  - Filter by machine and severity
  - Recent alerts list (last 10)
- Add machine detail page (1 hour)
  - Machine stats, 30-day OEE trend
  - Recent batches, recent alerts
  - Back button to machines list

### PR15: Supplier Traceability Page (4-5 hours)

**Status**: Not started
**Priority**: High (core traceability feature)

#### Tasks
- Create TypeScript types for traceability (1 hour)
  - Add `frontend/src/types/traceability.ts`
  - Interfaces: Supplier, MaterialLot, ProductionBatch, Order
  - Update `frontend/src/api/client.ts` with new endpoints

- Create TraceabilityPage component (3-4 hours)
  - Tab 1: Batch Lookup
    - Input: Batch ID
    - Output: Batch → Materials → Suppliers (tree visualization)
  - Tab 2: Supplier Impact
    - Select supplier from dropdown
    - Show quality issues linked to supplier
    - Show affected batches and orders
    - Cost impact summary
  - Tab 3: Order Status
    - List orders with production status
    - Click order → show batches, quality, suppliers

### PR16: AI Chat Interface (3-4 hours)

**Status**: Skeleton exists
**Priority**: Medium

#### Tasks
- Chat console with message history (1.5 hours)
  - Auto-scroll, timestamps
  - User/assistant styling
  - Loading indicator
- Integrate with `/api/chat` (1 hour)
  - useChat hook
  - Conversation history (max 50)
  - Error recovery
- Suggested prompts (45 min)
  - Show when chat empty
  - Example questions about traceability
  - Click to fill input

### PR17: Complete DashboardPage (4-6 hours)

**Status**: Metrics working, needs traceability integration
**Priority**: Medium

#### Tasks
- Add Supplier Quality Scorecard section (2-3 hours)
  - Top suppliers by quality rating
  - Quality trend chart
  - Click supplier → navigate to TraceabilityPage
- Add Orders Overview section (2-3 hours)
  - Recent orders list
  - Order status breakdown (pie chart)
  - Click order → navigate to TraceabilityPage

### PR18: Deployment Ready UI (2-3 hours)

**Status**: Not started
**Priority**: Medium

#### Tasks
- Add favicon and app title (15 min)
- Improve empty states (30 min)
- Add loading skeletons instead of spinners (1 hour)
- Improve mobile responsiveness (1 hour)
- Polish chart styling (consistent colors, labels) (30 min)

---

## Phase 4: Frontend Deployment (6-8 hours)

### Overview
Deploy React frontend to Azure Container Apps with CI/CD.

### Tasks

**1. Verify Frontend Dockerfile** (1 hour)
- Test multi-stage build locally
- Verify Nginx serves React correctly
- Test Docker image: `docker build -t frontend ./frontend && docker run -p 3000:80 frontend`

**2. Update Bicep Template** (2-3 hours)
- Update `infra/main.bicep` to add frontend Container App
- Configure ingress (HTTPS, external)
- Add environment variables (API_URL → backend)
- Configure CORS on backend to allow frontend origin

**3. GitHub Actions for Frontend** (2-3 hours)
- Update `.github/workflows/deploy-frontend.yml`
- Build frontend Docker image
- Push to Azure Container Registry
- Deploy to Container Apps
- Health check verification
- Trigger on changes to `frontend/` or `shared/`

**4. End-to-End Testing** (1-2 hours)
- Deploy both backend and frontend
- Test all pages in deployed environment
- Verify API calls (CORS working)
- Test traceability workflows
- Document deployed URLs

#### Deliverables
- ✅ Frontend deployed to Azure Container Apps
- ✅ Backend + Frontend communicating
- ✅ CI/CD working for both
- ✅ All features functional in production

---

## Phase 5: Polish & Demonstrable Scenarios (8-12 hours)

### Overview
Add planted scenarios to make traceability demonstrable in 5-minute demos.

### Tasks

**1. Plant Scenarios in Data Generator** (4-6 hours)
Update `shared/data_generator.py`:

- **Day 15 Quality Spike** (2-3 hours)
  - Create defective material lot from lower-rated supplier
  - Ensure batches on Day 15 using this lot have elevated defects
  - Make backward trace obvious: Quality → Batch → Lot → Supplier

- **Day 22 Machine Breakdown** (2-3 hours)
  - Simulate machine downtime (CNC-001 offline 4 hours)
  - Link affected batches to orders with tight due dates
  - Make forward trace obvious: Breakdown → Batches → Delayed orders

- **Supplier Quality Correlation** (1 hour)
  - Bias quality issues toward materials from low-rated suppliers
  - Formula: `defect_probability = base * (100 - supplier_rating) / 50`

**2. Add Quarantine Recommendations** (1-2 hours)
- Analyze generated material lots
- Flag lots appearing in >3 quality issues
- Add `quarantine_recommended: true` field
- Add `quarantine_reason` explanation

**3. Create Demo Documentation** (2-3 hours)
- Create `docs/DEMO-SCENARIOS.md`
- Document "Day 15 Quality Spike Demo" (step-by-step with screenshots)
- Document "Day 22 Breakdown Demo" (step-by-step)
- Document "Supplier Impact Analysis Demo"
- Update README.md with demo instructions

**4. Validation Tests** (1-2 hours)
- Test: Day 15 has quality spike (>10 defects)
- Test: Quality issues link to specific supplier
- Test: Day 22 has machine downtime
- Test: Affected orders flagged as delayed
- Test: Quarantine recommendations exist
- Test: Serial ranges non-overlapping

#### Deliverables
- ✅ Demonstrable scenarios working
- ✅ DEMO-SCENARIOS.md with step-by-step demos
- ✅ README.md updated
- ✅ All validation tests passing

---

## Optional: Authentication (8-10 hours - SKIP for demo)

Only pursue if demo requires multi-user access or enterprise showcase.

### Tasks
- Add @azure/msal-react configuration (1 hour)
- Implement login/logout UI (1 hour)
- Add protected routes (1 hour)
- Configure Azure AD app registration (1 hour)
- Update backend for JWT validation (2-3 hours)
- Add auth dependency to all API routes (2-3 hours)

---

## Success Criteria

### Technical
- ✅ All backend endpoints working (monitoring + traceability)
- ✅ All React pages fully functional with data
- ✅ Deployed to Azure Container Apps (backend + frontend)
- ✅ CI/CD pipeline working for both
- ✅ All tests passing (unit + integration)

### Demonstrable
- ✅ Can trace quality issue → supplier (5-min demo)
- ✅ Can trace supplier → affected orders (5-min demo)
- ✅ Can show order fulfillment status (5-min demo)
- ✅ Dashboard shows comprehensive factory metrics
- ✅ AI chat answers traceability questions

### Documentation
- ✅ README.md explains full feature set
- ✅ DEMO-SCENARIOS.md provides demo scripts
- ✅ API documentation complete (FastAPI /docs)
- ✅ Code well-commented with type hints

---

## Total Effort Estimate

| Phase | Hours | Cumulative |
|-------|-------|------------|
| Phase 2: Backend Integration | 8-12 | 8-12 |
| Phase 3: Frontend Complete | 18-24 | 26-36 |
| Phase 4: Deployment | 6-8 | 32-44 |
| Phase 5: Polish & Scenarios | 8-12 | 40-56 |
| **Total** | **40-56 hours** | - |

**Timeline**: 5-7 weeks at 8-10 hours/week, or 3-4 weeks at 15-20 hours/week

---

## Reference Documentation

- **ARCHIVE-completed-prs.md**: Detailed specs for completed PR6-PR13
- **MERGE-STRATEGY.md**: Guide for merging traceability feature branch
- **ROADMAP.md**: High-level phase breakdown (to be created)
- **docs/PR14_SUMMARY.md**: ProductionBatch implementation details
- **PR13_SUMMARY.md**: Supply chain models implementation details
- **docs/traceability_examples.py**: Example traceability queries

---

## Development Workflow

1. Clear context before starting new phase
2. Use Explore agent + deepcontext for codebase familiarization
3. Use context7 for library documentation
4. Use azure-mcp for Azure-specific questions
5. Clear context before pr-reviewer
6. Run pr-reviewer after major milestone
7. Update implementation plan with findings
8. Repeat for next phase

---

**Last Updated**: 2025-11-15 (Updated: Phase 2 Part 1 marked complete)
**Current Focus**: Phase 2 Part 2 - Testing & verification
**Next Milestone**: Phase 3 - Frontend complete with traceability pages
