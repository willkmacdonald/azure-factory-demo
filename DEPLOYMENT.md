# Factory Agent - Deployment Guide

This guide covers deploying the Factory Agent backend API to Azure Container Apps.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Architecture](#architecture)
- [Local Development](#local-development)
- [Azure Deployment](#azure-deployment)
- [CI/CD Pipeline](#cicd-pipeline)
- [Configuration](#configuration)
- [Monitoring](#monitoring)
- [Troubleshooting](#troubleshooting)

---

## Overview

Factory Agent uses a modern cloud-native architecture:

- **Backend**: FastAPI + Uvicorn (Python 3.11)
- **Container Platform**: Azure Container Apps (consumption plan)
- **Container Registry**: Azure Container Registry (ACR)
- **Monitoring**: Azure Log Analytics + Application Insights
- **Storage**: Azure Blob Storage (production) or local JSON (development)
- **CI/CD**: GitHub Actions

### Key Features

- **Auto-scaling**: Scales to zero when idle (cost savings)
- **Zero-downtime deployments**: Rolling updates with health checks
- **Secure secrets management**: Azure Key Vault integration
- **Automated CI/CD**: Push to main → automatic deployment
- **Multi-environment support**: dev, staging, prod

---

## Prerequisites

### Required Tools

1. **Azure CLI** (2.50.0 or later)
   ```bash
   # Install
   brew install azure-cli  # macOS
   # Or download from https://docs.microsoft.com/cli/azure/install-azure-cli

   # Login
   az login

   # Verify
   az --version
   ```

2. **Docker** (20.10 or later)
   ```bash
   # Install Docker Desktop
   # macOS: https://docs.docker.com/desktop/install/mac-install/
   # Windows: https://docs.docker.com/desktop/install/windows-install/

   # Verify
   docker --version
   docker info
   ```

3. **Git** (for CI/CD)
   ```bash
   git --version
   ```

### Azure Resources

You'll need:

- **Azure Subscription** with Contributor access
- **Azure OpenAI Service** deployed with a GPT-4 or GPT-3.5-turbo model
- **Azure Storage Account** with a blob container (for production mode)

### Required Credentials

Collect these values before deployment:

```bash
# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://<your-resource>.openai.azure.com/
AZURE_OPENAI_KEY=<your-key>
AZURE_OPENAI_DEPLOYMENT=gpt-4  # Your model deployment name
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Azure Storage (production only)
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=...
AZURE_STORAGE_CONTAINER_NAME=factory-data
```

---

## Architecture

### Azure Resources Created

```
factory-agent-dev-rg (Resource Group)
├── factory-agent-dev-env (Container Apps Environment)
│   └── factory-agent-dev-backend (Container App)
├── factoryagentdevacr (Container Registry)
├── factory-agent-dev-logs (Log Analytics Workspace)
└── factory-agent-dev-identity (Managed Identity)
```

### Container Configuration

- **Image**: Multi-stage Docker build (Python 3.11-slim)
- **Port**: 8000 (HTTP)
- **Health check**: `/health` endpoint
- **Scaling**: 0-5 instances (configurable)
- **Resources**: 0.5 CPU, 1GB RAM (configurable)

### Network Flow

```
Internet → Azure Container Apps Ingress (HTTPS)
         → Container App (HTTP on :8000)
         → FastAPI + Uvicorn
         → Azure OpenAI API
         → Azure Blob Storage (optional)
```

---

## Local Development

### Option 1: Docker Compose (Recommended)

```bash
# 1. Copy environment template
cp .env.example .env

# 2. Edit .env with your credentials
vim .env

# 3. Start services
docker-compose up --build

# 4. Access API
open http://localhost:8000/docs
```

### Option 2: Local Build Script

```bash
# Build and run locally
./scripts/build-local.sh

# Access API
open http://localhost:8000/docs
```

### Option 3: Python Virtual Environment

```bash
# 1. Create virtual environment
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set environment variables
export AZURE_OPENAI_ENDPOINT="https://..."
export AZURE_OPENAI_KEY="..."
export DEBUG=true
export STORAGE_MODE=local

# 4. Run FastAPI
python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Testing Local Deployment

```bash
# Health check
curl http://localhost:8000/health

# API documentation
open http://localhost:8000/docs

# Test metrics endpoint
curl http://localhost:8000/api/metrics/oee

# View logs
docker logs -f factory-agent-backend-local
```

---

## Azure Deployment

### Method 1: Automated Deployment Script (Recommended)

The deployment script automates the entire deployment process.

```bash
# 1. Set environment variables
export AZURE_OPENAI_ENDPOINT="https://..."
export AZURE_OPENAI_KEY="..."
export AZURE_STORAGE_CONNECTION_STRING="..."

# Or load from .env file
set -a; source .env; set +a

# 2. Run deployment script
./scripts/deploy.sh dev

# For production
./scripts/deploy.sh prod
```

**What the script does:**

1. ✅ Validates prerequisites (Azure CLI, Docker)
2. ✅ Creates resource group
3. ✅ Builds Docker image
4. ✅ Creates Azure Container Registry
5. ✅ Pushes image to ACR
6. ✅ Deploys infrastructure with Bicep
7. ✅ Runs health checks
8. ✅ Displays deployment URL

### Method 2: Manual Deployment Steps

If you prefer manual control:

#### Step 1: Create Resource Group

```bash
RESOURCE_GROUP="factory-agent-dev-rg"
LOCATION="eastus"

az group create \
  --name $RESOURCE_GROUP \
  --location $LOCATION
```

#### Step 2: Build Docker Image

```bash
cd backend

docker build \
  --tag factory-agent/backend:latest \
  --file Dockerfile \
  .

cd ..
```

#### Step 3: Create Container Registry

```bash
ACR_NAME="factoryagentdevacr"  # Must be globally unique

az acr create \
  --name $ACR_NAME \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --sku Basic \
  --admin-enabled false
```

#### Step 4: Push Image to ACR

```bash
# Login to ACR
az acr login --name $ACR_NAME

# Tag image for ACR
docker tag factory-agent/backend:latest \
  $ACR_NAME.azurecr.io/factory-agent/backend:latest

# Push to ACR
docker push $ACR_NAME.azurecr.io/factory-agent/backend:latest
```

#### Step 5: Deploy Infrastructure with Bicep

```bash
az deployment group create \
  --name factory-agent-deployment \
  --resource-group $RESOURCE_GROUP \
  --template-file infra/main.bicep \
  --parameters \
    appName=factory-agent \
    environmentName=dev \
    imageTag=latest \
    azureOpenAiEndpoint="$AZURE_OPENAI_ENDPOINT" \
    azureOpenAiKey="$AZURE_OPENAI_KEY" \
    azureStorageConnectionString="$AZURE_STORAGE_CONNECTION_STRING"
```

#### Step 6: Get Deployment URL

```bash
BACKEND_URL=$(az deployment group show \
  --name factory-agent-deployment \
  --resource-group $RESOURCE_GROUP \
  --query properties.outputs.backendUrl.value \
  -o tsv)

echo "Backend API: $BACKEND_URL"
```

#### Step 7: Test Deployment

```bash
# Health check
curl $BACKEND_URL/health

# Open API docs
open $BACKEND_URL/docs
```

---

## CI/CD Pipeline

### GitHub Actions Setup

The repository includes a GitHub Actions workflow for automated deployments.

#### Step 1: Create Azure Service Principal

```bash
# Get your subscription ID
SUBSCRIPTION_ID=$(az account show --query id -o tsv)

# Create service principal with contributor role
az ad sp create-for-rbac \
  --name "factory-agent-github" \
  --role contributor \
  --scopes /subscriptions/$SUBSCRIPTION_ID/resourceGroups/factory-agent-dev-rg \
  --sdk-auth
```

**Copy the entire JSON output** (you'll need it in the next step).

#### Step 2: Configure GitHub Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions

Add these secrets:

| Secret Name | Value | Source |
|------------|-------|--------|
| `AZURE_CREDENTIALS` | Full JSON from service principal | Step 1 output |
| `AZURE_SUBSCRIPTION_ID` | Your subscription ID | `az account show --query id -o tsv` |
| `AZURE_RESOURCE_GROUP` | `factory-agent-dev-rg` | Resource group name |
| `AZURE_OPENAI_ENDPOINT` | `https://...openai.azure.com/` | Azure OpenAI resource |
| `AZURE_OPENAI_KEY` | `...` | Azure OpenAI key |
| `AZURE_STORAGE_CONNECTION_STRING` | `DefaultEndpointsProtocol=https;...` | Storage account |

#### Step 3: Trigger Deployment

**Automatic trigger:**
```bash
git add .
git commit -m "feat: add new feature"
git push origin main
```

**Manual trigger:**
1. Go to GitHub → Actions tab
2. Select "Deploy Backend to Azure Container Apps"
3. Click "Run workflow"
4. Choose environment (dev/staging/prod)
5. Click "Run workflow"

#### Step 4: Monitor Deployment

- View progress in GitHub Actions tab
- Check deployment summary after completion
- Click URLs to verify deployment

---

## Configuration

### Environment Variables

The application supports these environment variables:

#### Required

| Variable | Description | Example |
|----------|-------------|---------|
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI resource endpoint | `https://my-resource.openai.azure.com/` |
| `AZURE_OPENAI_KEY` | Azure OpenAI API key | `abc123...` |
| `AZURE_OPENAI_DEPLOYMENT` | Model deployment name | `gpt-4` |

#### Optional

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG` | Enable debug mode | `false` |
| `LOG_LEVEL` | Logging level | `info` |
| `STORAGE_MODE` | Storage backend (`local` or `blob`) | `blob` |
| `ALLOWED_ORIGINS` | CORS allowed origins | `*` |
| `AZURE_OPENAI_API_VERSION` | API version | `2024-02-15-preview` |

### Scaling Configuration

Edit `infra/main.bicepparam` to adjust scaling:

```bicep
// Development: Scale to zero
param minReplicas = 0
param maxReplicas = 3

// Production: Always have 1 instance
param minReplicas = 1
param maxReplicas = 10
```

### Resource Allocation

Adjust CPU and memory in `infra/main.bicepparam`:

```bicep
// Development
param cpuCores = '0.5'
param memorySize = '1.0'

// Production
param cpuCores = '1.0'
param memorySize = '2.0'
```

---

## Monitoring

### View Logs

```bash
# Real-time logs (follow)
az containerapp logs show \
  --name factory-agent-dev-backend \
  --resource-group factory-agent-dev-rg \
  --follow

# Recent logs (last 100 lines)
az containerapp logs show \
  --name factory-agent-dev-backend \
  --resource-group factory-agent-dev-rg \
  --tail 100
```

### Log Analytics Queries

Navigate to Azure Portal → Log Analytics Workspace → Logs

**Example queries:**

```kusto
// All container logs (last hour)
ContainerAppConsoleLogs_CL
| where TimeGenerated > ago(1h)
| order by TimeGenerated desc

// Error logs only
ContainerAppConsoleLogs_CL
| where Log_s contains "ERROR"
| order by TimeGenerated desc

// Health check requests
ContainerAppConsoleLogs_CL
| where Log_s contains "/health"
| summarize count() by bin(TimeGenerated, 5m)
```

### Application Insights (Optional)

To enable Application Insights:

1. Create Application Insights resource
2. Add environment variable: `APPLICATIONINSIGHTS_CONNECTION_STRING`
3. Install SDK: `pip install opencensus-ext-azure`
4. Configure in code (see [Azure docs](https://learn.microsoft.com/azure/azure-monitor/app/opencensus-python))

---

## Troubleshooting

### Common Issues

#### 1. Health Check Failing

**Symptoms:**
- Container restarts frequently
- Deployment shows "Unhealthy" status

**Solutions:**
```bash
# Check logs
az containerapp logs show -n factory-agent-dev-backend -g factory-agent-dev-rg --follow

# Verify environment variables
az containerapp show -n factory-agent-dev-backend -g factory-agent-dev-rg \
  --query properties.template.containers[0].env

# Test locally
docker-compose up --build
curl http://localhost:8000/health
```

#### 2. Container Won't Start

**Symptoms:**
- Container crashes immediately
- No logs available

**Solutions:**
```bash
# Check revision provisioning state
az containerapp revision list \
  --name factory-agent-dev-backend \
  --resource-group factory-agent-dev-rg

# Test image locally
docker run -p 8000:8000 \
  -e AZURE_OPENAI_ENDPOINT="..." \
  -e AZURE_OPENAI_KEY="..." \
  factoryagentdevacr.azurecr.io/factory-agent/backend:latest
```

#### 3. Authentication Errors

**Symptoms:**
- "Unauthorized" errors in logs
- Azure OpenAI API calls failing

**Solutions:**
```bash
# Verify Azure OpenAI credentials
curl "$AZURE_OPENAI_ENDPOINT/openai/deployments?api-version=2024-02-15-preview" \
  -H "api-key: $AZURE_OPENAI_KEY"

# Update Container App secrets
az containerapp secret set \
  --name factory-agent-dev-backend \
  --resource-group factory-agent-dev-rg \
  --secrets azure-openai-key="$AZURE_OPENAI_KEY"
```

#### 4. Image Pull Errors

**Symptoms:**
- "ImagePullBackOff" error
- Container fails to start

**Solutions:**
```bash
# Verify image exists in ACR
az acr repository show-tags \
  --name factoryagentdevacr \
  --repository factory-agent/backend

# Check managed identity permissions
az role assignment list \
  --scope /subscriptions/.../resourceGroups/factory-agent-dev-rg/providers/Microsoft.ContainerRegistry/registries/factoryagentdevacr
```

### Debug Techniques

#### Enable Verbose Logging

```bash
az containerapp update \
  --name factory-agent-dev-backend \
  --resource-group factory-agent-dev-rg \
  --set-env-vars DEBUG=true LOG_LEVEL=debug
```

#### Execute Shell in Container

```bash
az containerapp exec \
  --name factory-agent-dev-backend \
  --resource-group factory-agent-dev-rg \
  --command /bin/bash
```

#### Check Resource Utilization

```bash
az monitor metrics list \
  --resource /subscriptions/.../resourceGroups/factory-agent-dev-rg/providers/Microsoft.App/containerApps/factory-agent-dev-backend \
  --metric "UsageNanoCores,WorkingSetBytes"
```

### Getting Help

1. **Check logs first**: `az containerapp logs show --follow`
2. **Review Azure Portal**: Container Apps → Monitoring → Log stream
3. **Test locally**: `docker-compose up --build`
4. **Validate Bicep**: `az deployment group validate ...`
5. **Open GitHub issue**: Include logs and error messages

---

## Cost Optimization

### Development Environment

- **Scale to zero**: `minReplicas = 0` (no cost when idle)
- **Small resources**: 0.5 CPU, 1GB RAM
- **Basic ACR**: $5/month
- **Log retention**: 30 days

**Estimated monthly cost:** $10-20 (mostly idle)

### Production Environment

- **Always-on**: `minReplicas = 1` (better performance)
- **Larger resources**: 1.0 CPU, 2GB RAM
- **Standard ACR**: $20/month (recommended)
- **Application Insights**: $2.30/GB

**Estimated monthly cost:** $50-100 (depends on traffic)

### Cost Reduction Tips

1. Use consumption plan (not dedicated)
2. Scale to zero in development
3. Use 30-day log retention
4. Clean up old container images
5. Use resource tags for cost tracking

---

## Security Best Practices

1. **Never commit secrets** to Git (use `.gitignore`)
2. **Use Managed Identity** for Azure service access
3. **Restrict CORS origins** in production
4. **Enable Container Apps authentication** for public APIs
5. **Use Azure Key Vault** for secrets (optional enhancement)
6. **Regular security updates**: Rebuild images monthly
7. **Network policies**: Consider private endpoints for production

---

## Next Steps

- [ ] Set up Application Insights for better monitoring
- [ ] Configure custom domain with Azure DNS
- [ ] Add Azure Front Door for global distribution
- [ ] Implement rate limiting per user
- [ ] Set up staging environment
- [ ] Configure Azure Key Vault for secrets
- [ ] Add automated backups for blob storage

---

## References

- [Azure Container Apps Docs](https://learn.microsoft.com/azure/container-apps/)
- [FastAPI Deployment Guide](https://fastapi.tiangolo.com/deployment/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Bicep Documentation](https://learn.microsoft.com/azure/azure-resource-manager/bicep/)
- [GitHub Actions for Azure](https://github.com/Azure/actions)
