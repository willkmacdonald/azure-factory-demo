# Factory Agent - Implementation Plan

**Last Updated**: 2026-01-22
**Project Status**: Phase 7 COMPLETE ✅ | All Phases Done
**Current Focus**: Maintenance mode - all planned features implemented

---

## Phase 7: Frontend Migration to Azure Static Web Apps ✅ COMPLETE

**Status**: ✅ COMPLETE (2026-01-22)
**Priority**: MEDIUM - Cost optimization
**Actual Effort**: ~2 hours
**Goal**: Reduce hosting costs by moving React frontend from Container Apps to Static Web Apps (Free tier)
**Result**: Frontend on SWA Free tier, backend warm (minReplicas=1), ~$20-25/month total

---

### Cost Analysis

#### Frontend Hosting Comparison

| Option | Monthly Cost | Notes |
|--------|-------------|-------|
| Container Apps (current) | ~$5-15/month | Environment overhead even with scale-to-zero |
| **Static Web Apps (Free)** | **$0** | 100GB bandwidth, 2 custom domains, free SSL |
| Static Web Apps (Standard) | ~$9/month | Only if advanced features needed |

**Estimated savings: $60-180/year**

#### ACR Tier Comparison (Reference)

| Tier | Monthly Cost | Included Storage | Key Features |
|------|-------------|------------------|--------------|
| **Basic (current)** | ~$5/month | 10 GB | Dev/test, 2 webhooks |
| **Standard** | ~$20/month | 100 GB | Production, 10 webhooks |
| **Premium** | ~$50/month | 500 GB | Geo-replication, private endpoints, VNet |

**Recommendation:** Stay on Basic tier. Demo has 2 small images (~50MB each), well under 10GB limit.

---

### Migration Scope

#### What Changes
- Frontend deployment: Container Apps → Static Web Apps
- GitHub Actions workflow: Docker build → static build + SWA deploy
- Infrastructure: Remove `frontend.bicep`, add `staticwebapp.bicep`
- Config: Remove `docker-entrypoint.sh`, add `staticwebapp.config.json`

#### What Stays the Same
- Backend on Container Apps (unchanged)
- ACR (still needed for backend)
- React app code (minimal changes to API client)
- Azure AD authentication

---

### Implementation Steps

#### PR36: Static Web Apps Configuration ✅ COMPLETE

**Priority**: HIGH
**Estimated Effort**: 30 minutes
**PR**: https://github.com/willkmacdonald/azure-factory-demo/pull/4

**Tasks**:
- [x] Create `frontend/staticwebapp.config.json` with SPA routing and security headers
- [x] Update `frontend/src/api/client.ts` to use build-time env only (remove window.ENV)
- [x] Test local build succeeds

**staticwebapp.config.json**:
```json
{
  "navigationFallback": {
    "rewrite": "/index.html",
    "exclude": ["/assets/*", "/config/*"]
  },
  "globalHeaders": {
    "X-Frame-Options": "SAMEORIGIN",
    "X-Content-Type-Options": "nosniff",
    "X-XSS-Protection": "1; mode=block",
    "Referrer-Policy": "strict-origin-when-cross-origin"
  }
}
```

---

#### PR37: Infrastructure Updates ✅ COMPLETE

**Priority**: HIGH
**Estimated Effort**: 30 minutes
**PR**: https://github.com/willkmacdonald/azure-factory-demo/pull/6

**Tasks**:
- [x] Create `infra/staticwebapp.bicep` (Free tier SWA resource)
- [x] Update `infra/backend.bicep` CORS to include SWA domain
- [x] Test Bicep template validates

**Key Bicep Parameters**:
- SKU: Free
- Location: Same region as backend (eastus)
- Build configuration for React/Vite

---

#### PR38: GitHub Actions Update ✅ COMPLETE

**Priority**: HIGH
**Estimated Effort**: 30 minutes
**PR**: https://github.com/willkmacdonald/azure-factory-demo/pull/7

**Tasks**:
- [x] Replace `.github/workflows/deploy-frontend.yml` with SWA deployment
- [x] Add `AZURE_STATIC_WEB_APPS_API_TOKEN` secret
- [x] Set `VITE_API_BASE_URL` at build time from secrets
- [x] Test deployment succeeds

**New Workflow Structure**:
1. Checkout code
2. Setup Node 22
3. Install dependencies (`npm ci`)
4. Build with backend URL (`VITE_API_BASE_URL`)
5. Deploy using `Azure/static-web-apps-deploy@v1`

---

#### PR39: Cleanup ✅ COMPLETE

**Priority**: LOW
**Estimated Effort**: 15 minutes
**PR**: https://github.com/willkmacdonald/azure-factory-demo/pull/8

**Tasks**:
- [x] Delete `frontend/Dockerfile`
- [x] Delete `frontend/docker-entrypoint.sh`
- [x] Delete `frontend/nginx.conf`
- [x] Delete `infra/frontend.bicep`
- [x] Update README.md with new architecture
- [x] Update `.claude/CLAUDE.md` tech stack section

---

### Files to Modify

| File | Action | Description |
|------|--------|-------------|
| `frontend/staticwebapp.config.json` | Create | SPA routing, security headers |
| `frontend/src/api/client.ts` | Edit | Remove window.ENV, use build-time only |
| `infra/staticwebapp.bicep` | Create | Static Web Apps infrastructure |
| `infra/backend.bicep` | Edit | Add SWA domain to CORS |
| `.github/workflows/deploy-frontend.yml` | Replace | New SWA deployment workflow |
| `frontend/Dockerfile` | Delete | No longer needed |
| `frontend/docker-entrypoint.sh` | Delete | No longer needed |
| `frontend/nginx.conf` | Delete | No longer needed |
| `infra/frontend.bicep` | Delete | No longer needed |

---

### Verification Steps

1. **Local build test:** `cd frontend && npm run build` succeeds
2. **Deploy to SWA:** GitHub Action completes successfully
3. **SPA routing:** Navigate to `/machines`, `/chat` directly - should work
4. **API connectivity:** Dashboard loads data from backend
5. **Security headers:** Check response headers in browser DevTools
6. **CORS:** No CORS errors in console
7. **Auth:** Azure AD login still works

---

### Rollback Plan

If issues arise:
1. Re-enable old `deploy-frontend.yml` from git history
2. Redeploy frontend Container App using `frontend.bicep`
3. Delete Static Web Apps resource

---

### Dependencies

- Backend must remain on Container Apps (needs Python runtime)
- ACR still required for backend container images
- Azure AD app registration unchanged

---

## Previous Phases (Archived)

See `docs/archive/implementation-plan-phase6-complete.md` for:
- Phase 1-4: Core application development
- Phase 5: Memory system implementation
- Phase 6: Tailwind CSS migration
- Security hardening (PR24A-D)

---

## Reference

- [Azure Static Web Apps Documentation](https://learn.microsoft.com/en-us/azure/static-web-apps/)
- [Azure Container Registry Pricing](https://azure.microsoft.com/en-us/pricing/details/container-registry/)
- [ACR SKU Features](https://learn.microsoft.com/en-us/azure/container-registry/container-registry-skus)
