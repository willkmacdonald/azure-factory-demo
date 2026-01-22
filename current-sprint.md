# Current Sprint: Static Web Apps Migration

**Sprint Goal**: Migrate frontend from Container Apps to Static Web Apps (Free tier)
**Started**: 2026-01-21
**Target**: 2026-01-22
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
- **Next session**: Start PR37 (Infrastructure - Bicep templates)

---

## Sprint Overview

| PR | Title | Effort | Status | Dependencies |
|----|-------|--------|--------|--------------|
| PR36 | Frontend SWA Configuration | 30 min | ✅ COMPLETE | None |
| PR36b | Test helpers to conftest.py | 15 min | ✅ COMPLETE | None |
| PR37 | Infrastructure (Bicep) | 30 min | Not Started | PR36 |
| PR38 | GitHub Actions Workflow | 30 min | Not Started | PR37 |
| PR39 | Cleanup & Documentation | 15 min | Not Started | PR38 deployed |

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

## PR37: Infrastructure (Bicep)

**Branch**: `feature/swa-infrastructure`
**Effort**: 30 minutes
**Status**: Not Started
**Depends On**: PR36 merged

### Goal
Create Bicep template for Static Web Apps and update backend CORS.

### Tasks

- [ ] Create `infra/staticwebapp.bicep`
  - Free tier SKU
  - Location: eastus (same as backend)
  - Output: default hostname for CORS config

- [ ] Update `infra/backend.bicep`
  - Add `*.azurestaticapps.net` to ALLOWED_ORIGINS
  - Keep existing Container Apps domain

- [ ] Validate Bicep templates
  - Run `az bicep build --file infra/staticwebapp.bicep`
  - Run `az bicep build --file infra/backend.bicep`

- [ ] Deploy SWA resource (manual)
  - Run deployment to create empty SWA
  - Get deployment token for GitHub Actions

### Files Changed

| File | Action |
|------|--------|
| `infra/staticwebapp.bicep` | Create |
| `infra/backend.bicep` | Edit (CORS) |

### Acceptance Criteria

- [ ] Bicep templates validate without errors
- [ ] SWA resource created in Azure
- [ ] Deployment token retrieved and ready for GitHub secret

### Manual Steps (Post-PR)

```bash
# Deploy Static Web App resource
az deployment group create \
  --resource-group factory-agent-dev-rg \
  --template-file infra/staticwebapp.bicep \
  --parameters name=factory-agent-frontend

# Get deployment token
az staticwebapp secrets list \
  --name factory-agent-frontend \
  --resource-group factory-agent-dev-rg \
  --query "properties.apiKey" -o tsv
```

---

## PR38: GitHub Actions Workflow

**Branch**: `feature/swa-github-actions`
**Effort**: 30 minutes
**Status**: Not Started
**Depends On**: PR37 merged, SWA resource exists, GitHub secrets configured

### Goal
Replace Docker-based deployment with Static Web Apps deployment.

### Tasks

- [ ] Add GitHub secrets (manual, before PR)
  - `AZURE_STATIC_WEB_APPS_API_TOKEN` - from PR37
  - `VITE_API_BASE_URL` - backend Container App URL

- [ ] Replace `.github/workflows/deploy-frontend.yml`
  - Remove Docker build steps
  - Remove ACR push steps
  - Add Node.js setup
  - Add npm build with env vars
  - Add SWA deploy action

- [ ] Test deployment
  - Push to trigger workflow
  - Verify GitHub Action succeeds
  - Verify frontend loads at SWA URL

### Files Changed

| File | Action |
|------|--------|
| `.github/workflows/deploy-frontend.yml` | Replace |

### New Workflow Structure

```yaml
name: Deploy Frontend (Static Web Apps)

on:
  push:
    branches: [main]
    paths: ['frontend/**']
  workflow_dispatch:

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: '22'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json

      - name: Install and build
        working-directory: frontend
        env:
          VITE_API_BASE_URL: ${{ secrets.VITE_API_BASE_URL }}
        run: |
          npm ci
          npm run build

      - name: Deploy
        uses: Azure/static-web-apps-deploy@v1
        with:
          azure_static_web_apps_api_token: ${{ secrets.AZURE_STATIC_WEB_APPS_API_TOKEN }}
          repo_token: ${{ secrets.GITHUB_TOKEN }}
          action: 'upload'
          app_location: 'frontend'
          output_location: 'dist'
          skip_app_build: true
```

### Acceptance Criteria

- [ ] GitHub Action runs successfully
- [ ] Frontend accessible at `*.azurestaticapps.net`
- [ ] All pages load (Dashboard, Machines, Alerts, Chat, Traceability)
- [ ] API calls succeed (no CORS errors)
- [ ] Azure AD login works

### Pre-PR Manual Steps

```bash
# Add GitHub secrets (Settings > Secrets and variables > Actions)
# 1. AZURE_STATIC_WEB_APPS_API_TOKEN = <from PR37>
# 2. VITE_API_BASE_URL = https://factory-agent-dev-backend.mangotree-xxx.eastus.azurecontainerapps.io
```

---

## PR39: Cleanup & Documentation

**Branch**: `feature/swa-cleanup`
**Effort**: 15 minutes
**Status**: Not Started
**Depends On**: PR38 deployed and verified

### Goal
Remove obsolete Container Apps files and update documentation.

### Tasks

- [ ] Delete obsolete files
  - `frontend/Dockerfile`
  - `frontend/docker-entrypoint.sh`
  - `frontend/nginx.conf`
  - `infra/frontend.bicep`

- [ ] Update README.md
  - Update architecture section
  - Update deployment instructions
  - Note Static Web Apps URL

- [ ] Update `.claude/CLAUDE.md`
  - Update tech stack (remove Nginx/Docker for frontend)
  - Update deployment approach section

- [ ] Delete old Container App resource (manual)
  - Remove frontend Container App from Azure
  - Update any DNS/custom domains

### Files Changed

| File | Action |
|------|--------|
| `frontend/Dockerfile` | Delete |
| `frontend/docker-entrypoint.sh` | Delete |
| `frontend/nginx.conf` | Delete |
| `infra/frontend.bicep` | Delete |
| `README.md` | Edit |
| `.claude/CLAUDE.md` | Edit |

### Acceptance Criteria

- [ ] No Docker files in `frontend/`
- [ ] No `frontend.bicep` in `infra/`
- [ ] README reflects new architecture
- [ ] Old Container App deleted from Azure

### Post-PR Manual Steps

```bash
# Delete old frontend Container App
az containerapp delete \
  --name factory-agent-dev-frontend \
  --resource-group factory-agent-dev-rg \
  --yes
```

---

## Verification Checklist

After all PRs merged:

- [ ] **Local dev**: `npm run dev` works with localhost backend
- [ ] **SPA routing**: Direct navigation to `/machines`, `/chat` works
- [ ] **API calls**: Dashboard loads data from backend
- [ ] **Security headers**: X-Frame-Options, CSP visible in DevTools
- [ ] **Auth**: Azure AD sign-in/sign-out works
- [ ] **Dark mode**: Theme toggle works
- [ ] **Mobile**: Responsive layout intact

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
