# Factory Agent - Implementation Plan

**Last Updated**: 2025-11-22 (Updated: PR22 Critical Issue Identified - Branch Cannot Be Merged As-Is)
**Status**: Phase 3 Complete (100%) | Phase 4 In Progress (60% - Deployed + Auth Complete, CI/CD & Reliability Pending) | Phase 5 Planned
**Architecture**: React + FastAPI + Azure Container Apps + AI Foundry + Azure Blob Storage + Azure AD Auth

---

## CRITICAL ALERT: PR22 Branch Issue ⚠️

**BLOCKER**: PR22 WIP branch **CANNOT BE MERGED AS-IS** - It deletes 5 critical infrastructure commits.

**Problem Summary**:
- PR22 was branched from commit d8fd64b (Nov 17), BEFORE 5 recent infra commits (Nov 19-22)
- Merging PR22 would **DELETE** critical Bicep templates added in main:
  - `infra/backend.bicep` (283 lines)
  - `infra/frontend.bicep` (205 lines)
  - `infra/shared.bicep` (145 lines)
- Would **REVERT** split infrastructure back to old monolithic `infra/main.bicep`
- Includes unrelated frontend changes (724 lines in package.json, MainLayout, DashboardPage)

**What's Good in PR22** (salvageable):
- shared/blob_storage.py: ExponentialRetry policy with configurable retries
- shared/config.py: AZURE_BLOB_RETRY_TOTAL, AZURE_BLOB_INITIAL_BACKOFF, etc.
- .env.example: Retry/timeout documentation (lines 69-90)
- tests/test_blob_storage.py: 24 tests passing (100%)

**Solution**: Create clean branch `pr22-retry-logic-clean` by cherry-picking ONLY retry/timeout changes from PR22 onto main branch. DELETE old PR22 branch to avoid confusion.

---

---

## Executive Summary

Factory Agent is a **feature-complete** Industry 4.0 monitoring application with AI-powered insights and supply chain traceability, now **deployed to Azure** with a **known reliability issue** to fix.

**Completed** (Phases 1-3):
- ✅ Backend: 21 REST API endpoints (metrics + traceability + AI chat)
- ✅ Frontend: 5 complete React pages with Material-UI (~4,900 lines of TypeScript)
- ✅ AI Chat: Azure AI Foundry integration with tool calling
- ✅ Supply Chain: End-to-end traceability with material-supplier linkage
- ✅ Testing: 162 backend tests (161 passing / 99.4% pass rate)
- ✅ Code Review: All critical and important issues resolved
- ✅ Authentication: Azure AD JWT validation module complete

**Deployed** (Phase 4 - 60% Complete):
- ✅ Infrastructure: Bicep templates (split backend/frontend), Dockerfiles, GitHub Actions workflows
- ✅ Deployment: Frontend + backend deployed to Azure Container Apps (manual deployment)
- ✅ Azure Blob Storage: Integrated and accessible
- ✅ Hybrid Development: Local dev + cloud data working
- ✅ Authentication: Azure AD JWT validation in backend/src/api/auth.py
- ⚠️ **PR22 BLOCKER**: Retry logic implemented but branch has fatal issues (deletes 5 critical infrastructure commits) - CANNOT MERGE AS-IS
  - Solution: Use PR22-FIX procedure to create clean branch with ONLY retry/timeout changes
  - Estimated time: 30-45 minutes
- ⏳ **CI/CD**: Infrastructure fixes completed (5 commits Nov 19-22), workflows ready for activation (blocked by PR22-FIX)
- ⚠️ **Known Issue**: 1 pre-existing test failure in test_whitespace_only_message (edge case validation, low impact)

**Next** (Phase 4 Continuation + Phase 5):
- Test and merge PR22 WIP branch (retry logic + timeout config already implemented)
- Activate GitHub Actions CI/CD workflows (infrastructure fixes complete)
- Fix pre-existing test failure (test_whitespace_only_message)
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

### Phase 4 Status: Deployment & Reliability (60% Complete)

**Current Situation** (2025-11-22):
- ✅ All core features complete (backend API, frontend, AI chat)
- ✅ Azure Blob Storage integrated and accessible
- ✅ Deployed to Azure Container Apps (manual deployment - working)
  - Frontend deployed to Azure Container Apps
  - Backend deployed to Azure Container Apps
  - Azure AD authentication functional
- ⏳ **PR22 WIP Branch** (Nov 18): Retry logic + timeout config implemented
  - ExponentialRetry policy configured
  - Timeout configuration added: AZURE_BLOB_RETRY_TOTAL=3, CONNECTION_TIMEOUT=30s, OPERATION_TIMEOUT=60s
  - Code written but NOT COMMITTED to main yet
  - Ready for testing and merge
- ⏳ **CI/CD Preparation**: 5 infrastructure commits (Nov 19-22)
  - Split Bicep templates (backend/frontend separate)
  - Replaced azure/arm-deploy with direct az CLI
  - Workflows ready for activation
- ⚠️ **Known Issue**: 1 pre-existing test failure (test_whitespace_only_message - edge case validation, low impact)

**Infrastructure Status**:
- ✅ `infra/shared.bicep` - Shared resources (Log Analytics, Container Environment, Managed Identity)
- ✅ `infra/backend.bicep` - Backend Container App + secrets (deployed)
- ✅ `infra/frontend.bicep` - Frontend Container App + Nginx config (deployed)
- ✅ `frontend/Dockerfile` - Multi-stage React build + Nginx (deployed)
- ✅ `backend/Dockerfile` - Python 3.11 + FastAPI (deployed)
- ⏳ `.github/workflows/deploy-frontend.yml` - CI/CD configured, infrastructure fixes complete (Nov 19-22)
- ⏳ `.github/workflows/deploy-backend.yml` - CI/CD configured, infrastructure fixes complete (Nov 19-22)
- ✅ Azure Blob Storage - Configured and tested with live data
- ⚠️ **Current State**: Manual deployment in use; CI/CD workflows ready for activation

### Immediate Priority: Complete Phase 4 Deployment

**PR22-FIX: Azure Blob Storage Retry Logic (Status: CRITICAL - BLOCKING)**

**ALERT**: Original PR22 branch **CANNOT BE MERGED** - it was branched from Nov 17 before 5 recent infrastructure commits and would delete critical Bicep templates (infra/backend.bicep, infra/frontend.bicep, infra/shared.bicep) if merged.

**Salvageable from PR22** (Good Code):
- ✅ **Retry Logic Implementation**:
  - ExponentialRetry policy with configurable max_retries (default: 3)
  - Backoff: initial=2s, increment_base=2
  - Configuration: AZURE_BLOB_RETRY_TOTAL, AZURE_BLOB_INITIAL_BACKOFF, AZURE_BLOB_INCREMENT_BASE
- ✅ **Timeout Configuration**:
  - Connection timeout: 30s (configurable via AZURE_BLOB_CONNECTION_TIMEOUT)
  - Operation timeout: 60s (configurable via AZURE_BLOB_OPERATION_TIMEOUT)
  - Environment variables documented in .env.example (lines 69-90)
- ✅ **Tests**: 24 blob storage tests, all passing

**Required Solution** (See "Next Actions" section for full instructions):
1. Create clean branch: `pr22-retry-logic-clean` from current main (64b616e)
2. Cherry-pick ONLY retry/timeout changes:
   - shared/blob_storage.py (ExponentialRetry implementation)
   - shared/config.py (timeout configuration variables)
   - .env.example (documentation)
   - tests/test_blob_storage.py (if any changes)
3. Verify: pytest passes (161/162 tests expected)
4. Merge clean branch to main
5. Delete old PR22 branch

**Estimated Effort**: 30-45 minutes
**Blocks**: CI/CD activation, Phase 4 completion

**CI/CD Activation (Status: Infrastructure Ready)**
- ✅ **Infrastructure Fixes Complete** (5 commits Nov 19-22):
  - Bicep templates split (backend/frontend separate)
  - azure/arm-deploy replaced with direct az CLI
  - Workflows configured with proper authentication
- ⏳ **Next Steps**:
  1. Test workflows manually via workflow_dispatch
  2. Resolve any authentication or deployment issues
  3. Activate automated deployments on push to main

**Test Failure Fix (Status: Identified, Low Priority)**
- ⚠️ **Issue**: test_whitespace_only_message expects 422/500, endpoint returns 200
- **Location**: tests/test_chat_integration.py:193
- **Impact**: Low (edge case validation, not core functionality)
- ⏳ **Next Steps**: Review chat endpoint validation logic, fix test or endpoint

**Alternatives: Optional Improvements**
- **PR21**: Selective Authentication (4-6 hours, security enhancement)
- **Deployment Documentation**: Document manual deployment process (1 hour)

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
- 21 REST API endpoints (all async with full type safety)
- 162 comprehensive tests (161 passing / 99.4% pass rate)
- 4 route modules (data, metrics, chat, traceability)
- Rate limiting (SlowAPI), CORS, input validation
- Async/await throughout FastAPI
- Azure AD JWT authentication

**Frontend**:
- ~4,900 lines of TypeScript (src/ only, excluding node_modules)
- 5 complete pages (Dashboard, Machines, Alerts, Traceability, Chat)
- 51+ reusable components
- 30+ type-safe API client methods
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
- ✅ All backend endpoints working (21 async endpoints)
- ✅ All React pages functional (5 pages, 51+ components)
- ✅ Type safety (Python type hints + TypeScript strict mode)
- ✅ Tests passing (161/162 = 99.4% pass rate)
- ✅ Deployed to Azure Container Apps (manual deployment)
- ⏳ CI/CD automation (infrastructure ready, workflows pending activation)

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
| **Phase 4: Deployment (Manual)** | **6-8 hrs** | **~4 hrs** | **✅ Complete** |
| Phase 4: PR22 Retry Logic (WIP) | **3-4 hrs** | **~2 hrs (code complete)** | ⏳ **Testing** |
| Phase 4: CI/CD Activation | **2-3 hrs** | **~1 hr (infra fixes)** | ⏳ **Activation** |
| Phase 4: Test Fix (optional) | **0.5 hrs** | - | 📋 Optional |
| Phase 5: Polish & Scenarios | 8-12 hrs | - | 📋 Planned |
| PR21: Selective Authentication (optional) | 4-6 hrs | - | 📋 Optional |
| **Total Completed** | - | **~61.5 hrs** | **82% Done** |
| **Total Remaining (Core)** | - | **~2-4 hrs** | **18% Left** |
| **Total with Phase 5** | - | **~10-16 hrs** | **If included** |

**Current Status**: ~82% complete by effort, all core features deployed, Phase 4 code complete (PR22 WIP ready for merge), next: test and merge PR22, activate CI/CD

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

### PR22-FIX: Recreate Retry Logic Branch (BLOCKING - 30-45 min)
**Status**: URGENT - Old PR22 cannot be merged, must create clean branch
**Priority**: CRITICAL - Blocks all further work

**Step-by-step Instructions**:

1. **Task 1**: Verify current state (5 min)
   ```bash
   git checkout main
   git log --oneline -5  # Verify latest commit is 64b616e
   ```

2. **Task 2**: Create clean feature branch (2 min)
   ```bash
   git checkout -b pr22-retry-logic-clean
   ```

3. **Task 3**: Cherry-pick ONLY retry/timeout changes from old PR22 (15 min)
   - Copy `shared/blob_storage.py` from PR22 (retry logic implementation)
   - Copy `shared/config.py` lines 43-48 (timeout config variables)
   - Copy `.env.example` lines 69-90 (retry/timeout documentation)
   - Verify `tests/test_blob_storage.py` (all 24 tests should pass)
   - **DO NOT** copy any other changes (frontend, package.json, Dockerfiles, etc.)

4. **Task 4**: Validate changes (10 min)
   ```bash
   # Run full test suite
   pytest
   # Expected: 161/162 passing (same as before)

   # Check git diff to verify ONLY retry/timeout files changed
   git diff main
   ```

5. **Task 5**: Commit changes (2 min)
   ```bash
   git add .
   git commit -m "feat: Add Azure Blob Storage retry logic and timeout configuration

   - Implement ExponentialRetry policy with configurable max_retries (default: 3)
   - Add connection timeout (default: 30s) and operation timeout (default: 60s)
   - Configuration via environment variables:
     * AZURE_BLOB_RETRY_TOTAL
     * AZURE_BLOB_INITIAL_BACKOFF
     * AZURE_BLOB_INCREMENT_BASE
     * AZURE_BLOB_CONNECTION_TIMEOUT
     * AZURE_BLOB_OPERATION_TIMEOUT
   - Documented in .env.example

   See PR22 for original implementation details."
   ```

6. **Task 6**: Merge to main (2 min)
   ```bash
   git checkout main
   git merge pr22-retry-logic-clean
   git push origin main
   ```

7. **Task 7**: Delete old PR22 branch (2 min)
   ```bash
   git branch -D pr22-feature  # (or whatever the old branch name is)
   git push origin --delete pr22-feature
   ```

8. **Task 8**: Verify merge (2 min)
   ```bash
   git log --oneline -3  # Confirm new commit on main
   pytest  # Run full test suite one more time
   ```

**Why This Approach**:
- Preserves the good retry logic implementation from PR22
- Avoids deleting 5 critical infrastructure commits
- Creates clean, focused PR with ONLY retry/timeout changes
- Prevents confusion with old PR22 branch still existing

### PR22: Test and Merge Retry Logic (BLOCKED - See PR22-FIX Above)
**Status**: BLOCKED - Cannot merge as-is, must use PR22-FIX approach instead
- ~~Task 1: Review PR22 WIP branch changes~~
- ~~Task 2: Run backend tests to validate retry behavior~~
- ~~Task 3: Merge PR22 WIP to main branch~~
- ~~Task 4: Deploy updated backend to Azure~~
**Action**: Use PR22-FIX procedure above instead

### PR23: Activate GitHub Actions CI/CD (Medium Priority, 1-2 hrs)
**Status**: Infrastructure fixes complete (5 commits Nov 19-22), workflows ready
- **Task 1**: Test backend workflow via workflow_dispatch (30 min)
- **Task 2**: Test frontend workflow via workflow_dispatch (30 min)
- **Task 3**: Resolve any authentication or deployment issues (30-60 min)
- **Task 4**: Enable automated deployments on push to main (5 min)

### Fix test_whitespace_only_message (Low Priority, 15-30 min, Optional)
**Status**: 1 pre-existing test failure (edge case validation)
- **Task 1**: Review chat endpoint validation logic (10 min)
- **Task 2**: Fix test expectation or add input validation (10-20 min)

### PR24: Deployment Documentation (Low Priority, 1 hr, Optional)
Document deployment process and infrastructure decisions for future reference

---

**Last Updated**: 2025-11-22 (CRITICAL: PR22 Branch Issue Identified)
**Status**: 82% complete by effort | Core features 100% done | Phase 4 deployed (manual) | PR22 BLOCKED by branch conflict
**Current State**: PR22 branch cannot be merged as-is (deletes 5 critical infrastructure commits); must use PR22-FIX procedure to cherry-pick retry logic onto clean branch
**Critical Blocker**: PR22-FIX procedure (30-45 min) must be completed BEFORE CI/CD activation
**Next Steps** (in order):
1. **URGENT**: Complete PR22-FIX procedure (clean branch with ONLY retry/timeout changes) - 30-45 min
2. Activate CI/CD workflows (blocked until PR22-FIX complete) - 1-2 hrs
3. Fix test_whitespace_only_message (optional, low priority) - 15-30 min
