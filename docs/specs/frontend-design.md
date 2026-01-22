# Frontend Architecture Design: Azure Static Web Apps Migration

**Created**: 2026-01-21
**Status**: In Progress (PR36 complete, PR37-39 pending)
**Author**: Claude Code

---

## Executive Summary

This document describes the architecture for migrating the Factory Agent React frontend from Azure Container Apps to Azure Static Web Apps. The migration reduces hosting costs to $0/month while maintaining the same functionality, security posture, and user experience.

---

## Current Architecture

### Container Apps Deployment

```
┌─────────────────────────────────────────────────────────────┐
│                    Azure Container Apps                      │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              Frontend Container                        │  │
│  │  ┌─────────────┐    ┌──────────────────────────────┐  │  │
│  │  │   Nginx     │    │    React SPA (dist/)         │  │  │
│  │  │  (port 80)  │───▶│    - index.html              │  │  │
│  │  │             │    │    - assets/                 │  │  │
│  │  │  nginx.conf │    │    - config/env.js (runtime) │  │  │
│  │  └─────────────┘    └──────────────────────────────┘  │  │
│  │         │                                              │  │
│  │         ▼                                              │  │
│  │  docker-entrypoint.sh                                  │  │
│  │  (generates env.js at container start)                 │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼ HTTPS
┌─────────────────────────────────────────────────────────────┐
│                 Backend Container App                        │
│                 (FastAPI + Uvicorn)                          │
└─────────────────────────────────────────────────────────────┘
```

### Current Configuration Flow

1. **Build time**: Vite compiles React app, `VITE_API_BASE_URL` baked into bundle
2. **Container start**: `docker-entrypoint.sh` generates `/config/env.js` with runtime values
3. **Runtime**: React reads `window.ENV.API_BASE_URL` (runtime) or falls back to build-time value
4. **Nginx**: Serves static files, handles SPA routing, adds security headers

### Current Files

| File | Purpose |
|------|---------|
| `frontend/Dockerfile` | Multi-stage build (Node → Nginx) |
| `frontend/docker-entrypoint.sh` | Runtime config injection |
| `frontend/nginx.conf` | SPA routing, security headers, caching |
| `infra/frontend.bicep` | Container Apps deployment |

---

## Proposed Architecture

### Static Web Apps Deployment

```
┌─────────────────────────────────────────────────────────────┐
│                  Azure Static Web Apps                       │
│                      (Free Tier)                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                  Global CDN                            │  │
│  │  ┌──────────────────────────────────────────────────┐ │  │
│  │  │           React SPA (dist/)                       │ │  │
│  │  │           - index.html                            │ │  │
│  │  │           - assets/ (hashed, cached)              │ │  │
│  │  │           - staticwebapp.config.json              │ │  │
│  │  └──────────────────────────────────────────────────┘ │  │
│  │                                                        │  │
│  │  Built-in features:                                    │  │
│  │  - SPA routing (navigationFallback)                   │  │
│  │  - Security headers (globalHeaders)                   │  │
│  │  - HTTPS + custom domains                             │  │
│  │  - CDN caching                                        │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼ HTTPS (CORS)
┌─────────────────────────────────────────────────────────────┐
│                 Backend Container App                        │
│                 (FastAPI + Uvicorn)                          │
│                 (unchanged)                                  │
└─────────────────────────────────────────────────────────────┘
```

### New Configuration Flow

1. **Build time (CI/CD)**: GitHub Actions sets `VITE_API_BASE_URL` environment variable
2. **Vite build**: Compiles React app with backend URL baked into bundle
3. **Deploy**: Static files uploaded directly to SWA (no container)
4. **Runtime**: SWA serves files via global CDN with configured headers

### Key Differences

| Aspect | Container Apps | Static Web Apps |
|--------|---------------|-----------------|
| **Runtime config** | `docker-entrypoint.sh` generates `env.js` | Build-time only |
| **Serving** | Nginx in container | Built-in SWA CDN |
| **SPA routing** | `nginx.conf` try_files | `staticwebapp.config.json` |
| **Security headers** | Nginx add_header | `globalHeaders` in config |
| **Scaling** | 0-5 replicas | Automatic (managed) |
| **Health checks** | Required (`/health`) | Not needed |
| **Cost** | ~$5-15/month | $0 (Free tier) |

---

## Design Decisions

### 1. Build-Time Configuration Only

**Decision**: Remove runtime config injection, use build-time environment variables only.

**Rationale**:
- Static Web Apps cannot run scripts at deploy time
- Build-time config is simpler and more predictable
- Different environments use different GitHub Actions workflows/secrets

**Implementation**:
```typescript
// frontend/src/api/client.ts
// Before (with runtime fallback):
const API_BASE_URL = window.ENV?.API_BASE_URL || import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// After (build-time only):
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
```

**Trade-off**: Cannot change API URL without rebuild. Acceptable for this project since we have separate CI/CD per environment.

---

### 2. SPA Configuration via staticwebapp.config.json

**Decision**: Use SWA's native configuration for routing and headers.

**Rationale**:
- No custom server needed
- Declarative configuration
- Maintained by Azure

**Implementation**:
```json
{
  "navigationFallback": {
    "rewrite": "/index.html",
    "exclude": ["/assets/*"]
  },
  "globalHeaders": {
    "X-Frame-Options": "SAMEORIGIN",
    "X-Content-Type-Options": "nosniff",
    "X-XSS-Protection": "1; mode=block",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self'; connect-src 'self' https://*.azurecontainerapps.io"
  },
  "mimeTypes": {
    ".json": "application/json"
  }
}
```

---

### 3. CORS Configuration

**Decision**: Update backend CORS to allow Static Web Apps domain.

**Current State**: Backend allows `https://*.azurecontainerapps.io`

**Required Change**: Add `https://*.azurestaticapps.net` to allowed origins.

**Implementation** (`infra/backend.bicep`):
```bicep
env: [
  {
    name: 'ALLOWED_ORIGINS'
    value: 'https://${frontendFqdn},https://*.azurestaticapps.net'
  }
]
```

---

### 4. GitHub Actions Deployment

**Decision**: Use `Azure/static-web-apps-deploy@v1` action.

**Workflow Structure**:
```yaml
name: Deploy Frontend (Static Web Apps)

on:
  push:
    branches: [main]
    paths:
      - 'frontend/**'
      - '.github/workflows/deploy-frontend.yml'

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
          VITE_API_BASE_URL: ${{ secrets.BACKEND_URL }}
        run: |
          npm ci
          npm run build

      - name: Deploy to Static Web Apps
        uses: Azure/static-web-apps-deploy@v1
        with:
          azure_static_web_apps_api_token: ${{ secrets.AZURE_STATIC_WEB_APPS_API_TOKEN }}
          repo_token: ${{ secrets.GITHUB_TOKEN }}
          action: 'upload'
          app_location: 'frontend'
          output_location: 'dist'
          skip_app_build: true  # Already built above
```

---

### 5. Infrastructure as Code

**Decision**: Create new `infra/staticwebapp.bicep` template.

**Implementation**:
```bicep
@description('Static Web App name')
param name string = 'factory-agent-frontend'

@description('Location')
param location string = resourceGroup().location

@description('SKU')
@allowed(['Free', 'Standard'])
param sku string = 'Free'

resource staticWebApp 'Microsoft.Web/staticSites@2022-09-01' = {
  name: name
  location: location
  sku: {
    name: sku
    tier: sku
  }
  properties: {
    repositoryUrl: 'https://github.com/your-org/factory-agent'
    branch: 'main'
    buildProperties: {
      appLocation: 'frontend'
      outputLocation: 'dist'
      skipGithubActionWorkflowGeneration: true
    }
  }
}

output defaultHostname string = staticWebApp.properties.defaultHostname
output resourceId string = staticWebApp.id
```

---

## Security Considerations

### Headers Preserved

All security headers from nginx.conf are replicated in staticwebapp.config.json:

| Header | Value | Purpose |
|--------|-------|---------|
| X-Frame-Options | SAMEORIGIN | Prevent clickjacking |
| X-Content-Type-Options | nosniff | Prevent MIME sniffing |
| X-XSS-Protection | 1; mode=block | XSS filtering |
| Referrer-Policy | strict-origin-when-cross-origin | Control referrer info |
| Content-Security-Policy | (see config) | Restrict resource loading |

### HTTPS

- Static Web Apps provides automatic HTTPS
- No configuration required
- Free SSL certificate included

### Authentication

- Azure AD authentication unchanged
- MSAL configuration remains in frontend
- Backend JWT validation unchanged

---

## Performance Considerations

### CDN Benefits

Static Web Apps includes global CDN:
- Lower latency for users worldwide
- Automatic edge caching for static assets
- No cold start delays (unlike Container Apps scale-to-zero)

### Caching Strategy

```json
{
  "routes": [
    {
      "route": "/assets/*",
      "headers": {
        "Cache-Control": "public, max-age=31536000, immutable"
      }
    },
    {
      "route": "/index.html",
      "headers": {
        "Cache-Control": "no-cache"
      }
    }
  ]
}
```

---

## Migration Checklist

### Pre-Migration
- [ ] Verify backend CORS accepts SWA domain
- [ ] Create `AZURE_STATIC_WEB_APPS_API_TOKEN` secret in GitHub
- [ ] Create `BACKEND_URL` secret with backend FQDN

### Migration
- [x] Create `frontend/staticwebapp.config.json` (PR36)
- [x] Update `frontend/src/api/client.ts` (remove window.ENV) (PR36)
- [x] Update `frontend/src/hooks/useChat.ts` (remove window.ENV) (PR36)
- [ ] Create `infra/staticwebapp.bicep` (PR37)
- [ ] Deploy SWA resource via Bicep (PR37)
- [ ] Replace GitHub Actions workflow (PR38)
- [ ] Test deployment (PR38)

### Post-Migration
- [ ] Verify all pages load correctly
- [ ] Verify API calls succeed (no CORS errors)
- [ ] Verify Azure AD login works
- [ ] Delete old Container App frontend resource (PR39)
- [ ] Delete unused files (Dockerfile, nginx.conf, etc.) (PR39)
- [ ] Update documentation (PR39)

### Rollback (if needed)
- [ ] Restore old workflow from git history
- [ ] Redeploy frontend Container App
- [ ] Delete SWA resource

---

## Cost Summary

| Resource | Before | After |
|----------|--------|-------|
| Frontend Container App | ~$5-15/month | $0 (deleted) |
| Static Web Apps (Free) | N/A | $0 |
| Backend Container App | ~$5-15/month | ~$5-15/month (unchanged) |
| ACR (Basic) | ~$5/month | ~$5/month (unchanged) |
| **Total** | **~$15-35/month** | **~$10-20/month** |

**Savings: ~$5-15/month ($60-180/year)**

---

## References

- [Azure Static Web Apps Documentation](https://learn.microsoft.com/en-us/azure/static-web-apps/)
- [SWA Configuration Reference](https://learn.microsoft.com/en-us/azure/static-web-apps/configuration)
- [SWA GitHub Actions](https://learn.microsoft.com/en-us/azure/static-web-apps/github-actions-workflow)
- [Container Registry Pricing](https://azure.microsoft.com/en-us/pricing/details/container-registry/)
