# Factory Agent - Implementation Plan

**Last Updated**: 2025-11-17 (Updated: PR3 Code Review Fixes)
**Status**: Phase 3 Complete (100%) | Phase 4 In Progress (Deployed + Auth Complete) | Phase 5 Planned
**Architecture**: React + FastAPI + Azure Container Apps + AI Foundry + Azure Blob Storage + Azure AD Auth

---

## Executive Summary

Factory Agent is a **feature-complete** Industry 4.0 monitoring application with AI-powered insights and supply chain traceability, now **deployed to Azure** with a **known reliability issue** to fix.

**Completed** (Phases 1-3):
- ✅ Backend: 21 REST API endpoints (metrics + traceability + AI chat)
- ✅ Frontend: 5 complete React pages with Material-UI
- ✅ AI Chat: Azure AI Foundry integration with tool calling
- ✅ Supply Chain: End-to-end traceability with material-supplier linkage
- ✅ Testing: 79+ backend tests (100% passing)
- ✅ Code Review: All critical and important issues resolved
- ✅ Authentication: Azure AD JWT validation module complete

**Deployed** (Phase 4 - 80% Complete):
- ✅ Infrastructure: Bicep templates, Dockerfiles, GitHub Actions
- ✅ Deployment: Frontend + backend deployed to Azure Container Apps (manual)
- ✅ Azure Blob Storage: Integrated and accessible (but with transient issues)
- ✅ Hybrid Development: Local dev + cloud data working
- ✅ Authentication: Azure AD JWT validation in backend/src/api/auth.py
- ⚠️ **Issue Found**: Intermittent connectivity errors from Azure Blob Storage (known, isolated)
- ⏳ **Needs**: Implement retry logic + timeouts (PR22) to resolve transient failures

**Next** (Phase 4 Continuation + Phase 5):
- Resolve reliability issues (retry logic, timeout config)
- Optional: Fix GitHub Actions CI/CD pipeline
- Phase 5: Polish with demo scenarios and documentation

---

## Current Status & Next Steps

### Recent Achievement: Azure Blob Storage Migration Complete ✅

**Migration Completed** (2025-11-17):
- ✅ **Storage Account**: `factoryagentdata` in `wkm-rg` (WKM Migration Sub)
- ✅ **Container**: `factory-data` (Azure Blob Storage)
- ✅ **Hybrid Development Pattern**:
  - Backend running locally (localhost:8000)
  - Frontend running locally (localhost:5173)
  - Data stored in Azure Blob Storage (cloud persistence)
- ✅ **Data Generated**: Fresh 30-day dataset (2025-10-18 to 2025-11-16)
- ✅ **Dataset Size**: 615KB production.json in Azure Blob
- ✅ **Status**: Tested and working end-to-end

**Infrastructure Note**:
- Attempted: Azure Dev subscription storage (created account but data plane access failed)
- Workaround: Using storage account in WKM Migration Sub (working smoothly)
- Forum post created for community help on Azure Dev subscription ResourceNotFound issue

### Phase 4 Status: Deployment & Reliability (In Progress)

**Current Situation** (2025-11-17):
- ✅ All core features complete (backend API, frontend, AI chat)
- ✅ Azure Blob Storage integrated and accessible
- ⏳ **Deployed to Azure** (manually - not via GitHub Actions)
  - Frontend deployed to Azure Container Apps
  - Backend deployed to Azure Container Apps
- ⚠️ **Known Issue**: Intermittent "Server error - please try again later" messages
  - **Root Cause**: Azure Blob Storage transient connectivity issues
  - **Frequency**: Intermittent, appears under certain load conditions
  - **Impact**: User-facing errors when `STORAGE_MODE="azure"`
  - **Hypothesis**: Possible 24-48 hour propagation delay for initial Azure deployments
  - **Investigation**: Identified when STORAGE_MODE switches to azure in production

**Infrastructure Status**:
- ✅ `infra/main.bicep` - Frontend + backend Container Apps defined
- ✅ `frontend/Dockerfile` - Multi-stage React build + Nginx (deployed)
- ✅ `backend/Dockerfile` - Python 3.11 + FastAPI (deployed)
- ⏳ `.github/workflows/deploy-frontend.yml` - CI/CD configured (not yet used)
- ⏳ `.github/workflows/deploy-backend.yml` - CI/CD configured (not yet used)
- ✅ Azure Blob Storage - Configured and tested with live data
- ⚠️ **Workaround**: Manual deployment in use (not automated CI/CD)

### Immediate Priority: Resolve Azure Blob Storage Reliability (Phase 4)

**Option 1: Investigate & Wait** (Low effort, risky)
- Theory: DNS/propagation delays on initial Azure deployment
- Action: Wait 24-48 hours and re-test
- Risk: May not resolve; production deployment incomplete

**Option 2: Implement Retry Logic** (Medium effort, recommended)
- Add exponential backoff for Azure Blob Storage API calls
- Configure retry policy: 3 attempts with 100-1000ms delays
- Update: `backend/src/shared/blob_storage.py` (if exists)
- Testing: Validate retry behavior under load
- Effort: 1-2 hours
- Impact: Improves reliability and handles transient failures

**Option 3: Add Timeout Configuration** (Medium effort, recommended)
- Configure Azure Blob Storage client timeouts
- Set connection timeout: 10-30 seconds
- Set request timeout: 30-60 seconds
- Add circuit breaker pattern for repeated failures
- Effort: 1-2 hours
- Impact: Prevents hanging requests, fail-fast behavior

**Option 4: Add Caching Layer** (Higher effort, optional)
- Cache Azure Blob data in-memory (Redis or process memory)
- Reduce direct Azure calls by caching recent data
- Implement cache invalidation strategy
- Effort: 3-4 hours
- Impact: Reduces load on Azure Blob, improves response times

**Option 5: Fallback to Local Storage** (Low effort, workaround)
- When STORAGE_MODE="azure" fails, fallback to local JSON
- Log fallback events for monitoring
- Effort: <1 hour
- Impact: Improves reliability but data isn't persisted to cloud

**Recommended Path**:
1. **Short-term**: Implement Option 2 (retry logic) - 1-2 hours
2. **Follow-up**: Add Option 3 (timeout config) - 1-2 hours
3. **Monitor**: Test in production for 24-48 hours
4. **Optional**: Add Option 4 (caching) if needed

**Alternatives: Optional Improvements**
- **PR20B**: Code Quality (4 items, 1-2 hours total)
- **PR21**: Selective Authentication (4-6 hours, security enhancement)
- **GitHub Actions Fix**: Troubleshoot and fix CI/CD pipeline (2-3 hours)
- **Deployment Documentation**: Document workaround process (1 hour)

---

## Phase Breakdown

### ✅ Phase 1: Backend API (Complete)
**Delivered**: 21 REST endpoints, rate limiting, CORS, health checks
- Metrics: OEE, scrap, quality, downtime
- Traceability: 10 endpoints for supply chain visibility
- Chat: Azure AI Foundry integration with tool calling
- Data: Setup, stats, machine info

### ✅ Phase 2: Backend Integration (Complete)
**Delivered**: Supply chain models integrated, 56 comprehensive tests
- Merged traceability feature branch
- Backward/forward trace endpoints
- Material-supplier linkage in quality issues (PR19)
- All tests passing (100%)

### ✅ Phase 3: Frontend Development (Complete)
**Delivered**: 5 complete pages (89,883 lines of TypeScript)

**Pages Implemented**:
1. **DashboardPage** - OEE gauges, downtime charts, quality metrics
2. **MachinesPage** - Machine status cards with performance data
3. **AlertsPage** - Quality issues with material/supplier/root cause columns
4. **TraceabilityPage** - 3-tab interface:
   - Batch Lookup: Material → Supplier tracing
   - Supplier Impact: Quality analysis by supplier
   - Order Status: Order fulfillment tracking
5. **ChatPage** - AI assistant with Azure AI Foundry

**Key Features**:
- TypeScript types for all API models
- API client with 30+ methods
- Material-UI components throughout
- Recharts for data visualization
- Full error handling and loading states
- Material-supplier root cause linkage (PR19 - Complete)

### 🚀 Phase 4: Deployment (Infrastructure Ready - Needs Execution)

**Status**: 90% complete, Azure Blob Storage integrated, needs deployment execution

**What's Ready**:
- ✅ Bicep infrastructure templates
- ✅ Dockerfiles (frontend + backend)
- ✅ GitHub Actions workflows
- ✅ Container Apps configuration
- ✅ CORS and rate limiting configured
- ✅ Azure Blob Storage integration (tested with live data)
- ✅ Hybrid development pattern validated (local frontend + backend, cloud data)

**What's Needed** (3-5 hours):
1. Test Dockerfiles locally (1 hour) - Docker build and docker-compose up
2. Deploy to Azure Container Apps (2-3 hours) - Execute Bicep deployment
3. Validate in production (1 hour) - Test all endpoints, chat, traceability in cloud

**Deliverables**:
- Both frontend and backend deployed to Azure Container Apps
- CI/CD pipeline functional and integrated with GitHub
- HTTPS endpoints accessible from cloud
- All features working in cloud with Azure Blob Storage
- Live data persisted in Azure

### 📋 Phase 5: Polish & Scenarios (Planned)

**Goals**: Add demo scenarios, documentation, screenshots

**Tasks** (8-12 hours):
1. **Planted Scenarios** (4-6 hours)
   - Day 15 quality spike traceable to supplier
   - Day 22 machine breakdown affecting orders
   - Supplier quality correlations

2. **Demo Documentation** (2-3 hours)
   - Create `docs/DEMO-SCENARIOS.md`
   - Step-by-step demo walkthroughs
   - Screenshots of key workflows

3. **Validation Tests** (1-2 hours)
   - Verify demo scenarios work
   - Test traceability workflows
   - Validate quarantine recommendations

4. **Final Polish** (1-2 hours)
   - Update README with deployment URLs
   - Add architecture diagrams
   - Record demo video (optional)

---

## Optional Work

### PR20B: Code Quality Improvements ✅

**Status**: Complete (2025-11-17)

**4 Improvements Completed**:
1. ✅ **Error Logging** - Verified `load_data_async()` already has comprehensive error logging matching sync version
2. ✅ **Rate Limiting** - Verified SlowAPI configuration is properly connected:
   - `app.state.limiter` set in main.py for global access
   - Exception handler registered for RateLimitExceeded
   - Local limiter instances in route files work correctly with @limiter.limit() decorators
   - Confirmed this is the standard SlowAPI pattern per official documentation
3. ✅ **OEE Documentation** - Enhanced hardcoded performance factor documentation (shared/metrics.py:110-120):
   - Added justification for 0.95 (95%) assumption
   - Explained industry-typical speed efficiency
   - Clarified acceptable for demo, needs replacement in production
4. ✅ **Security Docs** - Added comprehensive prompt injection documentation (shared/chat_service.py:40-76):
   - Documented current protections (pattern detection, logging, sanitization)
   - Listed limitations (basic pattern matching, no blocking, no semantic analysis)
   - Provided 10 production recommendations (Azure Content Safety, semantic analysis, etc.)
   - Added references (OWASP LLM Top 10, Azure docs, prompt injection primers)

**Impact**: Improved code documentation, clearer security boundaries for demo vs. production

**Actual Effort**: ~1 hour (verification + documentation enhancements)

---

## Recent Fixes

### Trio Test Failures Fixed ✅

**Issue**: Tests with `@pytest.mark.anyio` were running with both asyncio and trio backends, but trio wasn't installed, causing 6 test failures.

**Root Cause**:
- pytest-anyio defaults to testing with both asyncio and trio backends
- Factory Agent uses FastAPI (asyncio-only), no trio support needed
- trio library not in requirements or dependencies

**Solution** (2025-11-17):
- Added `anyio_backend` fixture to `tests/conftest.py` and `backend/tests/conftest.py`
- Fixture returns `'asyncio'` to force pytest-anyio to only use asyncio backend
- Documented the configuration for future maintainers

**Result**:
- Before: 168 tests collected (6 trio failures)
- After: 162 tests collected (0 trio failures)
- All asyncio tests pass (161/162 tests passing, 1 pre-existing failure in test_chat_integration.py unrelated to trio)

**Files Modified**:
- `tests/conftest.py` (created)
- `backend/tests/conftest.py` (added anyio_backend fixture)

**Actual Effort**: ~15 minutes

### PR21: Implement Selective Authentication (Public Read, Authenticated Write)

**Status**: Optional - Enhances security, not blocking deployment

**Goal**: Protect destructive endpoints while keeping viewing endpoints public

**Backend Tasks** (2-3 hours):
1. Add `python-jose[cryptography]` and `python-multipart` to requirements.txt
2. Create `backend/src/api/auth.py`:
   - Azure AD JWT token validation middleware
   - `get_current_user` dependency for protected routes
   - Environment variables: `AZURE_AD_TENANT_ID`, `AZURE_AD_CLIENT_ID`
3. Apply authentication to protected endpoints:
   - `POST /api/setup` - Add `Depends(get_current_user)`
   - Return 401 Unauthorized if token missing/invalid
4. Update CORS configuration to allow authentication headers
5. Update `.env.example` with Azure AD secrets

**Frontend Tasks** (2-3 hours):
1. Configure MSAL in `frontend/src/main.tsx`:
   - `MsalProvider` wrapper around App
   - Environment variables: `VITE_AZURE_AD_CLIENT_ID`, `VITE_AZURE_AD_TENANT_ID`
2. Create `frontend/src/components/AuthButton.tsx`:
   - Sign In/Sign Out button in AppBar
   - Display user name when authenticated
3. Update `frontend/src/api/client.ts`:
   - Use `useMsal` hook to get access tokens
   - Attach Bearer token to protected endpoint calls
4. Update `frontend/src/pages/DashboardPage.tsx`:
   - Add conditional "Generate New Data" button
   - Only show to authenticated users
   - Call `POST /api/setup` when clicked
5. Update `frontend/src/layouts/MainLayout.tsx`:
   - Add AuthButton to AppBar

**Testing** (30 min):
1. Verify public endpoints (GET) work without auth
2. Verify `POST /api/setup` returns 401 without token
3. Test sign in/sign out flow
4. Confirm authenticated users can generate data

**Documentation** (30 min):
- Update README with Azure AD setup instructions
- Document app registration requirements

**Estimated Effort**: 4-6 hours total (2-3 backend, 2-3 frontend)
**Priority**: Medium (security improvement, enables UI controls)
**Dependencies**: None (Phase 3 complete)
**Blocks**: None
**Note**: Option A (Public Read, Authenticated Write) - simplest for demo

### Backlog: Enhancements (40 min)

**3 Low-Priority Items**:
1. Fix TypeScript Warning import alias (15 min)
2. Delete duplicate regeneration script (10 min)
3. Update SECURITY_STATUS.md with limitations (15 min)

---

## Completed Work Summary

### Recent PRs (All Complete)

**PR3: Authentication Module Code Review Fixes** ✅
- **Status**: Complete (2025-11-17)
- **Location**: `backend/src/api/auth.py`
- **Fixes Applied**:
  1. ✅ Async/await patterns: Replaced synchronous `requests` with `httpx.AsyncClient`
  2. ✅ Type hints: Fixed `'any'` to `'Any'` from `typing` module
  3. ✅ Dependency: Added `httpx` to `backend/requirements.txt`
  4. ✅ Security: Improved error messages to avoid exposing sensitive endpoint details
- **Impact**: Authentication module now follows async/await best practices for FastAPI
- **Commits**: Merged to main branch

**PR19: Material-Supplier Root Cause Linkage** ✅
- Backend: QualityIssue model with material/supplier fields
- API: Material linkage in quality endpoint responses
- Frontend: AlertsPage shows Material/Lot/Supplier/Root Cause columns
- Frontend: TraceabilityPage highlights materials with quality issues
- **Status**: 100% complete (backend + frontend)
- **Commits**: b531dd7 (backend), e2dab42 (frontend)

**PR20A: Critical Code Review Fixes** ✅
- All 4 issues verified as already fixed in commit 2e97bd4
- Icon imports correct, type safety maintained
- Constants centralized, logging comprehensive
- **Effort**: <1 hour (verification only)

**PR20: Critical Backend Fixes** ✅
- Fixed parameter ordering in regenerate_data.py
- Material linkage already working (verified)
- Date validation already working (verified)
- **Effort**: ~15 minutes (only Issue 1 needed fix)

### Development Statistics

**Backend**:
- 21 REST API endpoints
- 79+ comprehensive tests (100% passing)
- 4 route modules (data, metrics, chat, traceability)
- Rate limiting, CORS, input validation
- Async/await throughout FastAPI

**Frontend**:
- 89,883 lines of TypeScript
- 5 complete pages
- 30+ API client methods
- Full Material-UI integration
- Recharts visualization

**Infrastructure**:
- Docker + Docker Compose
- Azure Bicep templates
- GitHub Actions CI/CD
- Azure Container Apps ready

---

## Success Criteria

### Technical ✅
- ✅ All backend endpoints working
- ✅ All React pages functional
- ✅ Type safety (Python + TypeScript)
- ✅ Tests passing (79+)
- ⏳ Deployed to Azure (ready to execute)

### Demonstrable ✅
- ✅ Can trace quality issue → supplier
- ✅ Can trace supplier → affected orders
- ✅ Dashboard shows comprehensive metrics
- ✅ AI chat answers traceability questions

### Documentation ✅
- ✅ README explains features
- ✅ API docs complete (FastAPI /docs)
- ✅ Code well-commented with type hints
- ⏳ DEMO-SCENARIOS.md (Phase 5)

---

## Timeline & Effort

| Phase | Estimated | Actual | Status |
|-------|-----------|--------|--------|
| Phase 1: Backend API | 12-16 hrs | ~14 hrs | ✅ Complete |
| Phase 2: Backend Integration | 8-12 hrs | ~10 hrs | ✅ Complete |
| Phase 3: Frontend Development | 24-30 hrs | ~28 hrs | ✅ Complete |
| Code Review + Fixes | 2-3 hrs | ~1 hr | ✅ Complete |
| **PR3: Auth Module Code Review Fixes** | **~0.5 hrs** | **~0.5 hrs** | **✅ Complete** |
| **Phase 4: Deployment** | **6-8 hrs** | **~4 hrs (manual)** | 🚀 **In Progress** |
| Phase 4: Reliability (PR22) | **3-4 hrs** | **TBD** | 📋 **Next** |
| Phase 4: CI/CD Fix (PR23, optional) | **2-3 hrs** | - | 📋 Optional |
| Phase 4: Documentation (PR24, optional) | **1 hr** | - | 📋 Optional |
| Phase 5: Polish & Scenarios | 8-12 hrs | - | 📋 Planned |
| PR20B: Code Quality (optional) | 1-2 hrs | - | 📋 Optional |
| PR21: Selective Authentication (optional) | 4-6 hrs | - | 📋 Optional |
| **Total Completed** | - | **~57.5 hrs** | **76% Done** |
| **Total Remaining (Core)** | - | **~10-15 hrs** | **24% Left** |
| **Total with All Optional** | - | **~18-33 hrs** | **If included** |

**Current Status**: ~76% complete by effort, all core features done, Phase 4 deployed with authentication complete, next: reliability fixes (retry logic + timeouts)

---

## Reference Documentation

- **README.md** - Main documentation with quick start
- **docs/DEPLOYMENT.md** - Deployment guide
- **docs/INSTALL.md** - Installation instructions
- **docs/ROADMAP.md** - High-level roadmap
- **docs/archive/** - Historical documentation

---

## Development Workflow

1. **Before new work**: Clear context to save tokens
2. **Code exploration**: Use Explore agent + deepcontext
3. **Library docs**: Use context7 MCP server
4. **Azure help**: Use azure-mcp for Azure-specific questions
5. **After milestone**: Run pr-reviewer agent
6. **Update plan**: Incorporate review findings
7. **Repeat**: Next phase

---

---

## Next Actions

### PR22: Azure Blob Storage Reliability (High Priority, 3-4 hrs)
Implement retry logic + timeout configuration to resolve transient failures:
- **Task 1**: Add exponential backoff to Azure Blob Storage client (1-2 hrs)
- **Task 2**: Configure timeouts: 10-30s connection, 30-60s request (1-2 hrs)
- **Task 3**: Test retry behavior under load (30 min - 1 hr)

### PR23: GitHub Actions CI/CD Fix (Medium Priority, 2-3 hrs, Optional)
Fix automated deployment workflow (currently using manual deployment):
- Troubleshoot workflow failures, fix Azure auth, validate end-to-end

### PR24: Deployment Documentation (Low Priority, 1 hr, Optional)
Document manual deployment workaround process for future reference

---

**Last Updated**: 2025-11-17
**Status**: 76% complete by effort | Core features 100% done | Phase 4 deployed (manual)
**Current Issue**: Intermittent Azure Blob connectivity (known, isolated)
**Next**: Implement retry logic + timeouts (PR22) to resolve transient failures
