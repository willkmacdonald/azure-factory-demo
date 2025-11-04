# Azure Migration Implementation Plan
## Factory Agent: Streamlit/CLI → React + Azure Container Apps

**Version:** 3.0
**Created:** 2025-01-01
**Last Updated:** 2025-11-04
**Target Timeline:** 4-5 weeks
**Architecture:** Azure Container Apps + FastAPI + React

---

## Current Status

**Phase**: Phase 3 - React Frontend Development (IN PROGRESS)
**Last Completed**: PR12 - Dashboard Layout & Navigation (2025-11-03)
**Next Priority**: PR13 - Metrics Dashboard & Charts

### Summary
Phase 1 (Backend API Foundation) and Phase 2 (Azure Blob Storage Integration) are complete! React project structure is now in place with Vite + React + TypeScript, Material-UI, Recharts, and Axios. Navigation infrastructure is ready. Now implementing data visualization and features.

**Progress - Phase 1**: 3/3 core PRs complete (100%)
- PR6: Async Chat API ✅ COMPLETE
- PR7: Production Hardening & Rate Limiting ✅ COMPLETE
- PR8: Conversation History Validation ✅ COMPLETE

**Progress - Phase 2**: 3/3 PRs complete (100%)
- Azure Storage Account Setup ✅ COMPLETE
- PR9: Blob Storage Implementation ✅ COMPLETE
- PR10: Comprehensive Testing & Dependency Fixes ✅ COMPLETE

**Progress - Phase 3**: 2/7 PRs complete (29%)
- PR11: Core API Client & Data Models ✅ COMPLETE
- PR12: Dashboard Layout & Navigation ✅ COMPLETE
- PR13: Metrics Dashboard & Charts (IN PROGRESS)
- PR14: Machine Status & Alerts View (PLANNED)
- PR15: AI Chat Interface (PLANNED)
- PR16: Authentication & Azure AD Integration (PLANNED)
- PR17: Deployment & CI/CD (PLANNED)

---

## 📚 Completed Work (Archive)

> **Full completion documentation moved to:** `/docs/archive/implementation-plan-backup-2025-11-04.md`

### Phase 1: Backend API Foundation ✅
- **PR6**: Async Chat API with FastAPI routes
- **PR7**: Production hardening (rate limiting, CORS)
- **PR8**: Conversation history validation & error handling

### Phase 2: Azure Blob Storage Integration ✅
- **Azure Storage**: Storage account created, blob container configured
- **PR9**: Async blob storage operations with dual-mode support
- **PR10**: Comprehensive test suite (47 tests)

### Phase 3: React Frontend - In Progress
- **PR11**: Core API client, TypeScript models, health check component
- **PR12**: Navigation infrastructure, responsive layout, placeholder pages

---

## 🚧 Upcoming PRs - Phase 3

### 🚧 PR13: Metrics Dashboard & Charts
**Status**: IN PROGRESS
**Priority**: HIGH
**Estimated Effort**: 4-5 hours

#### Overview
Build the metrics overview page with cards for key statistics and implement Recharts visualizations. This is the core dashboard view users see first.

#### Tasks

- [ ] CRITICAL: Move API service to correct directory structure (frontend/src/api/client.ts)
  - **Priority**: CRITICAL
  - **Effort**: Quick (<5 minutes)
  - **Context**: PR12 code review found API directory structure mismatch with CLAUDE.md specs
  - **Details**:
    - Move frontend/src/services/api.ts to frontend/src/api/client.ts
    - Update all imports from "frontend/src/services/api" to "frontend/src/api/client"
    - Rationale: CLAUDE.md specifies API client layer should be in `frontend/src/api/` directory
    - Files to update:
      - frontend/src/services/api.ts → frontend/src/api/client.ts
      - frontend/src/App.tsx (import statement)
      - frontend/src/components/ApiHealthCheck.tsx (import statement)

- [ ] Build metrics overview page with statistic cards (frontend/src/pages/Dashboard.tsx)
  - **Priority**: HIGH
  - **Effort**: Medium (1.5 hours)
  - **Context**: Main dashboard page layout
  - **Details**:
    - Grid layout with cards: Current OEE, Production Rate, Quality Score, Uptime %
    - Date range picker for filtering
    - Machine dropdown filter
    - Loading skeleton while data loads
    - Error state with retry button
    - Real-time data refresh (optional polling)

- [ ] Implement Recharts visualizations for production trends (frontend/src/components/charts/)
  - **Priority**: HIGH
  - **Effort**: Medium (2 hours)
  - **Context**: 3 main charts
  - **Details**:
    - OEETrendChart.tsx: LineChart showing daily OEE % over time
    - ProductionRateChart.tsx: AreaChart showing production rate trend
    - EfficiencyBreakdownChart.tsx: PieChart showing availability/performance/quality split
    - All charts responsive, labeled axes, tooltips
    - Click legend to show/hide series

- [ ] Create reusable chart components (frontend/src/components/charts/ChartContainer.tsx)
  - **Priority**: HIGH
  - **Effort**: Quick (1 hour)
  - **Context**: Wrapper for all charts
  - **Details**:
    - ChartContainer: Loading state, error handling, empty state
    - ChartLegend: Custom legend for Recharts
    - ChartTooltip: Formatted tooltip component
    - Theme colors for consistency

- [ ] Add real-time data fetching from backend API (frontend/src/hooks/useMetrics.ts)
  - **Priority**: HIGH
  - **Effort**: Medium (1 hour)
  - **Context**: Custom hook for metrics data
  - **Details**:
    - useMetrics hook with loading/error state
    - Auto-fetch on mount and filter changes
    - Optional polling with configurable interval
    - Caching to avoid duplicate requests
    - Error recovery with retry

#### Deliverables
- ✅ Metrics dashboard page with statistics cards
- ✅ 3 interactive Recharts charts
- ✅ Reusable chart wrapper components
- ✅ Real-time data fetching with caching

---

### 📋 PR14: Machine Status & Alerts View
**Status**: Planned
**Priority**: MEDIUM
**Estimated Effort**: 3-4 hours

#### Overview
Create machine list view with status indicators and alerts notification system. Provides operational visibility into individual machines.

#### Tasks

- [ ] Create machine list view with status indicators (frontend/src/pages/Machines.tsx)
  - **Priority**: MEDIUM
  - **Effort**: Medium (1.5 hours)
  - **Details**:
    - MUI DataGrid for machine list
    - Columns: Name, Status, OEE, Last Updated, Actions
    - Status indicator: Green (Running), Yellow (Warning), Red (Down)
    - Sort and filter capabilities
    - Click machine to view details

- [ ] Build alert notification system (frontend/src/components/alerts/AlertNotification.tsx)
  - **Priority**: MEDIUM
  - **Effort**: Medium (1.5 hours)
  - **Details**:
    - Alert card component with severity colors
    - Alert list showing recent alerts (last 10)
    - Filter by machine and severity
    - Mark alert as resolved
    - Toast notifications for new alerts

- [ ] Add filtering and sorting capabilities (frontend/src/hooks/useMachineFilter.ts)
  - **Priority**: MEDIUM
  - **Effort**: Quick (45 minutes)
  - **Details**:
    - Filter by status (Running, Warning, Down)
    - Sort by Name, OEE, Last Updated
    - Search by machine name
    - Persist filters in URL params

- [ ] Implement machine detail view (frontend/src/pages/MachineDetail.tsx)
  - **Priority**: MEDIUM
  - **Effort**: Medium (1 hour)
  - **Details**:
    - Machine stats: Current OEE, Status, Efficiency, Performance, Quality
    - Last 30 days trend chart
    - Recent alerts for this machine

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
  - **Details**:
    - Message list with auto-scroll to bottom
    - Message styling: different colors for user/assistant
    - Timestamp on each message
    - Loading indicator while waiting for response
    - Chat history persisted in component state

- [ ] Integrate with backend /api/chat endpoint (frontend/src/hooks/useChat.ts)
  - **Priority**: MEDIUM
  - **Effort**: Medium (1 hour)
  - **Details**:
    - useChat hook managing conversation state
    - Send message function with error handling
    - Conversation history management (max 50 messages)
    - Optimistic updates (show user message immediately)
    - Error recovery with retry

- [ ] Add typing indicators and loading states (frontend/src/components/chat/TypingIndicator.tsx)
  - **Priority**: MEDIUM
  - **Effort**: Quick (45 minutes)
  - **Details**:
    - Animated typing indicator when AI is responding
    - Loading spinner on send button
    - Disable input while waiting for response

- [ ] Implement suggested questions/prompts (frontend/src/components/chat/SuggestedPrompts.tsx)
  - **Priority**: MEDIUM
  - **Effort**: Quick (45 minutes)
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
  - **Details**:
    - Configure MSAL with Azure AD app registration
    - Set client ID, tenant ID, redirect URI
    - Create msalInstance and wrap App with MsalProvider

- [ ] Implement login/logout flow (frontend/src/components/auth/AuthButtons.tsx)
  - **Priority**: LOW
  - **Effort**: Medium (1 hour)
  - **Details**:
    - Login button with MSAL popup
    - Logout button
    - User profile display (optional)
    - Handle auth errors gracefully

- [ ] Add protected routes (frontend/src/components/auth/ProtectedRoute.tsx)
  - **Priority**: LOW
  - **Effort**: Quick (45 minutes)
  - **Details**:
    - ProtectedRoute component checking authentication
    - Redirect to login if not authenticated
    - Pass auth token to API client

- [ ] Configure redirect URIs and tenant settings (documentation)
  - **Priority**: LOW
  - **Effort**: Quick (30 minutes)
  - **Details**:
    - Document Azure AD app registration steps
    - List required redirect URIs
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
  - **Details**:
    - Multi-stage build: Node build stage + Nginx serve stage
    - Build stage: Install dependencies, build with Vite
    - Production stage: Alpine nginx, copy built assets
    - Non-root user for security

- [ ] Create nginx configuration (frontend/nginx.conf)
  - **Priority**: MEDIUM
  - **Effort**: Quick (30 minutes)
  - **Details**:
    - Serve static files from /dist
    - SPA routing: Fallback to index.html
    - Proxy /api requests to backend
    - GZIP compression
    - Cache headers for assets

- [ ] Update GitHub Actions workflow for frontend build/deploy
  - **Priority**: MEDIUM
  - **Effort**: Medium (1 hour)
  - **Details**:
    - Add frontend Docker build step
    - Add frontend Docker push step
    - Add frontend Container Apps update step
    - Test step: npm run build succeeds
    - Use secrets for Azure credentials

- [ ] Configure Azure Container Apps for frontend container
  - **Priority**: MEDIUM
  - **Effort**: Quick (45 minutes)
  - **Details**:
    - Frontend Container App with 80 port exposure
    - Environment variables: VITE_API_URL pointing to backend
    - Min/max replicas configuration
    - Ingress configuration for HTTPS

- [ ] Add environment variable configuration (frontend/.env.example)
  - **Priority**: MEDIUM
  - **Effort**: Quick (15 minutes)
  - **Details**:
    - VITE_API_URL: Backend API URL
    - VITE_AZURE_AD_CLIENT_ID: Azure AD client ID
    - VITE_AZURE_AD_TENANT_ID: Azure AD tenant ID
    - VITE_REDIRECT_URI: Auth redirect URI

#### Deliverables
- ✅ Frontend Dockerfile with multi-stage build
- ✅ Nginx configuration for SPA + API proxying
- ✅ Updated GitHub Actions workflow
- ✅ Azure Container Apps deployment documentation

---

## 🎯 Future Work Items

### Phase 4: Voice Integration (Post-Phase 3)
**Target**: Week 3-4 implementation
**Key Tasks**:
- Add transcribe endpoint (Azure OpenAI Whisper)
- Add synthesize endpoint (Azure OpenAI TTS)
- Build voice UI components

### Phase 5: Enhanced Deployment (Post-Phase 4)
**Target**: Week 4-5 implementation
**Key Tasks**:
- Production monitoring and logging
- Performance optimization
- Cost optimization
- Security hardening

---

## 🏗️ Architecture Overview

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
│  Uses: Material-UI, Recharts, React Router              │
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
│  - POST /api/chat                                        │
│  - POST /api/setup                                       │
│                                                           │
│  Reused Code:                                            │
│  - metrics.py (unchanged)                                │
│  - models.py (unchanged)                                 │
│  - data.py (Azure Blob Storage support)                  │
└──────────────────────────────────────────────────────────┘
                            ↓
                  Azure Blob Storage
                  (Factory data persistence)
```

---

## 🛠️ Technical Stack Summary

### Frontend
- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **UI Library**: Material-UI (MUI)
- **Charts**: Recharts
- **Routing**: React Router v6
- **Auth**: @azure/msal-react
- **HTTP**: Axios

### Backend
- **Framework**: FastAPI
- **Runtime**: Python 3.11
- **ASGI Server**: Uvicorn
- **Auth**: PyJWT + Azure AD validation
- **AI**: OpenAI SDK (Azure OpenAI)
- **Storage**: Azure Blob Storage SDK
- **Testing**: pytest (79+ tests)

### Azure Services
- **Hosting**: Azure Container Apps
- **Registry**: Azure Container Registry
- **Storage**: Azure Blob Storage
- **Auth**: Azure AD (Entra ID)
- **AI**: Azure OpenAI Service
- **CI/CD**: GitHub Actions

---

## 💰 Cost Estimates

### Azure Infrastructure (Monthly)
- **Container Apps**: ~$5-10 (consumption plan)
- **Container Registry**: ~$5 (Basic tier)
- **Blob Storage**: ~$1 (minimal data)
- **Azure AD**: Free tier
- **Total**: ~$11-16/month

### AI Services (Usage-based)
- **Azure OpenAI**: ~$0.002 per 1K tokens
- **Daily AI costs** (20 interactions): ~$0.10-0.20

**Total Estimated**: ~$12-25/month depending on usage

---

## ✅ Success Criteria

### Functional Requirements
- ✅ Modern web interface with responsive layout
- ✅ All metrics displayed: OEE, scrap, quality, downtime
- ✅ Interactive charts and tables
- ✅ Machine filtering works across all views
- ✅ Chat interface with AI assistant
- ✅ Tool-calling for accurate data retrieval
- ✅ Azure AD authentication
- ✅ Deployed and accessible via HTTPS

### Technical Requirements
- ✅ FastAPI backend with REST endpoints
- ✅ React frontend with TypeScript
- ✅ Both running in Azure Container Apps
- ✅ Data persisted in Azure Blob Storage
- ✅ Automatic deployment via GitHub Actions
- ✅ All tests passing (79+ tests)
- ✅ Proper error handling and logging

---

## 🚀 Next Steps

1. **Complete PR13**: Metrics Dashboard & Charts (IN PROGRESS)
2. **Continue Phase 3**: PRs 14-17 implementation
3. **Test thoroughly**: Each component before PR merge
4. **Deploy incrementally**: Test each feature in Azure
5. **Monitor costs**: Use Azure cost alerts

**Current Focus: PR13 - Metrics Dashboard & Charts**

---

## 📚 Documentation & Resources

### Project Documentation
- **Full PR history**: `/docs/archive/implementation-plan-backup-2025-11-04.md`
- **Completion docs**: `/docs/archive/PR*-COMPLETION.md`
- **Architecture guide**: `CLAUDE.md`

### Azure Documentation
- [Azure Container Apps](https://learn.microsoft.com/en-us/azure/container-apps/)
- [Azure Blob Storage Python SDK](https://learn.microsoft.com/en-us/azure/storage/blobs/storage-quickstart-blobs-python)
- [Azure AD MSAL.js](https://learn.microsoft.com/en-us/azure/active-directory/develop/msal-js-initializing-client-applications)

### Framework Documentation
- [FastAPI](https://fastapi.tiangolo.com/)
- [React TypeScript](https://react-typescript-cheatsheet.netlify.app/)
- [Recharts](https://recharts.org/en-US/)
- [Material-UI](https://mui.com/material-ui/getting-started/)

---

**Document Version**: 3.0
**Last Updated**: 2025-11-04
**Status**: Phase 3 In Progress - PR13 Active
