# Current Sprint: Static Web Apps Migration ✅ COMPLETE

**Sprint Goal**: Migrate frontend from Container Apps to Static Web Apps (Free tier)
**Started**: 2026-01-21
**Completed**: 2026-01-22
**Total Effort**: ~2 hours

---

## Session Log

### 2026-01-21: Planning Session
- Researched Azure deployment options and pricing
- Decided: Migrate frontend to Static Web Apps (Free tier) - saves $60-180/year
- Decided: Keep ACR on Basic tier (sufficient for 2 small images)
- Created `implementation-plan.md` for Phase 7
- Created `docs/specs/frontend-design.md` with full migration architecture
- Created `docs/specs/backend-design.md` documenting current backend
- Archived Phase 1-6 plan to `docs/archive/implementation-plan-phase6-complete.md`
- **Next session**: Start PR36 (SWA configuration)

### 2026-01-21: Implementation Session
- **PR36 (COMPLETE)**: Frontend SWA Configuration
  - Created `frontend/staticwebapp.config.json` with SPA routing, security headers, caching
  - Updated `frontend/src/api/client.ts` - removed `window.ENV` runtime config
  - Updated `frontend/src/hooks/useChat.ts` - removed `window.ENV` reference
  - Verified `npm run build` succeeds
  - PR merged: https://github.com/willkmacdonald/azure-factory-demo/pull/4
- **PR36b (COMPLETE)**: Test refactoring (unplanned)
  - Moved test helpers from `test_blob_storage.py` to `conftest.py`
  - Follows CLAUDE.md directive: tests should not contain business logic
  - All 24 blob storage tests pass
  - PR merged: https://github.com/willkmacdonald/azure-factory-demo/pull/5

### 2026-01-21: Context Load Session (brief)
- Loaded project context via `/load-context`
- Ran `/review-and-fix` - no code changes to review (only docs)
- Created `docs/NEW-TENANT-DEPLOYMENT-CHECKLIST.md` (untracked)
- **Next session**: Start PR37 (Infrastructure - Bicep templates)

### 2026-01-21: PR37 Implementation Session
- **PR37 (COMPLETE)**: Infrastructure - Bicep templates
  - Created `infra/staticwebapp.bicep` with Free tier SKU
  - Updated `infra/backend.bicep` with `staticWebAppHostname` parameter for CORS
  - Both templates validated with `az bicep build`
  - PR created: https://github.com/willkmacdonald/azure-factory-demo/pull/6
- Discussed safe decommissioning approach for PR39 (target `factory-agent-dev-frontend` by name only)
- **Next session**: Merge PR37, deploy SWA resource manually, start PR38

### 2026-01-22: PR38 Implementation Session
- **PR37 merged** to main (fast-forward)
- **SWA resource deployed** via Bicep
  - Name: `factory-agent-dev-frontend-swa`
  - URL: https://gray-ground-0bab7600f.2.azurestaticapps.net
  - SKU: Free tier
- **GitHub secrets added**:
  - `AZURE_STATIC_WEB_APPS_API_TOKEN`
  - `VITE_API_BASE_URL` (backend URL)
- **Backend CORS updated** to allow SWA domain
- **PR38 (COMPLETE)**: GitHub Actions Workflow
  - Replaced Docker-based workflow with SWA deployment
  - Fixed: `app_location` must point to `frontend/dist` (not `frontend`)
  - Fixed: Must copy `staticwebapp.config.json` to dist folder
  - PR merged: https://github.com/willkmacdonald/azure-factory-demo/pull/7
- **Verification tests passed**:
  - SPA routing: All pages return 200
  - Security headers: All present (X-Frame-Options, CSP, etc.)
  - Backend health: Healthy
  - CORS: SWA origin allowed
  - API data: Working
- **Next session**: PR39 (Cleanup & Documentation)

### 2026-01-22: PR39 Completion Session
- **PR39 (COMPLETE)**: Cleanup & Documentation
  - Deleted `frontend/Dockerfile`, `docker-entrypoint.sh`, `nginx.conf`
  - Deleted `infra/frontend.bicep`
  - Updated `.claude/CLAUDE.md` (local only - gitignored)
  - PR merged: https://github.com/willkmacdonald/azure-factory-demo/pull/8
- **Old Container App deleted**: `factory-agent-dev-frontend` removed from Azure
- **Phase 7 COMPLETE** 🎉

### 2026-01-22: Cost Optimization Session
- **Analyzed Azure billing** - found $41/month ACR charges
- **Deleted empty `slidemakerACR`** - saves ~$20/month
- **Downgraded `factoryagent4u4zqkacr`** from Standard to Basic - saves ~$15/month
- **Set `minReplicas: 1`** on backend - warm container, no cold starts (+$10-15/month)
- **Fixed CORS** - added SWA hostname to allowed origins
- **Committed infra changes** - `backend.bicep` defaults to minReplicas=1, workflow uses staticWebAppHostname
- **Net monthly savings**: ~$20-25/month (from ~$45 to ~$20-25)
- **New architecture verified**: Frontend instant, backend instant (warm container)

---

## Sprint Overview

| PR | Title | Effort | Status | Dependencies |
|----|-------|--------|--------|--------------|
| PR36 | Frontend SWA Configuration | 30 min | ✅ COMPLETE | None |
| PR36b | Test helpers to conftest.py | 15 min | ✅ COMPLETE | None |
| PR37 | Infrastructure (Bicep) | 30 min | ✅ COMPLETE | PR36 |
| PR38 | GitHub Actions Workflow | 30 min | ✅ COMPLETE | PR37 + manual deploy |
| PR39 | Cleanup & Documentation | 15 min | ✅ COMPLETE | PR38 deployed |

---

## PR36: Frontend SWA Configuration ✅ COMPLETE

**Branch**: `feature/swa-frontend-config` (merged)
**Effort**: 30 minutes
**Status**: ✅ COMPLETE
**PR**: https://github.com/willkmacdonald/azure-factory-demo/pull/4

### Goal
Prepare the React frontend for Static Web Apps by adding SWA configuration and simplifying the API client.

### Tasks

- [x] Create `frontend/staticwebapp.config.json`
  - SPA navigation fallback (rewrite to index.html)
  - Security headers (X-Frame-Options, CSP, etc.)
  - Asset caching rules

- [x] Update `frontend/src/api/client.ts`
  - Remove `window.ENV` runtime config dependency
  - Use build-time `import.meta.env.VITE_API_BASE_URL` only
  - Keep localhost fallback for local development

- [x] Update `frontend/src/hooks/useChat.ts` (discovered during implementation)
  - Also had `window.ENV` reference

- [x] Verify local build
  - Run `cd frontend && npm run build`
  - Confirm no errors
  - Check `dist/` output is valid

### Files Changed

| File | Action |
|------|--------|
| `frontend/staticwebapp.config.json` | Create |
| `frontend/src/api/client.ts` | Edit |
| `frontend/src/hooks/useChat.ts` | Edit |

### Acceptance Criteria

- [x] `npm run build` succeeds
- [x] `staticwebapp.config.json` includes all security headers from nginx.conf
- [x] API client uses build-time env only

---

## PR37: Infrastructure (Bicep) ✅ COMPLETE

**Branch**: `feature/swa-infrastructure` (merged)
**Effort**: 30 minutes
**Status**: ✅ COMPLETE
**PR**: https://github.com/willkmacdonald/azure-factory-demo/pull/6

### Goal
Create Bicep template for Static Web Apps and update backend CORS.

### Tasks

- [x] Create `infra/staticwebapp.bicep`
  - Free tier SKU
  - Location: eastus2 (SWA has limited region availability)
  - Output: default hostname for CORS config

- [x] Update `infra/backend.bicep`
  - Added `staticWebAppHostname` parameter for CORS
  - CORS computed as: user origins + SWA origin (if provided)
  - Backwards compatible

- [x] Validate Bicep templates
  - Run `az bicep build --file infra/staticwebapp.bicep`
  - Run `az bicep build --file infra/backend.bicep`

- [ ] Deploy SWA resource (manual, post-merge)
  - Run deployment to create empty SWA
  - Get deployment token for GitHub Actions

### Files Changed

| File | Action |
|------|--------|
| `infra/staticwebapp.bicep` | Create |
| `infra/backend.bicep` | Edit (CORS) |

### Acceptance Criteria

- [x] Bicep templates validate without errors
- [ ] SWA resource created in Azure (manual step)
- [ ] Deployment token retrieved and ready for GitHub secret (manual step)

### Manual Steps (Post-Merge)

```bash
# Deploy Static Web App resource
az deployment group create \
  --resource-group factory-agent-dev-rg \
  --template-file infra/staticwebapp.bicep \
  --parameters environmentName=dev

# Get deployment token
az staticwebapp secrets list \
  --name factory-agent-dev-frontend-swa \
  --resource-group factory-agent-dev-rg \
  --query "properties.apiKey" -o tsv
```

---

## PR38: GitHub Actions Workflow ✅ COMPLETE

**Branch**: `feature/swa-github-actions` (merged)
**Effort**: 30 minutes
**Status**: ✅ COMPLETE
**PR**: https://github.com/willkmacdonald/azure-factory-demo/pull/7

### Goal
Replace Docker-based deployment with Static Web Apps deployment.

### Tasks

- [x] Add GitHub secrets (manual, before PR)
  - `AZURE_STATIC_WEB_APPS_API_TOKEN` - from PR37
  - `VITE_API_BASE_URL` - backend Container App URL

- [x] Replace `.github/workflows/deploy-frontend.yml`
  - Remove Docker build steps
  - Remove ACR push steps
  - Add Node.js setup
  - Add npm build with env vars
  - Add SWA deploy action

- [x] Test deployment
  - Push to trigger workflow
  - Verify GitHub Action succeeds
  - Verify frontend loads at SWA URL

### Files Changed

| File | Action |
|------|--------|
| `.github/workflows/deploy-frontend.yml` | Replace |

### Learnings

- `app_location` must point directly to `frontend/dist` (not `frontend`) when using `skip_app_build: true`
- `staticwebapp.config.json` must be copied to `dist/` folder during build (not auto-detected when app_location is dist)
- Workflow simplified from 348 lines (3 jobs) to 108 lines (1 job)

### Acceptance Criteria

- [x] GitHub Action runs successfully
- [x] Frontend accessible at https://gray-ground-0bab7600f.2.azurestaticapps.net
- [x] All pages load (Dashboard, Machines, Alerts, Chat, Traceability)
- [x] API calls succeed (no CORS errors)
- [ ] Azure AD login works (manual test pending)

---

## PR39: Cleanup & Documentation ✅ COMPLETE

**Branch**: `feature/swa-cleanup` (merged)
**Effort**: 15 minutes
**Status**: ✅ COMPLETE
**PR**: https://github.com/willkmacdonald/azure-factory-demo/pull/8

### Goal
Remove obsolete Container Apps files and update documentation.

### Tasks

- [x] Delete obsolete files
  - `frontend/Dockerfile`
  - `frontend/docker-entrypoint.sh`
  - `frontend/nginx.conf`
  - `infra/frontend.bicep`

- [x] Update README.md (done in weekly-docs)
  - Update architecture section
  - Update deployment instructions
  - Note Static Web Apps URL

- [x] Update `.claude/CLAUDE.md` (local only - gitignored)
  - Update tech stack (remove Nginx/Docker for frontend)
  - Update deployment approach section

- [x] Delete old Container App resource (manual)
  - Removed `factory-agent-dev-frontend` from Azure

### Files Changed

| File | Action |
|------|--------|
| `frontend/Dockerfile` | Deleted |
| `frontend/docker-entrypoint.sh` | Deleted |
| `frontend/nginx.conf` | Deleted |
| `infra/frontend.bicep` | Deleted |

### Acceptance Criteria

- [x] No Docker files in `frontend/`
- [x] No `frontend.bicep` in `infra/`
- [x] README reflects new architecture
- [x] Old Container App deleted from Azure

---

## Verification Checklist

After all PRs merged:

- [x] **SPA routing**: Direct navigation to `/machines`, `/chat` works
- [x] **API calls**: Dashboard loads data from backend
- [x] **Security headers**: X-Frame-Options, CSP visible in DevTools
- [x] **CORS**: SWA origin allowed by backend
- [ ] **Local dev**: `npm run dev` works with localhost backend (not tested)
- [ ] **Auth**: Azure AD sign-in/sign-out works (manual test pending)
- [ ] **Dark mode**: Theme toggle works (manual test pending)
- [ ] **Mobile**: Responsive layout intact (manual test pending)

---

## Rollback Plan

If issues after deployment:

1. **Restore old workflow**
   ```bash
   git checkout HEAD~1 -- .github/workflows/deploy-frontend.yml
   git commit -m "Rollback: Restore Container Apps deployment"
   git push
   ```

2. **Redeploy Container App**
   ```bash
   az deployment group create \
     --resource-group factory-agent-dev-rg \
     --template-file infra/frontend.bicep
   ```

3. **Delete SWA resource**
   ```bash
   az staticwebapp delete \
     --name factory-agent-frontend \
     --resource-group factory-agent-dev-rg
   ```

---

## Notes

- Backend stays on Container Apps (unchanged)
- ACR still needed for backend images
- Free tier includes 100GB bandwidth/month (sufficient for demo)
- Custom domains can be added later if needed
