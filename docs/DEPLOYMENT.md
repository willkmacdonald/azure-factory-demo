# Azure Container Apps Deployment Guide

This guide explains how to deploy the Factory Agent application (frontend + backend) to Azure Container Apps using the automated CI/CD pipeline.

## Overview

Factory Agent uses a **multi-container architecture** with:
- **Backend**: FastAPI application (Python) running on Uvicorn
- **Frontend**: React application (TypeScript + Vite) served by Nginx

Both containers are deployed to **Azure Container Apps** with:
- Automatic scaling (scale-to-zero for cost savings)
- HTTPS termination
- Health checks
- Runtime environment configuration

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Azure Container Apps                    │
│                                                               │
│  ┌──────────────────┐         ┌──────────────────┐          │
│  │  Frontend App    │         │  Backend App     │          │
│  │  (React + Nginx) │────────▶│  (FastAPI)       │          │
│  │  Port: 80        │  API    │  Port: 8000      │          │
│  └──────────────────┘         └──────────────────┘          │
│                                                               │
│  ┌──────────────────────────────────────────────┐           │
│  │  Shared Container Apps Environment           │           │
│  │  - Log Analytics                              │           │
│  │  - Managed Identity                           │           │
│  │  - Auto-scaling (0-5 replicas)                │           │
│  └──────────────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────────┘
         │                              │
         ▼                              ▼
┌─────────────────┐           ┌─────────────────┐
│  Azure Container│           │  Azure Blob     │
│  Registry       │           │  Storage        │
│  (Images)       │           │  (Data)         │
└─────────────────┘           └─────────────────┘
```

---

## Prerequisites

### Azure Resources

1. **Azure Subscription** with permissions to create:
   - Resource Groups
   - Container Apps
   - Container Registry
   - Storage Accounts
   - Log Analytics Workspaces

2. **Azure OpenAI Service** deployment (for AI chat feature)

3. **Azure Storage Account** (for production data persistence)

### GitHub Configuration

Required GitHub Secrets (configured in: Settings > Secrets > Actions):

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `AZURE_CREDENTIALS` | Service Principal JSON | `{"clientId": "...", "clientSecret": "...", ...}` |
| `AZURE_SUBSCRIPTION_ID` | Azure Subscription ID | `12345678-1234-1234-1234-123456789012` |
| `AZURE_RESOURCE_GROUP` | Resource Group name | `factory-agent-dev-rg` |
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI endpoint URL | `https://my-openai.openai.azure.com/` |
| `AZURE_OPENAI_KEY` | Azure OpenAI API key | `abc123...` |
| `AZURE_STORAGE_CONNECTION_STRING` | Azure Storage connection string | `DefaultEndpointsProtocol=https;AccountName=...` |

### Creating the Service Principal

```bash
# Create Service Principal with Contributor role on resource group
az ad sp create-for-rbac \
  --name "factory-agent-github-actions" \
  --role contributor \
  --scopes /subscriptions/{subscription-id}/resourceGroups/{rg-name} \
  --sdk-auth

# Copy the JSON output and add as AZURE_CREDENTIALS secret in GitHub
```

---

## Deployment Workflows

### Backend Deployment

**Workflow File**: `.github/workflows/deploy-backend.yml`

**Triggers**:
- Push to `main` branch (paths: `backend/**`, `shared/**`, `infra/**`)
- Manual workflow dispatch

**Pipeline Stages**:
1. **Build**: Build Docker image from `backend/Dockerfile`
2. **Push**: Push image to Azure Container Registry
3. **Deploy**: Deploy to Azure Container Apps using Bicep template
4. **Test**: Health check and API validation

**Run Backend Deployment**:
```bash
# Automatic: Push changes to backend/shared/infra
git push origin main

# Manual: Via GitHub UI
# Actions > Deploy Backend to Azure Container Apps > Run workflow
```

### Frontend Deployment

**Workflow File**: `.github/workflows/deploy-frontend.yml`

**Triggers**:
- Push to `main` branch (paths: `frontend/**`, `infra/**`)
- Manual workflow dispatch

**Pipeline Stages**:
1. **Build**: Build Docker image from `frontend/Dockerfile` (multi-stage: Node + Nginx)
2. **Push**: Push image to Azure Container Registry
3. **Deploy**: Deploy to Azure Container Apps using Bicep template
4. **Test**: Health check and connectivity validation

**Run Frontend Deployment**:
```bash
# Automatic: Push changes to frontend/infra
git push origin main

# Manual: Via GitHub UI
# Actions > Deploy Frontend to Azure Container Apps > Run workflow
```

---

## Infrastructure as Code (Bicep)

### Main Template

**File**: `infra/main.bicep`

**Resources Created**:
- Container Apps Environment (shared)
- Container Registry (Standard tier)
- Log Analytics Workspace (30-day retention)
- Managed Identity (for ACR pull)
- Backend Container App (FastAPI)
- Frontend Container App (React + Nginx)

**Deployment**:
```bash
# Deploy infrastructure manually (optional - CI/CD does this automatically)
az deployment group create \
  --resource-group factory-agent-dev-rg \
  --template-file infra/main.bicep \
  --parameters \
    containerRegistryName=factoryagent4u4zqkacr \
    imageTag=latest \
    azureOpenAiEndpoint=$AZURE_OPENAI_ENDPOINT \
    azureOpenAiKey=$AZURE_OPENAI_KEY \
    azureStorageConnectionString=$AZURE_STORAGE_CONNECTION_STRING \
    environmentName=dev
```

---

## Docker Images

### Backend Dockerfile

**File**: `backend/Dockerfile`

**Multi-Stage Build**:
1. **Builder Stage**: Python 3.11, install dependencies
2. **Runtime Stage**: Python 3.11-slim, copy app + dependencies

**Image Size**: ~150MB (optimized)

**Build Locally**:
```bash
# Build from project root
docker build -f backend/Dockerfile -t factory-agent/backend .

# Run locally
docker run -p 8000:8000 \
  -e AZURE_OPENAI_ENDPOINT=$AZURE_OPENAI_ENDPOINT \
  -e AZURE_OPENAI_KEY=$AZURE_OPENAI_KEY \
  factory-agent/backend
```

### Frontend Dockerfile

**File**: `frontend/Dockerfile`

**Multi-Stage Build**:
1. **Builder Stage**: Node 22 Alpine, npm install + build
2. **Runtime Stage**: Nginx 1.27 Alpine, serve static files

**Image Size**: ~25MB (highly optimized)

**Runtime Configuration**:
- Environment variables injected at container startup (not build time)
- `docker-entrypoint.sh` generates `/config/env.js` with runtime config
- React app reads config from `window.ENV`

**Build Locally**:
```bash
# Build from project root
docker build -f frontend/Dockerfile -t factory-agent/frontend .

# Run locally
docker run -p 3000:80 \
  -e VITE_API_BASE_URL=http://localhost:8000 \
  factory-agent/frontend

# Test in browser: http://localhost:3000
```

---

## Environment Variables

### Backend Environment Variables

Set in Azure Container Apps configuration (via Bicep):

| Variable | Description | Example |
|----------|-------------|---------|
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI endpoint URL | `https://my-openai.openai.azure.com/` |
| `AZURE_OPENAI_KEY` | Azure OpenAI API key (secret) | `abc123...` |
| `AZURE_OPENAI_DEPLOYMENT` | Model deployment name | `gpt-4` |
| `AZURE_OPENAI_API_VERSION` | API version | `2024-02-15-preview` |
| `STORAGE_MODE` | Storage mode (`local` or `blob`) | `blob` |
| `AZURE_STORAGE_CONNECTION_STRING` | Blob storage connection (secret) | `DefaultEndpointsProtocol=...` |
| `AZURE_STORAGE_CONTAINER_NAME` | Blob container name | `factory-data` |
| `DEBUG` | Debug mode | `false` (prod), `true` (dev) |
| `LOG_LEVEL` | Logging level | `info` (prod), `debug` (dev) |

### Frontend Environment Variables

Set in Azure Container Apps configuration (via Bicep):

| Variable | Description | Example |
|----------|-------------|---------|
| `VITE_API_BASE_URL` | Backend API URL (auto-configured) | `https://factory-agent-dev-backend.xxx.azurecontainerapps.io` |
| `NODE_ENV` | Node environment | `production` |
| `APP_VERSION` | Application version (image tag) | `abc123` (commit SHA) |

**Important**: Frontend environment variables are injected at **runtime** (not build time) using `docker-entrypoint.sh`. This allows deploying the same Docker image to different environments without rebuilding.

---

## Runtime Environment Configuration (Frontend)

### How It Works

1. **Build Time**: React app is built with placeholder for runtime config
2. **Container Startup**: `docker-entrypoint.sh` generates `/config/env.js`:
   ```javascript
   window.ENV = {
     API_BASE_URL: 'https://factory-agent-dev-backend.xxx.azurecontainerapps.io',
     NODE_ENV: 'production',
     VERSION: 'abc123',
   };
   ```
3. **Runtime**: React app reads config from `window.ENV.API_BASE_URL`

### API Client Configuration

**File**: `frontend/src/api/client.ts`

```typescript
// Runtime config (from docker-entrypoint.sh)
const API_BASE_URL = window.ENV?.API_BASE_URL
  || import.meta.env.VITE_API_BASE_URL  // Build-time fallback
  || 'http://localhost:8000';            // Development fallback
```

**Benefits**:
- Single Docker image works in dev/staging/prod
- No rebuild needed to change backend URL
- Configuration visible in browser console
- Easier debugging and troubleshooting

---

## CORS Configuration

### Backend CORS Policy

Configured in `infra/main.bicep`:

```bicep
corsPolicy: {
  allowedOrigins: allowedOrigins != '' ? split(allowedOrigins, ',') : ['*']
  allowedMethods: ['GET', 'POST', 'OPTIONS']
  allowedHeaders: ['*']
  allowCredentials: true
}
```

**Default**: Allows all origins (`*`) for development

**Production**: Set `allowedOrigins` parameter to specific frontend URL:
```bash
--parameters allowedOrigins=https://factory-agent-dev-frontend.xxx.azurecontainerapps.io
```

---

## Scaling Configuration

### Auto-Scaling Settings

Configured in `infra/main.bicep`:

```bicep
scale: {
  minReplicas: 0     // Scale to zero when idle (cost savings)
  maxReplicas: 5     // Maximum 5 instances under load
  rules: [
    {
      name: 'http-scaling-rule'
      http: {
        metadata: {
          concurrentRequests: '10'  // Backend: 10 concurrent requests
          concurrentRequests: '20'  // Frontend: 20 concurrent requests
        }
      }
    }
  ]
}
```

**Scale-to-Zero**: Containers scale down to 0 replicas after 15 minutes of inactivity (Azure default)

**Cold Start**: ~5-10 seconds for container to start from zero

**Cost**: Only pay for active container time (no idle charges)

---

## Health Checks

### Backend Health Check

**Endpoint**: `GET /health`

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-16T12:00:00Z"
}
```

**Probes**:
- **Liveness**: Every 30s (restart if fails 3 times)
- **Readiness**: Every 10s (remove from load balancer if fails 3 times)

### Frontend Health Check

**Endpoint**: `GET /health`

**Response**:
```text
healthy
```

**Probes**:
- **Liveness**: Every 30s (restart if fails 3 times)
- **Readiness**: Every 10s (remove from load balancer if fails 3 times)

---

## Monitoring and Logs

### View Container Logs

```bash
# Backend logs
az containerapp logs show \
  --name factory-agent-dev-backend \
  --resource-group factory-agent-dev-rg \
  --follow

# Frontend logs
az containerapp logs show \
  --name factory-agent-dev-frontend \
  --resource-group factory-agent-dev-rg \
  --follow
```

### Log Analytics Queries

**Portal**: Azure Portal > Log Analytics Workspace > Logs

**Example Queries**:

```kusto
// All container logs from last hour
ContainerAppConsoleLogs_CL
| where TimeGenerated > ago(1h)
| order by TimeGenerated desc

// Error logs only
ContainerAppConsoleLogs_CL
| where Log_s contains "ERROR" or Log_s contains "Exception"
| order by TimeGenerated desc

// Frontend API calls
ContainerAppConsoleLogs_CL
| where ContainerAppName_s == "factory-agent-dev-frontend"
| where Log_s contains "API Client Configuration"
| order by TimeGenerated desc
```

---

## Troubleshooting

### Common Issues

#### 1. Frontend Cannot Connect to Backend

**Symptoms**:
- Frontend loads but shows "Network Error"
- API calls fail with CORS errors

**Solutions**:
```bash
# Check frontend environment config
az containerapp show \
  --name factory-agent-dev-frontend \
  --resource-group factory-agent-dev-rg \
  --query properties.template.containers[0].env

# Verify backend URL is correct
curl https://factory-agent-dev-backend.xxx.azurecontainerapps.io/health

# Check CORS configuration
az containerapp show \
  --name factory-agent-dev-backend \
  --resource-group factory-agent-dev-rg \
  --query properties.configuration.ingress.corsPolicy
```

#### 2. Container Won't Start

**Symptoms**:
- Container app shows "Failed" or "Provisioning Failed"

**Solutions**:
```bash
# Check container logs
az containerapp logs show \
  --name factory-agent-dev-backend \
  --resource-group factory-agent-dev-rg \
  --tail 100

# Check for image pull errors
az containerapp revision list \
  --name factory-agent-dev-backend \
  --resource-group factory-agent-dev-rg \
  --query "[0].properties.provisioningState"

# Verify image exists in ACR
az acr repository show-tags \
  --name factoryagent4u4zqkacr \
  --repository factory-agent/backend
```

#### 3. Deployment Fails in GitHub Actions

**Symptoms**:
- GitHub Actions workflow fails during deployment step

**Solutions**:
1. **Check GitHub Secrets**: Ensure all required secrets are configured
2. **Check Service Principal**: Verify Service Principal has Contributor role
3. **Check Bicep Template**: Validate template locally:
   ```bash
   az deployment group validate \
     --resource-group factory-agent-dev-rg \
     --template-file infra/main.bicep \
     --parameters containerRegistryName=factoryagent4u4zqkacr imageTag=test
   ```
4. **Check ACR Access**: Ensure Service Principal can push to ACR:
   ```bash
   az acr check-health --name factoryagent4u4zqkacr
   ```

#### 4. TypeScript Build Errors

**Symptoms**:
- Frontend Docker build fails with TypeScript errors
- Errors related to MUI Grid `item` prop

**Solutions**:
This is a known issue with MUI v7 Grid API changes. See "Known Issues" section below.

---

## Known Issues

### Frontend TypeScript Errors (MUI Grid v7)

**Issue**: Frontend build fails with TypeScript errors related to Material-UI Grid `item` prop.

**Root Cause**: Material-UI v7 deprecated the `item` prop in favor of a new Grid API.

**Status**: Tracked in implementation plan (PR20B)

**Workaround**: Frontend works in development mode with Vite (which doesn't enforce TypeScript errors). Production deployment requires fixing these errors first.

**Fix Required**: Update all Grid components to use MUI v7 API:
```typescript
// Old (v6)
<Grid container spacing={2}>
  <Grid item xs={12} sm={6}>...</Grid>
</Grid>

// New (v7)
<Grid container spacing={2}>
  <Grid size={{ xs: 12, sm: 6 }}>...</Grid>
</Grid>
```

**Files Affected**:
- `frontend/src/pages/DashboardPage.tsx`
- `frontend/src/pages/MachinesPage.tsx`
- `frontend/src/pages/AlertsPage.tsx`
- `frontend/src/pages/TraceabilityPage.tsx`
- `frontend/src/pages/ChatPage.tsx`

---

## Cost Optimization

### Azure Container Apps Pricing

**Consumption Plan** (current configuration):
- **Active Time**: $0.000012/vCPU-second + $0.000001/GB-second
- **Idle Time**: FREE (with scale-to-zero)
- **Requests**: FREE (no request charges)

**Estimated Monthly Cost** (low traffic demo):
- Backend: ~$5-10/month (0.5 vCPU, 1GB RAM, 10% uptime)
- Frontend: ~$2-5/month (0.25 vCPU, 0.5GB RAM, 5% uptime)
- **Total**: ~$7-15/month

**Cost Savings Tips**:
1. **Scale to Zero**: Already enabled (minReplicas: 0)
2. **Right-Size Resources**: Frontend uses minimal resources (0.25 vCPU)
3. **Use Blob Storage**: Cheaper than persistent volumes
4. **Log Retention**: 30 days (vs 90 days default)

---

## Security Best Practices

### Current Implementation

✅ **Secrets Management**: All secrets stored as Container App secrets (not env vars)
✅ **HTTPS**: Automatic HTTPS with Azure-managed certificates
✅ **Managed Identity**: ACR pull uses Managed Identity (no credentials)
✅ **Non-Root Containers**: Both images run as non-root users
✅ **Minimal Images**: Alpine-based images (reduced attack surface)
✅ **Health Checks**: Automatic restart on failure
✅ **CORS Policy**: Configurable CORS (default: wildcard for dev)

### Production Hardening (Recommended)

⚠️ **CORS**: Restrict to specific frontend origin
⚠️ **Rate Limiting**: Currently implemented in app code (not enforced at ingress)
⚠️ **Container Scanning**: Add image scanning to CI/CD
⚠️ **Firewall**: Add Azure Firewall for network-level protection
⚠️ **Authentication**: Add Azure AD authentication (currently public)

---

## Next Steps

### Deployment Checklist

- [ ] Fix frontend TypeScript errors (MUI Grid v7)
- [ ] Update Bicep parameter files with actual values
- [ ] Configure GitHub Secrets
- [ ] Run backend deployment workflow
- [ ] Run frontend deployment workflow
- [ ] Verify end-to-end connectivity
- [ ] Configure production CORS policy
- [ ] Set up monitoring alerts
- [ ] Document deployed URLs

### Future Enhancements

- [ ] Add Azure AD authentication (MSAL)
- [ ] Implement CDN for frontend static assets
- [ ] Add container image scanning (Trivy, Snyk)
- [ ] Configure custom domain with SSL
- [ ] Add Azure Application Insights for APM
- [ ] Implement blue-green deployments
- [ ] Add automated E2E tests in CI/CD

---

## Additional Resources

- [Azure Container Apps Documentation](https://learn.microsoft.com/en-us/azure/container-apps/)
- [Bicep Documentation](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/)
- [GitHub Actions for Azure](https://github.com/Azure/actions)
- [Docker Multi-Stage Builds](https://docs.docker.com/build/building/multi-stage/)
- [React Environment Variables at Runtime](https://www.mykolaaleksandrov.dev/posts/2025/10/vite-docker-react-environment-variables/)
