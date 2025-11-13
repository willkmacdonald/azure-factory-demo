# Azure Migration Implementation Plan
## Factory Agent: Streamlit/CLI → React + Azure Container Apps

**Version:** 2.0
**Created:** 2025-01-01
**Target Timeline:** 4-5 weeks
**Architecture:** Azure Container Apps + FastAPI + React

---

## Current Status

**Note**: This project has parallel development tracks:
- **React/Azure Migration Track** (this plan): PRs 6-17 for API and frontend development
- **Backend Traceability Track** (feature branch): PRs 13-14 for supply chain data models (ready to merge)

### React/Azure Migration Track

**Phase**: Phase 3 - React Frontend Development (IN PROGRESS)
**Last Completed**: PR13 - Metrics Dashboard & Charts (2025-11-06)
**Active PR**: Merging backend traceability PRs 13-14 from feature branch

### Summary
Phase 1 (Backend API Foundation), Phase 2 (Azure Blob Storage Integration), and foundational setup for Phase 3 (React Frontend) are now complete! PR9 successfully implemented async blob storage operations with dual-mode support (local JSON and Azure Blob Storage). PR10 delivered comprehensive test coverage with 47 tests across both storage backends, plus critical dependency fixes. React project structure is now in place at `frontend/` with Vite + React + TypeScript, Material-UI, Recharts, and Axios dependencies.

Additionally, parallel backend work has completed supply chain traceability with Suppliers, MaterialLots, Orders, and ProductionBatch models (feature branch PRs 13-14, ready to merge).

**Progress - Phase 1**: 3/3 core PRs complete (100%)
- PR6: Async Chat API ✅ COMPLETE
- PR7: Production Hardening & Rate Limiting ✅ COMPLETE
- PR8: Conversation History Validation ✅ COMPLETE

**Progress - Phase 2**: 3/3 PRs complete (100%)
- Azure Storage Account Setup ✅ COMPLETE
- PR9: Blob Storage Implementation ✅ COMPLETE
- PR10: Comprehensive Testing & Dependency Fixes ✅ COMPLETE

**Progress - Phase 3 (React Frontend)**: 3/7 PRs complete (43%)
- PR11: Core API Client & Data Models ✅ COMPLETE
- PR12: Dashboard Layout & Navigation ✅ COMPLETE
- PR13: Metrics Dashboard & Charts ✅ COMPLETE
- PR14: Machine Status & Alerts View (IN PROGRESS on main)
- PR15: AI Chat Interface (PLANNED)
- PR16: Authentication & Azure AD Integration (PLANNED)
- PR17: Deployment & CI/CD (PLANNED)

**Progress - Backend Traceability** (parallel feature branch, ready to merge):
- Traceability PR13: Pydantic Models & Entity Generation ✅ COMPLETE
- Traceability PR14: ProductionBatch Model & Generation ✅ COMPLETE

---

## ✅ Completed PRs (Archive)

### PR12: Dashboard Layout & Navigation (Completed 2025-11-03)
**Status**: COMPLETED
**Priority**: HIGH
**Effort**: 3-4 hours (completed)
**Dependencies**: PR11 complete (Core API Client & Data Models)

#### Overview
PR12 successfully implements the React frontend navigation infrastructure with Material-UI components and React Router v6. This establishes the visual framework for Phase 3 of the Factory Agent project.

#### Completed Tasks

- [x] Create main dashboard layout with MUI AppBar and Drawer
  - **Status**: IMPLEMENTED
  - **Files Created**: frontend/src/components/layout/MainLayout.tsx (203 lines)
  - **Implementation Details**:
    - Responsive AppBar with title and hamburger menu
    - Persistent Drawer navigation on desktop (≥md breakpoint)
    - Temporary (overlay) Drawer navigation on mobile (<md breakpoint)
    - Active route highlighting in navigation
    - React Router Outlet for rendering child routes
    - Material Design icons for navigation items
    - Navigation Items: Dashboard (/), Machines (/machines), Alerts (/alerts), AI Chat (/chat)
    - TypeScript with complete type annotations
    - Uses MUI hooks: useTheme(), useMediaQuery()
    - Uses React Router hooks: useNavigate(), useLocation()
    - Accessibility: ARIA labels, proper semantic HTML

- [x] Add navigation structure with React Router
  - **Status**: IMPLEMENTED
  - **Files Modified**: frontend/src/App.tsx, frontend/src/main.tsx
  - **Implementation Details**:
    - Wrapped App component with BrowserRouter in main.tsx
    - Added React Router Routes and Route configuration
    - Configured nested routes with MainLayout as parent
    - Routes: Dashboard (/), Machines (/machines), Alerts (/alerts), Chat (/chat)
    - Active route styling in navigation
    - Route transitions with proper outlet handling
    - Clean, minimal router setup

- [x] Create placeholder page components
  - **Status**: IMPLEMENTED
  - **Files Created**:
    - frontend/src/pages/DashboardPage.tsx (45 lines)
    - frontend/src/pages/MachinesPage.tsx (45 lines)
    - frontend/src/pages/AlertsPage.tsx (45 lines)
    - frontend/src/pages/ChatPage.tsx (45 lines)
  - **Details**:
    - All pages follow consistent structure
    - Container with page title and subtitle
    - Placeholder content indicating future functionality
    - Links to upcoming PR documentation

#### Files Created/Modified
**Created**:
- `frontend/src/components/layout/MainLayout.tsx` - Main layout component (203 lines)
- `frontend/src/pages/DashboardPage.tsx` - Dashboard placeholder (45 lines)
- `frontend/src/pages/MachinesPage.tsx` - Machines placeholder (45 lines)
- `frontend/src/pages/AlertsPage.tsx` - Alerts placeholder (45 lines)
- `frontend/src/pages/ChatPage.tsx` - Chat placeholder (45 lines)
- `PR12-COMPLETION.md` - Detailed completion documentation

**Modified**:
- `frontend/src/main.tsx` - Added BrowserRouter
- `frontend/src/App.tsx` - Refactored to use React Router
- `frontend/package.json` - Added react-router-dom dependency

#### Dependencies Added
- `react-router-dom`: Latest version for client-side routing

#### Build Verification
- TypeScript compilation: ✅ No errors
- Production build: ✅ Success (384.23 KB, gzipped: 123.18 KB)
- Dev server: ✅ Running cleanly on http://localhost:5173/
- No console errors

#### Testing Results
- Desktop layout with persistent drawer: ✅ Working
- Mobile layout with overlay drawer and hamburger menu: ✅ Working
- Navigation between routes: ✅ All routes render placeholder pages
- Active route highlighting: ✅ Correct highlighting
- Drawer closes on mobile after navigation: ✅ Proper behavior

#### Code Review Standards Met
✅ **Type Hints**: All components use TypeScript with complete type annotations
✅ **React Patterns**: Functional components with hooks (useState, useTheme, useMediaQuery, useNavigate, useLocation)
✅ **Material-UI**: Proper use of MUI components, responsive design with sx prop
✅ **React Router v6**: BrowserRouter, nested routes with Outlet, modern patterns
✅ **Responsive Design**: Mobile-first with useMediaQuery for breakpoints
✅ **Documentation**: JSDoc comments for all components

#### Completion Summary
PR12 successfully established the navigation infrastructure and responsive layout foundation for the React frontend. The implementation ensures:
- Responsive design works across all screen sizes
- Navigation structure is clean and intuitive
- All routes properly configured with React Router v6
- Foundation is now ready for implementing feature-rich pages in subsequent PRs
- TypeScript type safety throughout
- Material Design compliance with MUI components

**Key Commits**:
- Dashboard Layout & Navigation implementation
- React Router setup with nested routes
- Placeholder page components

---

### PR10: Comprehensive Testing for Azure Blob Storage Integration (Completed 2025-11-03)
**Status**: COMPLETED
**Priority**: Critical (Validates Phase 2 completion)
**Effort**: 3-4 hours (completed)
**Dependencies**: PR9 complete (blob storage implementation)

#### Completed Tasks

- [x] Add comprehensive test suite for blob storage operations
  - **Status**: IMPLEMENTED
  - **Files Created**: tests/test_blob_storage.py, tests/test_data_async.py
  - **Test Count**: 47 comprehensive tests total
  - **Implementation Details**:
    - **tests/test_blob_storage.py** (24 tests):
      - Blob upload and download operations (success paths)
      - Blob existence checking functionality
      - Authentication error handling and recovery
      - Blob not found scenarios with fallback behavior
      - Network error scenarios with retry logic
      - Connection string validation
      - JSON parsing and data integrity
      - Client cleanup and resource management
    - **tests/test_data_async.py** (23 tests):
      - Load from local JSON file mode
      - Save to local JSON file mode
      - Load from Azure Blob Storage mode
      - Save to Azure Blob Storage mode
      - Data consistency verification (local round-trip)
      - Data consistency verification (Azure round-trip)
      - Fallback behavior (missing blob generates fresh data)
      - Storage mode configuration verification
      - Invalid storage mode error handling
      - Concurrent async operations validation
      - Large data transfer handling (14,400+ records)
      - Error propagation and logging
  - **Result**: All 47 tests pass with comprehensive coverage

- [x] Fix critical dependency issues identified in code review
  - **Status**: FIXED
  - **Files Modified**: requirements.txt
  - **Dependency Updates**:
    - `aiofiles`: 25.0.0 → 24.1.0 (version compatibility fix)
    - `azure-storage-blob`: Added >=12.15.0 (explicit version requirement)
    - `aiohttp`: Added >=3.8.0 (async HTTP client for blob operations)
    - `pytest-asyncio`: 1.2.0 → 0.21.0 (async test framework compatibility)
  - **Result**: All dependencies properly pinned and compatible

- [x] Fix type hints and test implementation bugs
  - **Status**: FIXED
  - **Issues Resolved**:
    - Added complete type hints to all test fixtures (previously missing)
    - Fixed large data test loop variable collision (now generates exactly 14,400 records)
    - Ensured all async test patterns follow pytest-asyncio conventions
    - Added proper docstrings to all test functions
  - **Result**: No type errors, clean test execution

- [x] Verify all existing tests still pass with new async functions
  - **Status**: VERIFIED
  - **Tests Confirmed Passing**:
    - All 32 existing tests from PR6-PR8 (chat, validation, integration)
    - No regressions from new async data functions
    - Full test suite compatibility validated
  - **Result**: 79+ total tests passing (32 existing + 47 new)

#### Test Coverage Summary

**Storage Mode Validation**:
- Local JSON mode: 12 tests covering read/write/consistency
- Azure Blob mode: 12 tests covering read/write/consistency
- Mode switching: 4 tests for configuration and errors
- Concurrent operations: 3 tests for async safety

**Error Scenarios Covered**:
- Authentication failures (3 tests)
- Network errors with retry logic (4 tests)
- Missing blob/file scenarios (2 tests)
- Invalid configuration (2 tests)
- Data corruption/parsing errors (2 tests)

**Quality Metrics**:
- Test execution: All 47 tests pass without failures
- Type safety: Zero type errors across test suite
- Async patterns: Proper await usage throughout
- Documentation: Comprehensive docstrings on all tests
- Edge cases: Large data, special characters, concurrent access tested

#### Commits
- Commit e4bebc4: "fix: PR10 review fixes - dependencies, type hints, test bug"
- Original PR10 tests (test_blob_storage.py, test_data_async.py)

#### Completion Summary
PR10 successfully delivered comprehensive test coverage for Azure Blob Storage integration. The implementation ensures:
- 47 new tests covering all storage paths and error scenarios
- Critical dependency compatibility issues resolved
- Type hints complete throughout test suite
- Both local JSON and Azure Blob Storage modes thoroughly tested
- Data integrity validated across all storage transitions
- Error handling properly tested for production resilience
- All 79+ project tests passing with zero regressions
- Ready for production deployment with high confidence

---

### PR9: Azure Blob Storage Implementation (Completed 2025-11-03)
**Status**: COMPLETED
**Priority**: High (Cloud data persistence for Azure deployment)
**Effort**: 4-5 hours (completed)
**Dependencies**: Phase 1 complete (PR6-PR8), Azure Storage Account created

#### Completed Tasks

- [x] Install Azure Storage Blob SDK
  - **Status**: IMPLEMENTED
  - **Files Modified**: backend/requirements.txt
  - **Result**: `azure-storage-blob>=12.15.0` added and installed

- [x] Create async blob storage client wrapper
  - **Status**: IMPLEMENTED
  - **Files Created**: shared/blob_storage.py
  - **Implementation Details**:
    - Created `BlobStorageClient` class with async methods
    - Implemented `async def upload_blob(container, blob_name, data)` - writes JSON to blob
    - Implemented `async def download_blob(container, blob_name)` - reads JSON from blob
    - Implemented `async def blob_exists()` - checks blob existence in container
    - Connection string loaded from environment variable `AZURE_STORAGE_CONNECTION_STRING`
    - Retry logic implemented for transient failures (3 retries with exponential backoff)
    - Proper error handling with descriptive messages distinguishing auth errors, blob not found, network errors
  - **Result**: All methods are async and compatible with FastAPI routes

- [x] Update data.py for dual-storage support
  - **Status**: IMPLEMENTED
  - **Files Modified**: shared/data.py
  - **Implementation Details**:
    - Imported `BlobStorageClient` from blob_storage.py
    - Created `load_data_async()` - async version checking STORAGE_MODE
      - If azure: downloads from blob using `BlobStorageClient`
      - If local: reads from JSON file with `aiofiles`
      - Includes fallback logic: if blob missing, generates fresh data and saves
    - Created `save_data_async()` - async version supporting both modes
      - If azure: uploads to blob using `BlobStorageClient`
      - If local: writes to JSON file with `aiofiles`
      - Handles write errors gracefully
    - Kept existing sync functions (`load_data()`, `save_data()`) for CLI compatibility
  - **Result**: Both async functions work seamlessly in FastAPI routes

- [x] Add error handling for storage operations
  - **Status**: IMPLEMENTED
  - **Files Modified**: shared/data.py, shared/config.py
  - **Implementation Details**:
    - Wrapped blob operations in try/except blocks
    - Handle specific Azure exceptions:
      - `BlobNotFound`: Generates fresh data on first access
      - `AuthenticationError`: Logs credentials issue, fails with clear message
      - `ServiceRequestError`: Logs network issue, retries with exponential backoff (3 retries)
    - Added logging with request context
    - Connection validation at startup with health check
    - Meaningful error messages for debugging
  - **Result**: Proper error handling with logging and automatic retry logic

#### Testing Summary
- Integration tests in `tests/test_chat_integration.py` validate:
  - Data can be written to Azure Blob Storage
  - Data can be read from Azure Blob Storage
  - Both local JSON and Azure modes produce identical results
  - Fallback behavior works (missing blob generates fresh data)
  - Error scenarios handled gracefully

#### Configuration Applied
- **STORAGE_MODE environment variable**: Controls behavior (local/azure)
- **Default behavior**: local mode (JSON file) for development
- **Azure mode**: Enabled when STORAGE_MODE=azure and AZURE_STORAGE_CONNECTION_STRING set
- **.env.example updated**: Added clear documentation for storage configuration

#### Completion Summary
PR9 successfully implemented async blob storage operations with dual-mode support. The implementation ensures:
- FastAPI routes can read/write data to Azure Blob Storage
- Local development continues using JSON files without Azure dependencies
- Both storage modes fully tested and validated
- Proper async/await patterns (no blocking I/O)
- Comprehensive error handling with automatic retries
- Backward compatibility maintained (existing sync functions still available)
- Ready for production deployment with cloud data persistence

---

### Azure Storage Account Setup (Completed 2025-11-03)
**Status**: SETUP COMPLETE (Prerequisite for PR9)
**Type**: Azure Infrastructure Setup (Not a PR, but critical prerequisite)

#### What Was Created
- **Storage Account**: `factoryagentdata` (Standard_LRS tier, Hot access tier, East US region)
- **Blob Container**: `factory-data` (private access level - no public access)
- **Connection String**: Added to `.env` as `AZURE_STORAGE_CONNECTION_STRING`
- **Documentation**: Created `AZURE_STORAGE_SETUP.md` with detailed setup steps and troubleshooting

#### Configuration Details
- **Storage Mode Configuration**:
  - `STORAGE_MODE=local` (default for local development)
  - `AZURE_STORAGE_CONNECTION_STRING` added to `.env` for cloud connectivity
  - `AZURE_BLOB_CONTAINER=factory-data` configured for blob operations
- **Environment Variables Updated**:
  - `.env.example` updated with comprehensive documentation
  - Includes instructions for setting up storage account manually or via Azure CLI
  - Clear examples and comments for developers
- **Security Configuration**:
  - HTTPS-only transport (enforced by Azure)
  - Blob public access disabled (private container)
  - Encryption at rest (default Azure encryption)
  - No shared access signatures (SAS) used - connection string based auth

#### Cost Analysis
- **Estimated Monthly Cost**: ~$0.01-0.06 (negligible for demo)
- **Storage Tier**: Hot tier (appropriate for frequently accessed demo data)
- **Replication**: Standard-LRS (cost-effective, suitable for non-critical demo data)
- **Cost-saving notes**: Blob storage charges minimal amounts for demo data volumes

#### Testing Status
- Manual verification: Successfully created storage account via Azure Portal
- Connection verification: Credentials validated and stored securely
- Container verification: Blob container `factory-data` created and accessible
- Security verification: Public access disabled, HTTPS enforced

#### Completion Summary
Azure Storage Account setup successfully completed. The storage infrastructure is now ready to support Phase 2 implementation. PR9 can proceed immediately with implementing the async blob operations in the application code. All necessary environment variables are configured, and developers can switch between local and Azure storage modes via the `STORAGE_MODE` configuration.

---

### PR8: Conversation History Validation & Error Messages (Completed 2025-11-02)
**Status**: COMPLETED
**Priority**: Medium (Data integrity & better error messages)
**Effort**: 3-4 hours (completed)
**Source**: pr-reviewer & security-scanner deferred items from PR6

#### Completed Tasks

- [x] Validate conversation history with strict role enforcement
  - **Status**: IMPLEMENTED
  - **Implementation**: Updated ChatMessage model with role validator in backend/src/api/routes/chat.py
  - **Files Modified**: backend/src/api/routes/chat.py
  - **Result**: Only 'user' and 'assistant' roles allowed; invalid roles rejected with 422 error
  - **Details**:
    - Added `@field_validator('role')` to enforce allowed_roles = {"user", "assistant"}
    - Added `@field_validator('content')` to reject empty/whitespace-only content
    - Comprehensive error messages guide users to correct usage

- [x] Implement environment-based error messages
  - **Status**: IMPLEMENTED
  - **Implementation**: Added DEBUG config variable and conditional error detail formatting
  - **Files Modified**: shared/config.py, backend/src/api/routes/chat.py, .env.example
  - **Result**: Production errors hide internal details, development mode shows full diagnostics
  - **Details**:
    - Added `DEBUG` boolean config (default: False for production security)
    - Development (DEBUG=True): Returns detailed error messages with stack traces
    - Production (DEBUG=False): Returns generic "An error occurred" message
    - Documented in .env.example with clear security recommendations

- [x] Add input sanitization tests
  - **Status**: IMPLEMENTED
  - **Implementation**: Created comprehensive test suites for validation logic
  - **Files Created**: tests/test_chat_api.py, tests/test_chat_integration.py
  - **Result**: 32 tests covering all validation scenarios
  - **Coverage**:
    - ChatMessage validation: 9 tests (valid/invalid roles, empty content, length limits)
    - ChatRequest validation: 9 tests (message length, history limits, total size)
    - Edge cases: 4 tests (case sensitivity, Unicode, special characters)
    - Integration tests: 10 tests (API rejection, environment-based errors)

#### Testing Summary
- All 32 tests passing (22 unit tests + 10 integration tests)
- Validated malformed history rejection (invalid roles, empty content, oversized)
- Confirmed environment-based error behavior (dev vs production modes)
- Tested edge cases (Unicode, special characters, whitespace handling)
- Integration tests verify 422 Unprocessable Entity for validation failures

#### Completion Summary
PR8 successfully implemented comprehensive conversation history validation and environment-based error messages. The implementation ensures:
- Strict role enforcement prevents malformed history from reaching Azure OpenAI API
- Empty/whitespace-only content is rejected at validation layer
- Production deployments hide internal error details (security)
- Development mode provides detailed diagnostics for debugging
- All validation logic thoroughly tested with 32 comprehensive tests
- Ready for production deployment with confidence

---

### PR7: Production Hardening - Rate Limiting & CORS (Completed 2025-11-02)
**Status**: COMPLETED
**Priority**: High (Production-critical before public deployment)
**Effort**: 6-8 hours (completed)
**Source**: pr-reviewer & security-scanner deferred items

#### Completed Tasks

- [x] Implement rate limiting with slowapi decorator
  - **Status**: IMPLEMENTED
  - **Implementation**: Added rate limiter to all public endpoints
  - **Files Modified**: backend/src/api/main.py, backend/src/api/routes/chat.py
  - **Result**: DoS protection with 10 req/min for chat endpoint, 5 req/min for setup

- [x] Restrict CORS configuration to trusted origins
  - **Status**: IMPLEMENTED
  - **Implementation**: Configured CORS middleware with environment-based allowed origins
  - **Files Modified**: backend/src/api/main.py, shared/config.py
  - **Result**: Cross-origin requests limited to configured domains (localhost:3000 dev, restricted in production)

- [x] Add authentication endpoint placeholder
  - **Status**: IMPLEMENTED
  - **Implementation**: Added comment blocks documenting Azure AD JWT validation integration point
  - **Files Modified**: backend/src/api/routes/chat.py, backend/src/api/auth.py
  - **Result**: Clear documentation for Phase 5 Azure AD authentication integration

#### Testing Summary
- Rate limiting tested with rapid request sequences
- CORS headers verified for allowed/blocked origins
- 429 Too Many Requests error responses verified
- Health check endpoint confirmed not rate-limited (for monitoring)

#### Completion Summary
PR7 successfully addressed all production hardening requirements identified by pr-reviewer and security-scanner. The implementation ensures:
- Public endpoints are protected from DoS attacks
- CORS only allows configured origins
- Authentication integration point documented for future phases
- Health check endpoint remains accessible for monitoring
- Ready for deployment to Azure Container Apps

---

### PR6: Async Chat API Endpoint - All Issues Fixed (Completed 2025-11-02)
**Status**: COMPLETED
**Priority**: Critical (blocks production)
**Effort**: 8-10 hours (completed)
**Source**: pr-reviewer + security-scanner findings

#### Critical Issues (ALL COMPLETED)

- [x] Fix synchronous file I/O in async context (shared/data.py:96-113)
  - **Status**: FIXED
  - **Implementation**: Created `load_data_async()` using `aiofiles` library
  - **Files Modified**: shared/data.py
  - **Result**: FastAPI routes now use async file I/O without blocking event loop

- [x] Fix synchronous metrics functions in async context (shared/metrics.py:37-284)
  - **Status**: FIXED
  - **Implementation**: All metrics functions now async-compatible
  - **Files Modified**: shared/metrics.py
  - **Result**: Tool execution in async context no longer blocks

- [x] Fix missing type hints on chat models (backend/src/api/routes/chat.py:18-23)
  - **Status**: FIXED
  - **Implementation**: Created `ChatMessage` Pydantic model with typed `role` and `content` fields
  - **Files Modified**: backend/src/api/routes/chat.py, shared/models.py
  - **Result**: Full type safety on all chat data structures

#### Important Issues (ALL COMPLETED)

- [x] Add request ID and timing logs (backend/src/api/routes/chat.py:90-147)
  - **Status**: FIXED
  - **Implementation**:
    - Added uuid4 request_id generation
    - Log start_time and end_time for all requests
    - Structured logging with request context and extra fields
  - **Files Modified**: backend/src/api/routes/chat.py
  - **Result**: Full request tracing and performance metrics for debugging

- [x] Improve error handling in get_openai_client (backend/src/api/routes/chat.py:47-92)
  - **Status**: FIXED
  - **Implementation**:
    - Separate validation for endpoint and API key
    - Format validation for endpoints
    - Try/except wrapper with HTTPException
  - **Files Modified**: backend/src/api/routes/chat.py
  - **Result**: Clear error messages on initialization failures

- [x] Externalize hardcoded API version (shared/config.py:13, .env.example:13-16)
  - **Status**: FIXED
  - **Implementation**:
    - Added AZURE_API_VERSION to config.py with default "2024-08-01-preview"
    - Updated .env.example with new variable
  - **Files Modified**: shared/config.py, .env.example
  - **Result**: API version now configurable per deployment

- [x] Validate input lengths and add history restrictions (backend/src/api/routes/chat.py:30-39)
  - **Status**: FIXED
  - **Implementation**:
    - Message field: max_length=2000
    - History field: max_items=50
    - Prevents token limit exceeded and API failures
  - **Files Modified**: backend/src/api/routes/chat.py, shared/models.py
  - **Result**: Validated user inputs prevent unexpected API costs

- [x] Sanitize user input for prompt injection (shared/chat_service.py:31-82, :307-309)
  - **Status**: FIXED
  - **Implementation**:
    - Created `sanitize_user_input()` function
    - Detects injection patterns (suspicious tokens)
    - Applied in get_chat_response() call
  - **Files Modified**: shared/chat_service.py
  - **Result**: Protection against prompt injection attacks

#### Production Hardening (Noted - To Be Addressed in Future PRs)

- [ ] Implement CORS restrictions (backend/src/api/main.py:56-77) - Deferred to PR7
- [ ] Add authentication placeholder (backend/src/api/routes/chat.py:63) - Deferred to Phase 5
- [ ] Implement rate limiting (backend/src/api/routes/chat.py:63) - Deferred to PR7
- [ ] Sanitize conversation history (backend/src/api/routes/chat.py:29) - Deferred to next PR
- [ ] Environment-based error messages (backend/src/api/routes/chat.py:106) - Deferred to next PR

#### Testing Summary
- All asyncio tests pass (6/6)
- Tests verify: system prompt, tool execution, chat responses, conversation history
- Request ID and timing logs verified
- Input validation tested with boundary conditions
- Error handling verified for missing credentials

#### Completion Summary
PR6 successfully addressed all critical async/sync issues and important security/quality concerns identified by pr-reviewer and security-scanner. The implementation ensures:
- FastAPI routes properly handle async operations without blocking
- Security vulnerabilities fixed (input validation, prompt injection protection)
- Full type safety with Pydantic models
- Production-grade error handling and request tracing
- Ready for deployment with optional hardening (CORS, auth, rate limiting)

---


## Backlog - Future Enhancements

### Security Hardening Tasks (Post-PR8 - From security-scanner Review)

**Review Date**: 2025-11-02
**Priority Levels**: Critical (pre-production), High (quick wins), Medium (long-term hardening), Low (enhancements)

#### Critical Priority - Must Fix Before Production Deployment

- [ ] Rotate API Keys (Manual Task - Not Code)
  - **Priority**: Critical
  - **Effort**: Quick (15 minutes manual work)
  - **Context**: API keys were exposed in .env file (though protected by .gitignore and never committed). Per security best practices, rotate both Azure OpenAI and OpenAI API keys.
  - **Steps**:
    1. Azure OpenAI: Go to Azure Portal → Keys and Endpoint → Regenerate
    2. OpenAI: Go to OpenAI Platform → API Keys → Revoke current key → Create new key
    3. Update local .env with new keys
    4. Update all Azure Container Apps environment secrets (via Azure Portal or CLI)
  - **Impact**: Prevents potential unauthorized API usage if keys were exposed elsewhere

#### High Priority - Quick Security Wins (Do These Next)

- [ ] Add input validation to SetupRequest.days parameter (backend/src/api/routes/data.py:56-62)
  - **Priority**: High
  - **Effort**: Quick (5 minutes)
  - **Context**: Prevents resource exhaustion via excessive data generation requests. Currently accepts any integer for days parameter.
  - **Implementation**:
    ```python
    from pydantic import Field

    class SetupRequest(BaseModel):
        days: int = Field(
            default=30,
            ge=1,
            le=365,
            description="Number of days of production data to generate (1-365)"
        )
    ```
  - **Rationale**: Limits data generation to 1-365 days; requesting 10000+ days could crash the application

- [ ] Add startup warning for DEBUG mode (backend/src/api/main.py)
  - **Priority**: High
  - **Effort**: Quick (10 minutes)
  - **Context**: Prevents accidental production deployment with DEBUG=true, which exposes internal error details to clients.
  - **Implementation**:
    ```python
    import logging
    from shared.config import DEBUG

    logger = logging.getLogger(__name__)

    if DEBUG:
        logger.warning(
            "⚠️  DEBUG MODE ENABLED - Detailed errors will be exposed to clients. "
            "Set DEBUG=false for production deployments."
        )
    ```
  - **Rationale**: Verbose error messages in production can leak system information to attackers

#### Medium Priority - Production Hardening (Do After Demo Phase)

- [ ] Implement Hybrid Secret Management (shared/config.py, backend/src/api/routes/chat.py)
  - **Priority**: Medium
  - **Effort**: Medium (2-3 hours)
  - **Context**: Currently uses plaintext .env files. Production deployments need Azure Key Vault or Managed Identity.
  - **Features**:
    1. Azure Managed Identity for Azure OpenAI (eliminates API keys entirely)
    2. Azure Key Vault integration for OpenAI API key
    3. Fallback to environment variables for local development compatibility
    4. Configuration via SECRETS_BACKEND environment variable (env, keyvault, managed-identity)
  - **Implementation Strategy**:
    - Create secrets.py with pluggable backend system
    - DefaultAzureCredential for Managed Identity in containers
    - ChainedTokenCredential for local dev (uses .env, then MSAL if available)
    - Update config.py to use new secrets manager
    - Update requirements.txt: `azure-keyvault-secrets`, `azure-identity`
  - **Rationale**: Managed Identity eliminates key rotation, Key Vault provides audit trails and encryption at rest

- [ ] Add rate limiting to read-only endpoints (backend/src/api/routes/metrics.py, data.py)
  - **Priority**: Medium
  - **Effort**: Medium (30 minutes)
  - **Context**: Currently rate limiting only on /api/chat (expensive endpoint). Read-only endpoints are unprotected.
  - **Protected endpoints**: /api/oee, /api/scrap, /api/quality, /api/downtime, /api/stats, /api/machines, /api/date-range
  - **Implementation**:
    ```python
    from slowapi import Limiter
    from slowapi.util import get_remote_address

    limiter = Limiter(key_func=get_remote_address)

    @limiter.limit("60/minute")
    async def get_oee(...):
        ...
    ```
  - **Rate limits**: 60 req/min for reads (more generous than 10 req/min for writes)
  - **Rationale**: Prevents scraping and DDoS attacks on data endpoints

- [ ] Enhance Prompt Injection Protection (shared/chat_service.py:31-82)
  - **Priority**: Medium
  - **Effort**: Medium (2-3 hours)
  - **Context**: Current implementation only logs suspicious patterns; production needs to block them.
  - **Enhancements**:
    1. Unicode normalization (NFKC) to prevent lookalike character attacks
    2. Block (not just log) suspicious patterns in production
    3. Consider Azure Content Safety API for advanced detection
    4. Add entropy checking for encoded payloads
  - **Implementation**:
    ```python
    import unicodedata

    def sanitize_user_input(message: str) -> tuple[str, bool]:
        """Sanitize and validate user input.

        Returns: (sanitized_message, is_safe)
        """
        # Unicode normalization (prevent homograph attacks)
        normalized = unicodedata.normalize('NFKC', message)

        # Check for suspicious patterns
        suspicious_patterns = [
            r'(?i)(ignore|forget|disregard).*instructions',
            r'(?i)system.*prompt',
            r'(?i)developer.*mode',
            # ... more patterns
        ]

        is_suspicious = any(re.search(p, normalized) for p in suspicious_patterns)

        if is_suspicious and not DEBUG:
            # Block in production
            raise ValueError("Input contains suspicious patterns")
        elif is_suspicious:
            # Log for debugging
            logger.warning(f"Suspicious input detected: {message}")

        return normalized, not is_suspicious
    ```
  - **Rationale**: Defense-in-depth against prompt injection, homograph attacks, encoded payloads

- [ ] Implement Azure AD Authentication (New files: shared/auth.py, updates to all route files)
  - **Priority**: Medium
  - **Effort**: Large (4-6 hours)
  - **Context**: Currently no authentication; anyone with API access can use service. Required for production multi-tenant security.
  - **Implementation**:
    1. Create shared/auth.py with JWT token validation
    2. Add @require_auth dependency to protected endpoints
    3. Use PyJWT + Azure AD JWKS for token verification
    4. Frontend: Already configured in Phase 5 MSAL setup
  - **Configuration**:
    ```python
    # shared/auth.py
    from fastapi import Depends, HTTPException, Security
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
    import jwt
    from jwt import PyJWKClient
    from shared.config import AZURE_AD_TENANT_ID, AZURE_AD_CLIENT_ID

    security = HTTPBearer()
    jwks_url = f"https://login.microsoftonline.com/{AZURE_AD_TENANT_ID}/discovery/v2.0/keys"
    jwks_client = PyJWKClient(jwks_url)

    async def verify_azure_token(credentials: HTTPAuthorizationCredentials = Security(security)):
        token = credentials.credentials
        try:
            signing_key = jwks_client.get_signing_key_from_jwt(token)
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                audience=AZURE_AD_CLIENT_ID,
                issuer=f"https://login.microsoftonline.com/{AZURE_AD_TENANT_ID}/v2.0"
            )
            return payload
        except Exception as e:
            raise HTTPException(status_code=401, detail="Invalid token")
    ```
  - **Environment Variables**: AZURE_AD_TENANT_ID, AZURE_AD_CLIENT_ID (from app registration)
  - **Rationale**: Only authenticated users can access the API; enables multi-tenant deployments

#### Low Priority - Optional Enhancements

- [ ] Add conversation history content sanitization (shared/chat_service.py:307-314)
  - **Priority**: Low
  - **Effort**: Quick (1 hour)
  - **Context**: Sanitize content in conversation history before sending to Azure OpenAI API.
  - **Note**: Pydantic model validation already prevents most issues (only 'user'/'assistant' roles allowed, non-empty content)
  - **Enhancement**: Additional sanitization layer for defense-in-depth
  - **Rationale**: Defense-in-depth against malformed history injection

- [ ] Add request ID to metrics endpoints (backend/src/api/routes/metrics.py)
  - **Priority**: Low (Enhancement)
  - **Effort**: Quick (1 hour)
  - **Context**: The /api/chat endpoint includes excellent request ID tracking for debugging (line 135: `request_id = str(uuid.uuid4())`), but the metrics endpoints don't have this. For a demo project this is perfectly acceptable, but adding request IDs to metrics endpoints would provide consistent logging across all endpoints.
  - **Why It's Optional**: This is a nice-to-have for production observability, but not required for demo purposes. The current implementation is appropriate for the project scope.
  - **Implementation Notes**:
    - Add uuid.uuid4() generation for each metrics request
    - Include request_id in logging statements
    - Return request_id in response headers (optional)

- [ ] Rate limit configuration documentation enhancement (.env.example)
  - **Priority**: Low (Enhancement)
  - **Effort**: Quick (15 minutes)
  - **Context**: The .env.example file has excellent documentation of rate limiting (lines 32-39), explaining the format and rationale. Consider adding a comment about what happens when rate limits are exceeded (429 status code, automatic retry headers).
  - **Example improvement**:
    ```bash
    # Rate limiting for chat endpoint
    # Format: number/timeunit (e.g., "10/minute", "100/hour", "1000/day")
    # Default: 10/minute - prevents DoS attacks and excessive API costs
    # When exceeded: Returns 429 Too Many Requests with Retry-After header
    RATE_LIMIT_CHAT=10/minute
    ```
  - **Why It's Optional**: Documentation enhancement only, no code changes. Helps future developers understand rate limiting behavior.

---

### Security Review Summary

**Review Date**: 2025-11-02
**Reviewer**: security-scanner agent
**PR Reviewed**: PR8 (conversation history validation + environment-based errors)
**Risk Level**: CRITICAL (due to API key exposure in .env, but mitigated by .gitignore)

**Key Findings**:
- 1 Critical: API keys in .env (mitigated by .gitignore, requires key rotation)
- 2 High: Missing input validation (days parameter), DEBUG mode info disclosure
- 5 Medium: Missing auth, basic prompt injection, no rate limiting on reads, secret management, enhanced prompt injection
- 2 Low: Content sanitization, request ID tracking

**Positive Security Practices** (9 identified):
- ✅ Comprehensive Pydantic input validation on chat endpoints
- ✅ Rate limiting on expensive operations (chat, setup)
- ✅ Environment-based secret management with .env files
- ✅ HTTPS endpoint validation
- ✅ Structured logging with request tracking and request IDs
- ✅ Restricted CORS configuration with environment-based origins
- ✅ Complete type safety throughout codebase
- ✅ Proper async/await patterns (no blocking I/O)
- ✅ Environment-based error handling (DEBUG mode for development)

**Overall Assessment**: Excellent security practices for demo project. Main gaps (authentication, advanced prompt injection, secret vault) are expected for demo phase and documented here for production hardening.

---

## 🎯 Phase 3: React Frontend Development (NOW IN PROGRESS)

### Structure Overview
Phase 3 focuses on building out the React frontend with 7 focused PRs. The frontend project structure is now in place at `frontend/` with:
- Vite + React + TypeScript (fully configured)
- Material-UI (MUI) components
- Recharts for data visualization
- Axios for API calls
- Basic project structure (components, pages, api, utils)

Each PR builds incrementally, allowing for testing at each stage before moving to the next.

---

### PR11: Core API Client & Data Models (Completed 2025-11-03)
**Status**: COMPLETED
**Priority**: HIGH
**Estimated Effort**: 3-4 hours (completed in ~3 hours)

#### Overview
Create TypeScript interfaces and Axios-based API client layer that matches backend Pydantic models. This foundation enables all other frontend PRs to communicate with the backend.

#### Completed Tasks

- [x] Create TypeScript interfaces matching backend models (frontend/src/types/api.ts)
  - **Status**: IMPLEMENTED
  - **Files Created**: frontend/src/types/api.ts
  - **Implementation Details**:
    - Complete TypeScript interfaces for all backend Pydantic models
    - OEEMetrics, ScrapMetrics, QualityIssue, QualityIssues types
    - DowntimeAnalysis, MajorDowntimeEvent types
    - ChatMessage, ChatRequest, ChatResponse types
    - SetupRequest, SetupResponse, StatsResponse types
    - MachineInfo, DateRangeResponse types
    - HealthResponse, ApiError types
    - MetricsQueryParams interface for filtering
    - isApiError() type guard utility

- [x] Build Axios-based API client with error handling (frontend/src/services/api.ts)
  - **Status**: IMPLEMENTED
  - **Files Updated**: frontend/src/services/api.ts
  - **Implementation Details**:
    - Axios instance with 30-second timeout and base URL configuration
    - Request interceptor with development logging
    - Response interceptor with error formatting
    - FormattedApiError interface for consistent error handling
    - formatApiError() utility for Axios error conversion
    - getErrorMessage() utility for user-friendly error messages
    - All API methods: checkHealth, generateData, getStats, getMachines, getDateRange
    - Metrics methods: getOEE, getScrap, getQuality, getDowntime
    - Chat method: sendChatMessage
    - All methods fully typed with TypeScript
    - Proper handling of network, timeout, server, and client errors

- [x] Add loading states and error handling utilities (frontend/src/utils/async.ts)
  - **Status**: IMPLEMENTED
  - **Files Created**: frontend/src/utils/async.ts
  - **Implementation Details**:
    - useAsyncData<T> hook for auto-fetching data with loading/error states
    - useAsyncCallback<T> hook for user-triggered async actions
    - Error checking utilities: isNetworkError, isTimeoutError, isServerError, isClientError
    - Authentication and rate limit error checkers: isAuthError, isRateLimitError
    - withRetry() utility with exponential backoff
    - createSkeletonArray() for loading placeholders
    - debounce() utility for input throttling

- [x] Test API connectivity with health check endpoint
  - **Status**: IMPLEMENTED
  - **Files Created**: frontend/src/components/ApiHealthCheck.tsx
  - **Implementation Details**:
    - Interactive health check component with Material-UI
    - Real-time API connectivity testing
    - Loading, error, and success states
    - Manual refresh functionality
    - API endpoint documentation display
    - Integration into App.tsx for immediate testing
    - Demonstrates useAsyncData hook usage
    - Build verification: npm run build succeeds with no TypeScript errors

#### Deliverables
- ✅ Complete TypeScript API types (matches backend)
- ✅ Axios client with full error handling
- ✅ Reusable async utilities and hooks
- ✅ API connectivity verified with interactive component

#### Files Created/Modified
**Created**:
- `frontend/src/types/api.ts` - Complete API type definitions (200+ lines)
- `frontend/src/utils/async.ts` - React hooks and async utilities (350+ lines)
- `frontend/src/components/ApiHealthCheck.tsx` - Health check component (120+ lines)
- `PR11_IMPLEMENTATION.md` - Comprehensive implementation documentation

**Modified**:
- `frontend/src/services/api.ts` - Enhanced with interceptors and error handling (350+ lines)
- `frontend/src/App.tsx` - Added ApiHealthCheck component integration
- `frontend/package.json` - Added @mui/icons-material dependency

#### Dependencies Added
- `@mui/icons-material@^7.1.12` - Material-UI icons for UI components

#### Build Verification
- TypeScript compilation: ✅ No errors
- Production build: ✅ Success (373.56 KB, gzipped: 120.39 KB)
- All new types properly integrated
- No linting errors

#### Testing
- Manual testing: ✅ ApiHealthCheck component works correctly
- Loading states: ✅ Display correctly
- Error states: ✅ Network errors handled properly
- Success states: ✅ Health check succeeds with backend running

#### Documentation
- Comprehensive PR11_IMPLEMENTATION.md created
- All functions have JSDoc comments
- Usage examples provided for hooks and utilities
- Backend API reference created by Explore agent

#### Code Review & Improvements (2025-11-03)
**Review Agent**: pr-reviewer
**Overall Assessment**: Ready for merge (95% CLAUDE.md compliance)

**Critical Fixes Applied**:
- ✅ Fixed `MachineInfo.id` type mismatch: `string` → `number` (frontend/src/types/api.ts:156)
- ✅ Fixed `SetupResponse.machines` type mismatch: `string[]` → `number` (frontend/src/types/api.ts:135)

**Important Improvements Applied**:
- ✅ Added `isBusinessError()` helper for metrics endpoints that return `{ error: string }` with 200 OK
- ✅ Updated all metrics endpoints (getOEE, getScrap, getQuality, getDowntime) to check for business errors
- ✅ Removed unused state variables from App.tsx (selectedMachine, dateRange)
- ✅ Fixed useAsyncData dependency array issue with useRef pattern to prevent unnecessary re-renders
- ✅ Added comprehensive JSDoc documentation to AsyncState and UseAsyncDataOptions interfaces

**Review Highlights**:
- Excellent TypeScript type coverage across all API responses
- Comprehensive error handling with user-friendly messages
- Beginner-friendly patterns with extensive inline comments
- Appropriate simplicity for demo project (no over-engineering)
- Strong foundation for future PRs to build upon

**Files Modified During Review**:
- `frontend/src/types/api.ts` - Type fixes for backend alignment
- `frontend/src/services/api.ts` - Business error handling added
- `frontend/src/App.tsx` - Removed placeholder code
- `frontend/src/utils/async.ts` - Fixed dependency array issue, added JSDoc

---

### 🚧 PR12: Dashboard Layout & Navigation - COMPLETED (2025-11-03)
**Status**: Completed
**Priority**: HIGH
**Estimated Effort**: 3-4 hours (completed)

*Moved to Completed PRs section above*

---

### ✅ PR13: Metrics Dashboard & Charts - COMPLETED (2025-11-06)
**Status**: COMPLETED
**Priority**: HIGH
**Estimated Effort**: 4-5 hours (completed)

#### Overview
Build the metrics overview page with cards for key statistics and implement Recharts visualizations. This is the core dashboard view users see first.

#### Completed Tasks

- [x] Build metrics overview page with statistic cards (frontend/src/pages/Dashboard.tsx)
  - **Status**: COMPLETED
  - **Details**: Dashboard page with statistics cards and filtering implemented

- [x] Implement Recharts visualizations for production trends (frontend/src/components/charts/)
  - **Status**: COMPLETED
  - **Details**: OEE trend, production rate, and efficiency breakdown charts completed

- [x] Create reusable chart components (frontend/src/components/charts/ChartContainer.tsx)
  - **Status**: COMPLETED
  - **Details**: Chart wrapper components with loading, error, and empty states

- [x] Add real-time data fetching from backend API (frontend/src/hooks/useMetrics.ts)
  - **Status**: COMPLETED
  - **Details**: Custom metrics hook with loading/error state and data caching

#### Deliverables
- ✅ Metrics dashboard page with statistics cards
- ✅ 3 interactive Recharts charts
- ✅ Reusable chart wrapper components
- ✅ Real-time data fetching with caching

#### Completion Notes
All metrics dashboard features are working properly. The core dashboard view displays OEE metrics, production trends, and key statistics with interactive charts and filtering capabilities.

---

### 🚧 PR14: Machine Status & Alerts View
**Status**: IN PROGRESS
**Priority**: MEDIUM
**Estimated Effort**: 3-4 hours

#### Overview
Create machine list view with status indicators and alerts notification system. Provides operational visibility into individual machines.

#### Tasks

- [ ] Relocate API service: Move `frontend/src/services/api.ts` to `frontend/src/api/client.ts` and update all imports
  - **Priority**: HIGH
  - **Effort**: Quick (<5 minutes)
  - **Context**: Directory structure cleanup from PR13 - API client should be in `frontend/src/api/` per CLAUDE.md architecture guidelines
  - **Details**:
    - Move frontend/src/services/api.ts to frontend/src/api/client.ts
    - Update all imports from "frontend/src/services/api" to "frontend/src/api/client"
    - Files to update: App.tsx, ApiHealthCheck.tsx, and any other components importing from services/api
    - Verify build succeeds after relocation

- [ ] Create machine list view with status indicators (frontend/src/pages/Machines.tsx)
  - **Priority**: MEDIUM
  - **Effort**: Medium (1.5 hours)
  - **Context**: Machine inventory page
  - **Details**:
    - MUI DataGrid for machine list
    - Columns: Name, Status, OEE, Last Updated, Actions
    - Status indicator: Green (Running), Yellow (Warning), Red (Down)
    - Sort and filter capabilities
    - Click machine to view details

- [ ] Build alert notification system (frontend/src/components/alerts/AlertNotification.tsx)
  - **Priority**: MEDIUM
  - **Effort**: Medium (1.5 hours)
  - **Context**: Alert display and management
  - **Details**:
    - Alert card component with severity colors
    - Alert list showing recent alerts (last 10)
    - Filter by machine and severity
    - Mark alert as resolved
    - Toast notifications for new alerts
    - Alert history page

- [ ] Add filtering and sorting capabilities (frontend/src/hooks/useMachineFilter.ts)
  - **Priority**: MEDIUM
  - **Effort**: Quick (45 minutes)
  - **Context**: Machine list filtering
  - **Details**:
    - Filter by status (Running, Warning, Down)
    - Sort by Name, OEE, Last Updated
    - Search by machine name
    - Persist filters in URL params

- [ ] Implement machine detail view (frontend/src/pages/MachineDetail.tsx)
  - **Priority**: MEDIUM
  - **Effort**: Medium (1 hour)
  - **Context**: Detailed machine view
  - **Details**:
    - Machine stats: Current OEE, Status, Efficiency, Performance, Quality
    - Last 30 days trend chart
    - Recent alerts for this machine
    - Back button to machine list

#### Deliverables
- ✅ Machine list view with status indicators
- ✅ Alert notification system with filtering
- ✅ Filtering and sorting on machine list
- ✅ Machine detail page with statistics

---

### 📋 PR15: AI Chat Interface
**Status**: Planned
**Priority**: MEDIUM
**Estimated Effort**: 3-4 hours

#### Overview
Create chat UI component with message history and integrate with backend chat API. Provides AI assistant interaction for factory insights.

#### Tasks

- [ ] Create chat UI component with message history (frontend/src/components/chat/ChatConsole.tsx)
  - **Priority**: MEDIUM
  - **Effort**: Medium (1.5 hours)
  - **Context**: Main chat interface
  - **Details**:
    - Message list with auto-scroll to bottom
    - Message styling: different colors for user/assistant
    - Timestamp on each message
    - Loading indicator while waiting for response
    - Chat history persisted in component state

- [ ] Integrate with backend /api/chat endpoint (frontend/src/hooks/useChat.ts)
  - **Priority**: MEDIUM
  - **Effort**: Medium (1 hour)
  - **Context**: Chat API integration
  - **Details**:
    - useChat hook managing conversation state
    - Send message function with error handling
    - Conversation history management (max 50 messages)
    - Optimistic updates (show user message immediately)
    - Error recovery with retry

- [ ] Add typing indicators and loading states (frontend/src/components/chat/TypingIndicator.tsx)
  - **Priority**: MEDIUM
  - **Effort**: Quick (45 minutes)
  - **Context**: UX feedback
  - **Details**:
    - Animated typing indicator when AI is responding
    - Loading spinner on send button
    - Disable input while waiting for response
    - Estimated time remaining (optional)

- [ ] Implement suggested questions/prompts (frontend/src/components/chat/SuggestedPrompts.tsx)
  - **Priority**: MEDIUM
  - **Effort**: Quick (45 minutes)
  - **Context**: Help users get started
  - **Details**:
    - Show suggested questions initially (when chat is empty)
    - Examples: "What's the OEE for Machine A?", "Show me today's downtime"
    - Click to fill input box
    - Hide after first message

#### Deliverables
- ✅ Chat console with message history
- ✅ Integration with backend API
- ✅ Typing indicators and loading states
- ✅ Suggested prompts for easy interaction

---

### 📋 PR16: Authentication & Azure AD Integration
**Status**: Planned
**Priority**: LOW (Optional for demo, HIGH for production)
**Estimated Effort**: 2-3 hours

#### Overview
Add Azure AD authentication with Microsoft accounts. Enables secure multi-user access and aligns with enterprise Azure ecosystem.

#### Tasks

- [ ] Add @azure/msal-react for Azure AD authentication (frontend/src/authConfig.ts)
  - **Priority**: LOW
  - **Effort**: Quick (45 minutes)
  - **Context**: MSAL setup and configuration
  - **Details**:
    - Configure MSAL with Azure AD app registration
    - Set client ID, tenant ID, redirect URI
    - Add login request scopes
    - Create msalInstance and wrap App with MsalProvider

- [ ] Implement login/logout flow (frontend/src/components/auth/AuthButtons.tsx)
  - **Priority**: LOW
  - **Effort**: Medium (1 hour)
  - **Context**: User authentication UI
  - **Details**:
    - Login button with MSAL popup
    - Logout button
    - User profile display (optional)
    - Handle auth errors gracefully
    - Loading state during auth flow

- [ ] Add protected routes (frontend/src/components/auth/ProtectedRoute.tsx)
  - **Priority**: LOW
  - **Effort**: Quick (45 minutes)
  - **Context**: Route-level auth protection
  - **Details**:
    - ProtectedRoute component checking authentication
    - Redirect to login if not authenticated
    - Show loading while checking auth status
    - Pass auth token to API client

- [ ] Configure redirect URIs and tenant settings (documentation)
  - **Priority**: LOW
  - **Effort**: Quick (30 minutes)
  - **Context**: Azure AD app registration
  - **Details**:
    - Document Azure AD app registration steps
    - List required redirect URIs
    - Explain tenant configuration
    - Provide example .env.example entries

#### Deliverables
- ✅ MSAL configuration for Azure AD
- ✅ Login/logout UI components
- ✅ Protected routes
- ✅ Azure AD setup documentation

---

### 📋 PR17: Deployment & CI/CD
**Status**: Planned
**Priority**: MEDIUM
**Estimated Effort**: 3-4 hours

#### Overview
Create Docker containers for React frontend and update deployment pipeline. Enables Azure Container Apps deployment with automated CI/CD.

#### Tasks

- [ ] Create Dockerfile for React frontend (frontend/Dockerfile)
  - **Priority**: MEDIUM
  - **Effort**: Quick (30 minutes)
  - **Context**: Container image for frontend
  - **Details**:
    - Multi-stage build: Node build stage + Nginx serve stage
    - Build stage: Install dependencies, build with Vite
    - Production stage: Alpine nginx, copy built assets
    - Health check (optional)
    - Non-root user for security

- [ ] Create nginx configuration (frontend/nginx.conf)
  - **Priority**: MEDIUM
  - **Effort**: Quick (30 minutes)
  - **Context**: Web server configuration
  - **Details**:
    - Serve static files from /dist
    - SPA routing: Fallback to index.html
    - Proxy /api requests to backend
    - Proxy /ws for WebSocket (future)
    - GZIP compression
    - Cache headers for assets

- [ ] Update GitHub Actions workflow for frontend build/deploy (frontend steps added to .github/workflows/azure-deploy.yml)
  - **Priority**: MEDIUM
  - **Effort**: Medium (1 hour)
  - **Context**: CI/CD pipeline
  - **Details**:
    - Add frontend Docker build step
    - Add frontend Docker push step
    - Add frontend Container Apps update step
    - Test step: npm run build succeeds
    - Use secrets for Azure credentials

- [ ] Configure Azure Container Apps for frontend container (documentation)
  - **Priority**: MEDIUM
  - **Effort**: Quick (45 minutes)
  - **Context**: Deployment setup
  - **Details**:
    - Container Apps environment (shared with backend)
    - Frontend Container App with 80 port exposure
    - Environment variables: VITE_API_URL pointing to backend
    - Min/max replicas configuration
    - Ingress configuration for HTTPS
    - Document manual setup steps for Azure Portal

- [ ] Add environment variable configuration (frontend/.env.example)
  - **Priority**: MEDIUM
  - **Effort**: Quick (15 minutes)
  - **Context**: Build-time configuration
  - **Details**:
    - VITE_API_URL: Backend API URL
    - VITE_AZURE_AD_CLIENT_ID: Azure AD client ID
    - VITE_AZURE_AD_TENANT_ID: Azure AD tenant ID
    - VITE_REDIRECT_URI: Auth redirect URI
    - Document each variable

#### Deliverables
- ✅ Frontend Dockerfile with multi-stage build
- ✅ Nginx configuration for SPA + API proxying
- ✅ Updated GitHub Actions workflow
- ✅ Azure Container Apps deployment documentation

---

## 🎯 Upcoming Work Items

### Phase 4: Voice Integration (Post-Phase 3)
**Target**: Week 3-4 implementation
**Key Tasks**:
- Add transcribe endpoint (Azure OpenAI Whisper)
- Add synthesize endpoint (Azure OpenAI TTS)
- Build voice UI components

### Phase 5: Containerization & Azure Deployment (Post-Phase 4)
**Target**: Week 4-5 implementation
**Key Tasks**:
- Create Docker containers
- Set up Azure Container Registry
- Deploy to Azure Container Apps
- Configure Azure AD authentication
- Set up GitHub Actions CI/CD

---

## 🎯 Migration Goals

Transform the factory operations chatbot from a local Streamlit/CLI application to a cloud-native web application deployed on Azure with:

- **React split-pane interface**: Dashboard (left) + Chat Console (right)
- **FastAPI backend**: RESTful API with WebSocket support
- **Azure Container Apps**: Serverless container hosting
- **Azure AD authentication**: Microsoft account login
- **Voice interface**: Browser-based recording with OpenAI Whisper/TTS
- **Full Azure deployment**: Container Apps, Blob Storage, Container Registry

---

## 🏗️ Architecture Overview

### Current Architecture
```
┌─────────────────────────────────────────────┐
│  Streamlit Dashboard (Port 8501)            │
│  - OEE gauges, charts, tables               │
│  - Sidebar filters                          │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│  Typer CLI (Terminal)                       │
│  - python -m src.main chat                  │
│  - python -m src.main voice                 │
│  - Rich console output                      │
└─────────────────────────────────────────────┘

        ↓ Both use same metrics layer

┌─────────────────────────────────────────────┐
│  Python Backend (Local)                     │
│  - metrics.py: 4 analysis functions         │
│  - data.py: JSON file storage               │
│  - Azure OpenAI client                      │
└─────────────────────────────────────────────┘
```

### Target Architecture
```
┌──────────────────────────────────────────────────────────┐
│  React Frontend (Azure Container Apps)                   │
│                                                           │
│  ┌─────────────────────┐  ┌──────────────────────────┐  │
│  │  Dashboard Panel    │  │  Console Panel           │  │
│  │  (Left Pane)        │  │  (Right Pane)            │  │
│  │                     │  │                          │  │
│  │  - OEE Gauge        │  │  - Chat History          │  │
│  │  - Trend Charts     │  │  - Message Input         │  │
│  │  - Downtime Table   │  │  - Voice Recorder        │  │
│  │  - Quality Table    │  │  - Audio Playback        │  │
│  │  - Machine Filter   │  │  - Typing Indicator      │  │
│  │                     │  │                          │  │
│  └─────────────────────┘  └──────────────────────────┘  │
│                                                           │
│  Uses: Material-UI, Recharts, react-split-pane          │
└──────────────────────────────────────────────────────────┘
                            ↓
                    HTTPS + Azure AD Auth
                            ↓
┌──────────────────────────────────────────────────────────┐
│  FastAPI Backend (Azure Container Apps)                  │
│                                                           │
│  REST Endpoints:                                         │
│  - GET  /api/metrics/oee                                 │
│  - GET  /api/metrics/scrap                               │
│  - GET  /api/metrics/quality                             │
│  - GET  /api/metrics/downtime                            │
│  - GET  /api/machines                                    │
│  - GET  /api/stats                                       │
│  - POST /api/setup                                       │
│                                                           │
│  Chat & Voice:                                           │
│  - POST /api/chat                                        │
│  - WS   /ws/chat (WebSocket for streaming)              │
│  - POST /api/voice/transcribe                            │
│  - POST /api/voice/synthesize                            │
│                                                           │
│  Reused Code:                                            │
│  - metrics.py (unchanged)                                │
│  - models.py (unchanged)                                 │
│  - data.py (updated for Blob Storage)                    │
│  - config.py (updated for Azure)                         │
└──────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────┐
│  Azure Services                                          │
│                                                           │
│  - Azure Blob Storage: production.json data              │
│  - Azure Container Registry: Docker images               │
│  - Azure AD (Entra ID): Authentication                   │
│  - Azure OpenAI: GPT-4 chat, Whisper (speech-to-text),  │
│                  TTS (text-to-speech)                    │
│  - Application Insights: Monitoring (optional)           │
└──────────────────────────────────────────────────────────┘
```

---

## 📋 Implementation Phases

### Phase 1: Backend API with FastAPI (Week 1-2)

**Goal:** Create REST API that reuses existing Python business logic

#### Tasks

**1.1 Project Structure Setup**
- Create `backend/` directory
- Set up Python package structure with `src/api/`
- Copy existing modules: `metrics.py`, `models.py`, `data.py`, `config.py`
- Create `requirements.txt` with FastAPI dependencies

**1.2 FastAPI Application Core**
- Create `backend/src/api/main.py` with FastAPI app
- Configure CORS for local React development
- Add health check endpoint: `GET /health`
- Set up environment variable loading

**1.3 Metrics Endpoints**
- Create `backend/src/api/routes/metrics.py`
- Implement endpoints:
  ```python
  GET /api/metrics/oee?start_date=X&end_date=Y&machine=Z
  GET /api/metrics/scrap?start_date=X&end_date=Y&machine=Z
  GET /api/metrics/quality?start_date=X&end_date=Y&severity=X&machine=Z
  GET /api/metrics/downtime?start_date=X&end_date=Y&machine=Z
  ```
- Use existing `metrics.py` functions directly (no changes needed)
- Return Pydantic models as JSON (automatic serialization)

**1.4 Data Management Endpoints**
- Create `backend/src/api/routes/data.py`
- Implement:
  ```python
  POST /api/setup          # Generate synthetic data
  GET  /api/stats          # Get data statistics
  GET  /api/machines       # List available machines
  GET  /api/date-range     # Get available data dates
  ```

**1.5 Chat Service Layer (Shared Logic)**
- Create `backend/src/services/chat_service.py`
- Extract from `src/main.py`:
  ```python
  # Move these functions to chat_service.py:
  def get_chat_response(client, system_prompt, history, user_message):
      """Renamed from _get_chat_response, identical logic"""
      # ... existing tool-calling loop ...

  def execute_tool(tool_name, tool_args):
      """Moved as-is from main.py"""
      # ... existing tool execution ...

  TOOLS = [...]  # Moved as-is from main.py
  ```
- This preserves all existing logic while making it reusable

**1.6 Chat Endpoint**
- Create `backend/src/api/routes/chat.py`
- Implement `POST /api/chat` endpoint using `chat_service`:
  ```python
  from services.chat_service import get_chat_response

  @router.post("/api/chat")
  async def chat(request: ChatRequest):
      response, updated_history = get_chat_response(
          client, system_prompt, request.history, request.message
      )
      return {"response": response, "history": updated_history}
  ```

**1.7 Test Migration**
- Rename `tests/test_main.py` → `tests/test_chat_service.py`
- Update imports:
  ```python
  # OLD: from src.main import _get_chat_response, execute_tool
  # NEW: from src.services.chat_service import get_chat_response, execute_tool
  ```
- All test logic stays identical (just import changes)
- Add new `tests/test_api.py` for endpoint testing

**1.8 Local Testing**
- Run with: `uvicorn src.api.main:app --reload`
- Test all endpoints with Postman or curl
- Verify metrics calculations match existing CLI/Streamlit output
- Run pytest: All migrated tests should pass

**Deliverables:**
- ✅ Working FastAPI application running locally
- ✅ All metrics endpoints functional
- ✅ Basic chat endpoint working
- ✅ Pytest tests passing
- ✅ API documentation auto-generated at `/docs`

---

### Phase 2: Azure Blob Storage Integration (Week 2)

**Goal:** Migrate from local JSON file to Azure Blob Storage

#### Tasks

**2.1 Azure Storage Account Setup**
- Create Azure Storage Account in portal
- Create blob container: `factory-data`
- Get connection string from Azure Portal
- Add `AZURE_STORAGE_CONNECTION_STRING` to `.env`

**2.2 Update data.py for Blob Storage**
- Install: `azure-storage-blob`
- Modify `save_data()` to write to blob:
  ```python
  from azure.storage.blob import BlobServiceClient

  def save_data(data: Dict[str, Any]) -> None:
      blob_service_client = BlobServiceClient.from_connection_string(conn_str)
      blob_client = blob_service_client.get_blob_client(
          container="factory-data",
          blob="production.json"
      )
      blob_client.upload_blob(json.dumps(data), overwrite=True)
  ```
- Modify `load_data()` to read from blob
- Keep local file fallback for development

**2.3 Environment-based Storage**
- Add `STORAGE_MODE` config: `local` or `azure`
- Local dev: Use JSON file
- Azure deployment: Use Blob Storage
- Update `config.py` to handle both modes

**2.4 Testing**
- Test data generation to blob
- Test data loading from blob
- Verify metrics work with blob-based data
- Test fallback to local file in dev mode

**Deliverables:**
- ✅ Data persists in Azure Blob Storage
- ✅ FastAPI reads from blob in Azure mode
- ✅ Local development still works with JSON file
- ✅ Tests updated for both storage modes

---

### Phase 3: React Frontend Development (Week 2-3)

**Goal:** Build beginner-friendly React interface with split-pane layout

#### Tasks

**3.1 React Project Setup**
- Create `frontend/` directory
- Initialize with Vite: `npm create vite@latest . -- --template react-ts`
- Install dependencies:
  ```bash
  npm install @mui/material @emotion/react @emotion/styled
  npm install recharts axios react-split-pane
  npm install @types/react-split-pane --save-dev
  ```

**3.2 Core Layout Components**

**3.2.1 App.tsx (Main Layout)**
```typescript
import React from 'react';
import SplitPane from 'react-split-pane';
import DashboardPanel from './components/DashboardPanel';
import ConsolePanel from './components/ConsolePanel';

function App() {
  // Shared state: selected machine filter
  const [selectedMachine, setSelectedMachine] = useState<string | null>(null);

  return (
    <SplitPane split="vertical" defaultSize="60%">
      <DashboardPanel
        selectedMachine={selectedMachine}
        onMachineChange={setSelectedMachine}
      />
      <ConsolePanel selectedMachine={selectedMachine} />
    </SplitPane>
  );
}
```

**3.2.2 DashboardPanel.tsx (Left Pane Container)**
- Tab navigation: OEE, Availability, Quality
- Machine filter dropdown at top
- Renders child components based on active tab

**3.2.3 ConsolePanel.tsx (Right Pane Container)**
- Chat history display area
- Message input box at bottom
- Voice recorder button
- "Thinking..." indicator

**3.3 Dashboard Components (Left Pane)**

**3.3.1 OEEGauge.tsx**
- Beginner pattern with detailed comments:
```typescript
import React, { useState, useEffect } from 'react';
import { PieChart, Pie, Cell } from 'recharts';
import axios from 'axios';

interface OEEGaugeProps {
  machineId?: string;
  startDate: string;
  endDate: string;
}

export const OEEGauge: React.FC<OEEGaugeProps> = ({
  machineId,
  startDate,
  endDate
}) => {
  // State for OEE data
  const [oee, setOee] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(true);

  // Fetch OEE data when component mounts or params change
  useEffect(() => {
    const fetchOEE = async () => {
      setLoading(true);
      try {
        const params = { start_date: startDate, end_date: endDate };
        if (machineId) params.machine_name = machineId;

        const response = await axios.get('/api/metrics/oee', { params });
        setOee(response.data.oee * 100); // Convert to percentage
      } catch (error) {
        console.error('Failed to fetch OEE:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchOEE();
  }, [machineId, startDate, endDate]); // Re-fetch when these change

  // Gauge chart data (0-100 scale)
  const data = [
    { name: 'OEE', value: oee },
    { name: 'Gap', value: 100 - oee }
  ];

  // Color based on OEE value (red/yellow/green)
  const getColor = (value: number) => {
    if (value >= 75) return '#4caf50'; // Green
    if (value >= 60) return '#ffeb3b'; // Yellow
    return '#f44336'; // Red
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      <h3>Current OEE: {oee.toFixed(1)}%</h3>
      <PieChart width={200} height={200}>
        <Pie
          data={data}
          cx={100}
          cy={100}
          startAngle={180}
          endAngle={0}
          innerRadius={60}
          outerRadius={80}
          dataKey="value"
        >
          <Cell fill={getColor(oee)} />
          <Cell fill="#e0e0e0" />
        </Pie>
      </PieChart>
    </div>
  );
};
```

**3.3.2 TrendChart.tsx**
- Line chart showing daily OEE or scrap rate trends
- Uses Recharts LineChart component
- Fetches daily data for date range
- Similar useState/useEffect pattern

**3.3.3 DowntimeTable.tsx**
- Material-UI Table component
- Displays downtime events with sorting
- Color-coded by duration (>2 hours highlighted)

**3.3.4 QualityTable.tsx**
- Material-UI Table component
- Quality issues with severity badges
- Color coding: Red (High), Yellow (Medium), Green (Low)

**3.4 Console Components (Right Pane)**

**3.4.1 ChatConsole.tsx**
- Container with message list and input
- Manages conversation history state
- Handles send message action

**3.4.2 MessageList.tsx**
```typescript
interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface MessageListProps {
  messages: Message[];
}

export const MessageList: React.FC<MessageListProps> = ({ messages }) => {
  // Auto-scroll to bottom when new message arrives
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div style={{ height: '100%', overflowY: 'auto', padding: '1rem' }}>
      {messages.map((msg, idx) => (
        <MessageItem key={idx} message={msg} />
      ))}
      <div ref={messagesEndRef} />
    </div>
  );
};
```

**3.4.3 ChatInput.tsx**
- Text input with send button
- Enter key to send
- Disabled while waiting for response

**3.4.4 VoiceRecorder.tsx**
- Button to start/stop recording
- Uses browser MediaRecorder API
- Visual feedback during recording
- (Implemented in Phase 4)

**3.5 Services Layer**

**3.5.1 api.ts**
```typescript
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Metrics API
export const getOEE = (params: {
  start_date: string;
  end_date: string;
  machine_name?: string;
}) => api.get('/api/metrics/oee', { params });

export const getScrap = (params: {
  start_date: string;
  end_date: string;
  machine_name?: string;
}) => api.get('/api/metrics/scrap', { params });

// Chat API
export const sendChatMessage = (message: string, history: any[]) =>
  api.post('/api/chat', { message, history });

// ... other endpoints
```

**3.6 Local Development Testing**
- Run backend: `cd backend && uvicorn src.api.main:app --reload`
- Run frontend: `cd frontend && npm run dev`
- Test split-pane resize
- Test all dashboard tabs load data
- Test machine filter updates charts
- Test chat sends messages

**Deliverables:**
- ✅ React app running locally on port 3000
- ✅ Split-pane layout with dashboard + console
- ✅ Dashboard displays OEE gauges, charts, tables
- ✅ Console has message list and input
- ✅ All components fetch data from FastAPI backend
- ✅ Machine filter works across dashboard and chat

---

### Phase 4: Voice Feature Integration (Week 3-4)

**Goal:** Add browser-based voice recording with Azure OpenAI Whisper/TTS

**Note:** Azure OpenAI now supports both Whisper (speech-to-text) and TTS (text-to-speech) models. This keeps everything in the Azure ecosystem without needing separate OpenAI API keys.

#### Tasks

**4.1 Backend Voice Endpoints**

**4.1.1 POST /api/voice/transcribe**
```python
from fastapi import UploadFile, File
from openai import AzureOpenAI
import os
import tempfile

@router.post("/voice/transcribe")
async def transcribe_audio(audio: UploadFile = File(...)):
    """Transcribe audio using Azure OpenAI Whisper."""
    # Use same Azure OpenAI client as chat
    client = AzureOpenAI(
        azure_endpoint=os.getenv("AZURE_ENDPOINT"),
        api_key=os.getenv("AZURE_API_KEY"),
        api_version="2024-08-01-preview"
    )

    # Read audio file
    audio_bytes = await audio.read()

    # Create temporary file (Whisper needs file path)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp:
        temp.write(audio_bytes)
        temp_path = temp.name

    try:
        # Transcribe with Azure OpenAI Whisper
        with open(temp_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model=os.getenv("AZURE_WHISPER_DEPLOYMENT_NAME", "whisper"),
                file=audio_file
            )
        return {"text": transcript.text}
    finally:
        os.unlink(temp_path)
```

**4.1.2 POST /api/voice/synthesize**
```python
from pydantic import BaseModel

class TTSRequest(BaseModel):
    text: str
    voice: str = "alloy"  # alloy, echo, fable, onyx, nova, shimmer

@router.post("/voice/synthesize")
async def synthesize_speech(request: TTSRequest):
    """Generate speech from text using Azure OpenAI TTS."""
    client = AzureOpenAI(
        azure_endpoint=os.getenv("AZURE_ENDPOINT"),
        api_key=os.getenv("AZURE_API_KEY"),
        api_version="2024-08-01-preview"
    )

    response = client.audio.speech.create(
        model=os.getenv("AZURE_TTS_DEPLOYMENT_NAME", "tts"),
        voice=request.voice,
        input=request.text
    )

    # Return audio as streaming response
    return StreamingResponse(
        io.BytesIO(response.content),
        media_type="audio/mpeg"
    )
```

**4.2 Frontend Voice Components**

**4.2.1 VoiceRecorder.tsx**
```typescript
import React, { useState, useRef } from 'react';
import { Button, CircularProgress } from '@mui/material';
import MicIcon from '@mui/icons-material/Mic';
import StopIcon from '@mui/icons-material/Stop';

export const VoiceRecorder: React.FC<{onTranscript: (text: string) => void}> =
({ onTranscript }) => {
  const [recording, setRecording] = useState(false);
  const [processing, setProcessing] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  const startRecording = async () => {
    try {
      // Request microphone access
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

      // Create MediaRecorder
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      // Collect audio data
      mediaRecorder.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      // Handle recording stop
      mediaRecorder.onstop = async () => {
        // Create audio blob
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });

        // Stop all tracks (release microphone)
        stream.getTracks().forEach(track => track.stop());

        // Send to backend for transcription
        await transcribeAudio(audioBlob);
      };

      // Start recording
      mediaRecorder.start();
      setRecording(true);
    } catch (error) {
      console.error('Microphone access failed:', error);
      alert('Please allow microphone access');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && recording) {
      mediaRecorderRef.current.stop();
      setRecording(false);
      setProcessing(true);
    }
  };

  const transcribeAudio = async (audioBlob: Blob) => {
    try {
      const formData = new FormData();
      formData.append('audio', audioBlob, 'recording.wav');

      const response = await axios.post('/api/voice/transcribe', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      onTranscript(response.data.text);
    } catch (error) {
      console.error('Transcription failed:', error);
    } finally {
      setProcessing(false);
    }
  };

  return (
    <Button
      variant="contained"
      color={recording ? "secondary" : "primary"}
      onClick={recording ? stopRecording : startRecording}
      disabled={processing}
      startIcon={recording ? <StopIcon /> : <MicIcon />}
    >
      {processing ? <CircularProgress size={24} /> :
       recording ? 'Stop Recording' : 'Record Voice'}
    </Button>
  );
};
```

**4.2.2 AudioPlayer.tsx**
```typescript
export const AudioPlayer: React.FC<{text: string}> = ({ text }) => {
  const [playing, setPlaying] = useState(false);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  const playAudio = async () => {
    setPlaying(true);
    try {
      // Request TTS from backend
      const response = await axios.post('/api/voice/synthesize',
        { text },
        { responseType: 'blob' }
      );

      // Create audio URL from blob
      const audioBlob = new Blob([response.data], { type: 'audio/mpeg' });
      const audioUrl = URL.createObjectURL(audioBlob);

      // Play audio
      const audio = new Audio(audioUrl);
      audioRef.current = audio;
      audio.onended = () => {
        setPlaying(false);
        URL.revokeObjectURL(audioUrl);
      };
      audio.play();
    } catch (error) {
      console.error('TTS playback failed:', error);
      setPlaying(false);
    }
  };

  return (
    <Button onClick={playAudio} disabled={playing}>
      🔊 Play Response
    </Button>
  );
};
```

**4.3 Azure OpenAI Model Deployments (Required)**

Before implementing voice features, deploy Whisper and TTS models in your Azure OpenAI resource:

1. **Deploy Whisper model:**
   - Go to Azure OpenAI Studio → Deployments
   - Create deployment: Model = `whisper`, Deployment name = `whisper` (or custom name)
   - Set `AZURE_WHISPER_DEPLOYMENT_NAME` environment variable

2. **Deploy TTS model:**
   - Create deployment: Model = `tts-1` or `tts-1-hd`, Deployment name = `tts` (or custom name)
   - Set `AZURE_TTS_DEPLOYMENT_NAME` environment variable

**Note:** These are Azure OpenAI deployments, not separate Azure Speech service. Everything uses your existing Azure OpenAI resource.

**4.4 Integration with Chat**
- Add VoiceRecorder to ChatConsole
- When transcription completes, populate chat input
- After AI response, optionally play TTS
- Show audio waveform during recording (optional enhancement)

**4.5 Testing**
- Test microphone permission request
- Test recording and transcription with Azure Whisper
- Test TTS generation and playback with Azure TTS
- Test error handling (denied permissions, API failures)
- Verify all voice calls use Azure OpenAI (no separate OpenAI API keys needed)

**Deliverables:**
- ✅ Voice recording works in browser
- ✅ Whisper transcription accurate
- ✅ TTS plays assistant responses
- ✅ Graceful error handling
- ✅ Visual feedback during recording/processing

---

### Phase 5: Containerization & Azure Deployment (Week 4-5)

**Goal:** Deploy to Azure Container Apps with full CI/CD pipeline

#### Tasks

**5.1 Docker Configuration**

**5.1.1 Backend Dockerfile**
```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/

# Expose port
EXPOSE 8000

# Run with uvicorn
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**5.1.2 Frontend Dockerfile**
```dockerfile
# frontend/Dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci

# Copy source and build
COPY . .
RUN npm run build

# Production image with nginx
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

**5.1.3 Frontend nginx.conf**
```nginx
server {
    listen 80;
    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
    }

    # Proxy API requests to backend
    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # WebSocket support
    location /ws {
        proxy_pass http://backend:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

**5.1.4 Docker Compose (Local Development)**
```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - AZURE_ENDPOINT=${AZURE_ENDPOINT}
      - AZURE_API_KEY=${AZURE_API_KEY}
      - AZURE_DEPLOYMENT_NAME=${AZURE_DEPLOYMENT_NAME}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - AZURE_STORAGE_CONNECTION_STRING=${AZURE_STORAGE_CONNECTION_STRING}
      - STORAGE_MODE=azure
    volumes:
      - ./backend/src:/app/src
      - ./data:/app/data

  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - backend
    environment:
      - VITE_API_URL=http://localhost:8000
```

**5.2 Azure Resources Setup**

**5.2.1 Create Azure Container Registry**
```bash
# Azure CLI commands
az group create --name factory-agent-rg --location eastus

az acr create \
  --resource-group factory-agent-rg \
  --name factoryagentacr \
  --sku Basic

# Enable admin access for Container Apps
az acr update --name factoryagentacr --admin-enabled true

# Get login credentials
az acr credential show --name factoryagentacr
```

**5.2.2 Push Images to ACR**
```bash
# Login to ACR
az acr login --name factoryagentacr

# Build and tag images
docker build -t factoryagentacr.azurecr.io/backend:latest ./backend
docker build -t factoryagentacr.azurecr.io/frontend:latest ./frontend

# Push to ACR
docker push factoryagentacr.azurecr.io/backend:latest
docker push factoryagentacr.azurecr.io/frontend:latest
```

**5.2.3 Create Container Apps Environment**
```bash
az containerapp env create \
  --name factory-agent-env \
  --resource-group factory-agent-rg \
  --location eastus
```

**5.2.4 Deploy Backend Container App**
```bash
az containerapp create \
  --name factory-backend \
  --resource-group factory-agent-rg \
  --environment factory-agent-env \
  --image factoryagentacr.azurecr.io/backend:latest \
  --registry-server factoryagentacr.azurecr.io \
  --registry-username <username> \
  --registry-password <password> \
  --target-port 8000 \
  --ingress external \
  --min-replicas 0 \
  --max-replicas 3 \
  --secrets \
    azure-openai-key=$AZURE_API_KEY \
    openai-key=$OPENAI_API_KEY \
    storage-conn=$AZURE_STORAGE_CONNECTION_STRING \
  --env-vars \
    AZURE_ENDPOINT=$AZURE_ENDPOINT \
    AZURE_DEPLOYMENT_NAME=$AZURE_DEPLOYMENT_NAME \
    AZURE_API_KEY=secretref:azure-openai-key \
    OPENAI_API_KEY=secretref:openai-key \
    AZURE_STORAGE_CONNECTION_STRING=secretref:storage-conn \
    STORAGE_MODE=azure
```

**5.2.5 Deploy Frontend Container App**
```bash
az containerapp create \
  --name factory-frontend \
  --resource-group factory-agent-rg \
  --environment factory-agent-env \
  --image factoryagentacr.azurecr.io/frontend:latest \
  --registry-server factoryagentacr.azurecr.io \
  --registry-username <username> \
  --registry-password <password> \
  --target-port 80 \
  --ingress external \
  --min-replicas 1 \
  --max-replicas 2 \
  --env-vars \
    VITE_API_URL=https://<backend-url>
```

**5.3 Azure AD Authentication Setup**

**5.3.1 Register App in Azure AD**
1. Go to Azure Portal → Azure Active Directory
2. App registrations → New registration
3. Name: "Factory Agent Web App"
4. Redirect URI: `https://<frontend-url>/auth/callback`
5. Note: Application (client) ID and Directory (tenant) ID

**5.3.2 Configure MSAL in Frontend**
```typescript
// frontend/src/authConfig.ts
import { Configuration } from '@azure/msal-browser';

export const msalConfig: Configuration = {
  auth: {
    clientId: import.meta.env.VITE_AZURE_AD_CLIENT_ID,
    authority: `https://login.microsoftonline.com/${import.meta.env.VITE_AZURE_AD_TENANT_ID}`,
    redirectUri: import.meta.env.VITE_REDIRECT_URI,
  },
  cache: {
    cacheLocation: 'localStorage',
    storeAuthStateInCookie: false,
  },
};

export const loginRequest = {
  scopes: ['User.Read'],
};
```

**5.3.3 Wrap App with MSAL Provider**
```typescript
// frontend/src/main.tsx
import { MsalProvider } from '@azure/msal-react';
import { PublicClientApplication } from '@azure/msal-browser';
import { msalConfig } from './authConfig';

const msalInstance = new PublicClientApplication(msalConfig);

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <MsalProvider instance={msalInstance}>
      <App />
    </MsalProvider>
  </React.StrictMode>
);
```

**5.3.4 Add Authentication to Components**
```typescript
// frontend/src/App.tsx
import { useIsAuthenticated, useMsal } from '@azure/msal-react';
import { loginRequest } from './authConfig';

function App() {
  const isAuthenticated = useIsAuthenticated();
  const { instance } = useMsal();

  const handleLogin = () => {
    instance.loginPopup(loginRequest);
  };

  const handleLogout = () => {
    instance.logoutPopup();
  };

  if (!isAuthenticated) {
    return (
      <div>
        <h1>Factory Agent - Please Sign In</h1>
        <Button onClick={handleLogin}>Sign in with Microsoft</Button>
      </div>
    );
  }

  return (
    <div>
      <Button onClick={handleLogout}>Sign Out</Button>
      {/* Main app content */}
    </div>
  );
}
```

**5.3.5 Secure Backend with JWT Validation**
```python
# backend/src/api/auth.py
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from jwt import PyJWKClient

security = HTTPBearer()

AZURE_AD_TENANT_ID = os.getenv("AZURE_AD_TENANT_ID")
AZURE_AD_CLIENT_ID = os.getenv("AZURE_AD_CLIENT_ID")

jwks_url = f"https://login.microsoftonline.com/{AZURE_AD_TENANT_ID}/discovery/v2.0/keys"
jwks_client = PyJWKClient(jwks_url)

async def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Verify Azure AD JWT token."""
    token = credentials.credentials

    try:
        # Get signing key
        signing_key = jwks_client.get_signing_key_from_jwt(token)

        # Verify token
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=AZURE_AD_CLIENT_ID,
            issuer=f"https://login.microsoftonline.com/{AZURE_AD_TENANT_ID}/v2.0"
        )

        return payload
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

# Protect endpoints
@router.get("/api/metrics/oee", dependencies=[Depends(verify_token)])
async def get_oee(...):
    ...
```

**5.4 GitHub Actions CI/CD**

**5.4.1 Create Workflow File**
```yaml
# .github/workflows/azure-deploy.yml
name: Deploy to Azure Container Apps

on:
  push:
    branches: [main]
  workflow_dispatch:

env:
  ACR_NAME: factoryagentacr
  RESOURCE_GROUP: factory-agent-rg

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Azure Login
        uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}

      - name: Build and push backend image
        run: |
          az acr login --name ${{ env.ACR_NAME }}
          docker build -t ${{ env.ACR_NAME }}.azurecr.io/backend:${{ github.sha }} ./backend
          docker push ${{ env.ACR_NAME }}.azurecr.io/backend:${{ github.sha }}

      - name: Build and push frontend image
        run: |
          docker build -t ${{ env.ACR_NAME }}.azurecr.io/frontend:${{ github.sha }} ./frontend
          docker push ${{ env.ACR_NAME }}.azurecr.io/frontend:${{ github.sha }}

      - name: Update backend container app
        run: |
          az containerapp update \
            --name factory-backend \
            --resource-group ${{ env.RESOURCE_GROUP }} \
            --image ${{ env.ACR_NAME }}.azurecr.io/backend:${{ github.sha }}

      - name: Update frontend container app
        run: |
          az containerapp update \
            --name factory-frontend \
            --resource-group ${{ env.RESOURCE_GROUP }} \
            --image ${{ env.ACR_NAME }}.azurecr.io/frontend:${{ github.sha }}
```

**5.4.2 Configure GitHub Secrets**
- `AZURE_CREDENTIALS`: Service principal JSON
- `AZURE_OPENAI_KEY`: Azure OpenAI API key (single key for chat + Whisper + TTS)
- `AZURE_STORAGE_CONNECTION_STRING`: Blob storage connection
- `AZURE_AD_CLIENT_ID`: Azure AD application client ID
- `AZURE_AD_TENANT_ID`: Azure AD tenant ID

**5.5 Final Testing**
- Test full authentication flow
- Test all dashboard features on Azure
- Test chat functionality on Azure
- Test voice recording and playback
- Test auto-scaling (simulate load)
- Verify monitoring in Application Insights

**Deliverables:**
- ✅ Backend and frontend containerized
- ✅ Images in Azure Container Registry
- ✅ Both containers running in Azure Container Apps
- ✅ Azure AD authentication working
- ✅ CI/CD pipeline deploying on git push
- ✅ Production data in Blob Storage
- ✅ All features working in production

---

## 📁 Final Project Structure

```
factory-agent/
├── backend/
│   ├── src/
│   │   ├── api/
│   │   │   ├── main.py              # FastAPI app
│   │   │   ├── auth.py              # JWT validation
│   │   │   └── routes/
│   │   │       ├── metrics.py       # Metrics endpoints
│   │   │       ├── chat.py          # Chat endpoints
│   │   │       ├── voice.py         # Voice endpoints (Azure OpenAI)
│   │   │       └── data.py          # Data management
│   │   ├── services/
│   │   │   └── chat_service.py      # NEW: Chat logic (extracted from main.py)
│   │   ├── metrics.py               # EXISTING (unchanged)
│   │   ├── models.py                # EXISTING (unchanged)
│   │   ├── data.py                  # EXISTING (updated for Blob)
│   │   └── config.py                # EXISTING (updated)
│   ├── tests/
│   │   ├── test_metrics.py          # EXISTING
│   │   ├── test_chat_service.py     # MIGRATED (renamed from test_main.py)
│   │   ├── test_api.py              # NEW: API endpoint tests
│   │   └── test_auth.py             # NEW: Auth tests
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── layout/
│   │   │   │   └── SplitLayout.tsx
│   │   │   ├── dashboard/
│   │   │   │   ├── DashboardPanel.tsx
│   │   │   │   ├── OEEGauge.tsx
│   │   │   │   ├── TrendChart.tsx
│   │   │   │   ├── DowntimeTable.tsx
│   │   │   │   ├── QualityTable.tsx
│   │   │   │   └── MachineFilter.tsx
│   │   │   ├── console/
│   │   │   │   ├── ConsolePanel.tsx
│   │   │   │   ├── ChatConsole.tsx
│   │   │   │   ├── MessageList.tsx
│   │   │   │   ├── MessageItem.tsx
│   │   │   │   ├── ChatInput.tsx
│   │   │   │   ├── VoiceRecorder.tsx
│   │   │   │   └── AudioPlayer.tsx
│   │   │   └── auth/
│   │   │       ├── LoginButton.tsx
│   │   │       └── LogoutButton.tsx
│   │   ├── services/
│   │   │   ├── api.ts               # Axios client
│   │   │   └── websocket.ts         # WebSocket client
│   │   ├── authConfig.ts            # MSAL configuration
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── public/
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── package.json
│   ├── vite.config.ts
│   └── .env.example
├── .github/
│   └── workflows/
│       └── azure-deploy.yml         # CI/CD pipeline
├── docker-compose.yml               # Local development
├── .gitignore
├── README.md
└── implementation-plan.md           # This file
```

---

## 🛠️ Technical Stack Summary

### Frontend
- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **UI Library**: Material-UI (MUI)
- **Charts**: Recharts
- **Layout**: react-split-pane
- **Auth**: @azure/msal-react
- **HTTP**: Axios
- **State**: React hooks (useState, useEffect, useContext)

### Backend
- **Framework**: FastAPI
- **Runtime**: Python 3.11
- **ASGI Server**: Uvicorn
- **Auth**: PyJWT + Azure AD validation
- **AI**: OpenAI SDK (Azure OpenAI + OpenAI)
- **Storage**: Azure Blob Storage SDK
- **Testing**: pytest

### Azure Services
- **Hosting**: Azure Container Apps (consumption plan)
- **Registry**: Azure Container Registry (Basic tier)
- **Storage**: Azure Blob Storage
- **Auth**: Azure AD (Entra ID)
- **AI**: Azure OpenAI Service
- **Voice**: OpenAI Whisper + TTS APIs
- **Monitoring**: Application Insights (optional)
- **CI/CD**: GitHub Actions

### Development
- **Containers**: Docker + Docker Compose
- **Version Control**: Git + GitHub
- **API Testing**: Postman or curl
- **Local Dev**: Hot reload for both frontend and backend

---

## 💰 Cost Estimates

### Azure Container Apps (Monthly)
- **Container Apps**: ~$5-10 (consumption plan, low traffic)
- **Container Registry**: ~$5 (Basic tier)
- **Blob Storage**: ~$1 (minimal data)
- **Azure AD**: Free tier
- **Total Infrastructure**: ~$11-16/month

### AI Services (Usage-based)
- **Azure OpenAI**: ~$0.002 per 1K tokens
  - Typical chat: 500 tokens = $0.001
  - Active demo day (50 chats): ~$0.05
- **OpenAI Whisper**: $0.006/minute
  - 5-second recording: ~$0.0005
- **OpenAI TTS**: $15 per 1M characters
  - 200-char response: ~$0.003
- **Daily AI costs** (20 interactions): ~$0.10-0.20

### Total Estimated Cost
- **Low usage** (few demos): ~$12-20/month
- **Active testing**: ~$15-25/month

**Cost-saving tips:**
- Scale containers to 0 when not in use
- Use Azure free credits (12 months for new accounts)
- Monitor with cost alerts

---

## 🎓 Learning Outcomes

By completing this migration, you will gain hands-on experience with:

### Azure Services
- ✅ **Azure Container Apps**: Serverless container hosting
- ✅ **Azure Container Registry**: Private Docker registry
- ✅ **Azure Blob Storage**: Cloud object storage
- ✅ **Azure AD (Entra ID)**: Enterprise authentication
- ✅ **Azure OpenAI**: Managed AI services
- ✅ **Azure Portal**: Resource management
- ✅ **Azure CLI**: Infrastructure as Code

### Development Skills
- ✅ **FastAPI**: Modern Python web framework
- ✅ **React + TypeScript**: Frontend development
- ✅ **Docker**: Containerization and orchestration
- ✅ **GitHub Actions**: CI/CD pipelines
- ✅ **REST API design**: Backend architecture
- ✅ **WebSockets**: Real-time communication (optional)
- ✅ **JWT Authentication**: Token-based security
- ✅ **Browser APIs**: MediaRecorder, Web Audio

### Architecture Patterns
- ✅ **Microservices**: Separate frontend/backend
- ✅ **Container-based deployment**: Cloud-native apps
- ✅ **Stateless API design**: Scalable backends
- ✅ **Authentication flows**: MSAL + JWT
- ✅ **Cloud storage patterns**: Blob storage usage

---

## 🔍 Code Reuse Strategy

### Unchanged (100% Reused)
- **metrics.py** (285 lines): All 4 analysis functions work as-is
- **models.py** (86 lines): Pydantic models serialize to JSON automatically

### Minor Updates (90% Reused)
- **data.py** (245 lines): Add Blob Storage SDK, keep logic
- **config.py** (21 lines): Add Azure-specific environment variables

### Refactored (60-80% Logic Reused)
- **main.py** (613 lines): Split into shared services + FastAPI routes
  - Create `backend/src/services/chat_service.py`:
    - `get_chat_response()` - extracted from `_get_chat_response()` (unchanged logic)
    - `execute_tool()` - moved as-is from main.py
    - `TOOLS` constant - moved as-is
  - Create `backend/src/api/routes/chat.py`:
    - Uses `chat_service.get_chat_response()` in endpoint
  - **Tests updated**: `tests/test_chat_service.py` replaces `tests/test_main.py`
    - All existing test logic preserved
    - Import from `services.chat_service` instead of `main`
    - Same coverage, same assertions

### Replaced (New Code)
- **dashboard.py** (255 lines): Convert to React components
- **CLI commands**: No longer needed (web-only)

### New Code
- FastAPI application (~300 lines)
- React components (~800 lines)
- Docker configurations (~100 lines)
- GitHub Actions (~80 lines)

**Total Reuse**: ~60-70% of business logic preserved

---

## ✅ Success Criteria

### Functional Requirements
- ✅ Split-pane web interface (dashboard left, console right)
- ✅ All metrics displayed: OEE, scrap, quality, downtime
- ✅ Interactive charts and tables
- ✅ Machine filtering works across all views
- ✅ Chat interface with AI assistant
- ✅ Tool-calling for accurate data retrieval
- ✅ Voice recording and transcription
- ✅ Text-to-speech playback
- ✅ Azure AD authentication required
- ✅ Deployed and accessible via HTTPS

### Technical Requirements
- ✅ FastAPI backend with REST endpoints
- ✅ React frontend with TypeScript
- ✅ Both running in Azure Container Apps
- ✅ Data persisted in Azure Blob Storage
- ✅ Automatic deployment via GitHub Actions
- ✅ All tests passing (backend pytest)
- ✅ Proper error handling and logging
- ✅ Mobile-responsive layout (optional)

### Learning Requirements
- ✅ Understand Azure Container Apps concepts
- ✅ Can deploy containers to Azure independently
- ✅ Understand React component lifecycle
- ✅ Can add new dashboard widgets
- ✅ Can extend API with new endpoints
- ✅ Understand Azure AD authentication flow

---

## 🚀 Next Steps

1. **Review this plan** and ask questions about any unclear sections
2. **Set up local environment**:
   - Install Docker Desktop
   - Install Node.js 18+
   - Install Python 3.11+
   - Install Azure CLI
3. **Start Phase 1**: Backend API development
4. **Iterate phase by phase**: Test thoroughly at each stage
5. **Deploy to Azure**: Complete Phase 5 deployment

**Ready to begin? Let's start with Phase 1: Backend API Setup!**

---

## 📚 Helpful Resources

### Azure Documentation
- [Azure Container Apps](https://learn.microsoft.com/en-us/azure/container-apps/)
- [Azure AD MSAL.js](https://learn.microsoft.com/en-us/azure/active-directory/develop/msal-js-initializing-client-applications)
- [Azure Blob Storage Python SDK](https://learn.microsoft.com/en-us/azure/storage/blobs/storage-quickstart-blobs-python)

### Framework Documentation
- [FastAPI](https://fastapi.tiangolo.com/)
- [React TypeScript](https://react-typescript-cheatsheet.netlify.app/)
- [Recharts](https://recharts.org/en-US/)
- [Material-UI](https://mui.com/material-ui/getting-started/)

### Tutorials
- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)
- [React Beginner Guide](https://react.dev/learn)
- [Docker for Python Apps](https://docs.docker.com/language/python/)

---

**Document Version**: 2.4
**Last Updated**: 2025-11-03
**Author**: Migration Planning Assistant
**Status**: Phase 2 Complete! - Ready for Phase 3 React Frontend Development
