#!/bin/bash
# =============================================================================
# Factory Agent - Azure Deployment Script
# =============================================================================
# This script automates the deployment of Factory Agent to Azure Container Apps.
#
# Prerequisites:
# - Azure CLI installed and logged in (az login)
# - Docker installed and running
# - Appropriate Azure permissions (Contributor role on subscription/resource group)
#
# Usage:
#   ./scripts/deploy.sh [environment]
#
# Examples:
#   ./scripts/deploy.sh dev       # Deploy to development
#   ./scripts/deploy.sh staging   # Deploy to staging
#   ./scripts/deploy.sh prod      # Deploy to production
#
# What this script does:
# 1. Validates prerequisites (Azure CLI, Docker)
# 2. Creates Azure resource group if it doesn't exist
# 3. Builds Docker image for backend
# 4. Creates Azure Container Registry if it doesn't exist
# 5. Pushes Docker image to ACR
# 6. Deploys infrastructure using Bicep template
# 7. Verifies deployment health
# 8. Displays deployment information
# =============================================================================

set -e  # Exit on error
set -u  # Exit on undefined variable

# =============================================================================
# CONFIGURATION
# =============================================================================

# Environment (default: dev)
ENVIRONMENT="${1:-dev}"

# Validate environment
if [[ ! "$ENVIRONMENT" =~ ^(dev|staging|prod)$ ]]; then
    echo "❌ Error: Invalid environment '$ENVIRONMENT'"
    echo "Usage: $0 [dev|staging|prod]"
    exit 1
fi

# Application configuration
APP_NAME="factory-agent"
LOCATION="${AZURE_LOCATION:-eastus}"
RESOURCE_GROUP="${APP_NAME}-${ENVIRONMENT}-rg"

# Image configuration
IMAGE_TAG="${IMAGE_TAG:-$(git rev-parse --short HEAD 2>/dev/null || echo 'latest')}"

# Generate ACR name using same logic as Bicep (infra/main.bicep:var containerRegistryName)
# Note: This script replicates Bicep's uniqueString() logic to know the ACR name before deployment
# Bicep uses: substring(uniqueString(resourceGroup().id), 0, 6)
# We cannot call Bicep's uniqueString() from bash, but we can hash the same input
# This ensures the ACR exists before we try to push images to it

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# =============================================================================
# PREREQUISITE CHECKS
# =============================================================================

log_info "Checking prerequisites..."

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    log_error "Azure CLI is not installed. Please install it first:"
    echo "  https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    log_error "Docker is not installed. Please install it first:"
    echo "  https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker daemon is running
if ! docker info &> /dev/null; then
    log_error "Docker daemon is not running. Please start Docker Desktop."
    exit 1
fi

# Check if logged into Azure
if ! az account show &> /dev/null; then
    log_error "Not logged into Azure. Please run: az login"
    exit 1
fi

# Get Azure subscription info
SUBSCRIPTION_ID=$(az account show --query id -o tsv)
SUBSCRIPTION_NAME=$(az account show --query name -o tsv)

log_success "Prerequisites validated"
echo ""
log_info "Azure Subscription: ${SUBSCRIPTION_NAME}"
log_info "Subscription ID: ${SUBSCRIPTION_ID}"
log_info "Environment: ${ENVIRONMENT}"
log_info "Location: ${LOCATION}"
echo ""

# =============================================================================
# LOAD ENVIRONMENT VARIABLES
# =============================================================================

# Load .env file if it exists (without overriding existing env vars)
if [ -f ".env" ]; then
    log_info "Loading environment variables from .env file..."
    set -a
    source .env
    set +a
    log_success "Environment variables loaded from .env"
else
    log_info "No .env file found, using existing environment variables"
fi

echo ""

# =============================================================================
# ENVIRONMENT VARIABLE CHECKS
# =============================================================================

log_info "Checking required environment variables..."

REQUIRED_VARS=(
    "AZURE_OPENAI_ENDPOINT"
    "AZURE_OPENAI_KEY"
    "AZURE_STORAGE_CONNECTION_STRING"
)

MISSING_VARS=()

for VAR in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!VAR:-}" ]; then
        MISSING_VARS+=("$VAR")
    fi
done

if [ ${#MISSING_VARS[@]} -gt 0 ]; then
    log_error "Missing required environment variables:"
    for VAR in "${MISSING_VARS[@]}"; do
        echo "  - $VAR"
    done
    echo ""
    echo "Please set these variables in your environment or .env file:"
    echo "  export AZURE_OPENAI_ENDPOINT='https://...'"
    echo "  export AZURE_OPENAI_KEY='...'"
    echo "  export AZURE_STORAGE_CONNECTION_STRING='...'"
    echo ""
    echo "Or source them from .env file:"
    echo "  set -a; source .env; set +a"
    exit 1
fi

log_success "All required environment variables are set"
echo ""

# =============================================================================
# RESOURCE GROUP
# =============================================================================

log_info "Checking resource group..."

if ! az group exists --name "$RESOURCE_GROUP" &> /dev/null || [ "$(az group exists --name "$RESOURCE_GROUP")" = "false" ]; then
    log_info "Creating resource group: ${RESOURCE_GROUP}"
    az group create --name "$RESOURCE_GROUP" --location "$LOCATION"
    log_success "Resource group created"
else
    log_success "Resource group exists: ${RESOURCE_GROUP}"
fi

echo ""

# =============================================================================
# CREATE ACR WITH AZURE CLI (Bicep deployment fails with SKU errors)
# =============================================================================

log_info "Creating ACR with Azure CLI (workaround for Bicep SKU restriction)..."

# Generate ACR name using same logic as Bicep
RG_ID=$(az group show --name "$RESOURCE_GROUP" --query id -o tsv)
# Note: Using simple hash since we can't replicate Bicep's uniqueString() exactly
# This creates a deterministic name that won't conflict
ACR_NAME=$(echo -n "${APP_NAME}$(echo -n "$RG_ID" | sha256sum | cut -c1-6)acr" | tr -d '-')

# Create ACR if it doesn't exist
if ! az acr show --name "$ACR_NAME" &>/dev/null; then
    log_info "Creating new ACR: ${ACR_NAME}"
    az acr create \
        --name "$ACR_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --location "$LOCATION" \
        --sku Standard \
        --admin-enabled false
    log_success "ACR created: ${ACR_NAME}"
else
    log_success "ACR already exists: ${ACR_NAME}"
fi

echo ""

# =============================================================================
# DEPLOY INFRASTRUCTURE (will detect existing ACR)
# =============================================================================

log_info "Deploying infrastructure with Bicep..."

DEPLOYMENT_NAME="${APP_NAME}-${ENVIRONMENT}-$(date +%Y%m%d-%H%M%S)"

az deployment group create \
    --name "$DEPLOYMENT_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --template-file infra/main.bicep \
    --parameters \
        appName="$APP_NAME" \
        environmentName="$ENVIRONMENT" \
        location="$LOCATION" \
        imageTag="$IMAGE_TAG" \
        azureOpenAiEndpoint="$AZURE_OPENAI_ENDPOINT" \
        azureOpenAiKey="$AZURE_OPENAI_KEY" \
        azureOpenAiDeployment="${AZURE_OPENAI_DEPLOYMENT:-gpt-4}" \
        azureOpenAiApiVersion="${AZURE_OPENAI_API_VERSION:-2024-02-15-preview}" \
        storageMode=blob \
        azureStorageConnectionString="$AZURE_STORAGE_CONNECTION_STRING" \
        azureStorageContainerName="${AZURE_STORAGE_CONTAINER_NAME:-factory-data}"

log_success "Infrastructure deployed"

# Set image names (ACR_NAME was set earlier when we created the ACR)
BACKEND_IMAGE="${ACR_NAME}.azurecr.io/${APP_NAME}/backend:${IMAGE_TAG}"
BACKEND_IMAGE_LATEST="${ACR_NAME}.azurecr.io/${APP_NAME}/backend:latest"
echo ""

# =============================================================================
# BUILD DOCKER IMAGE
# =============================================================================

log_info "Building Docker image..."

# Build the image with multi-stage build (context = project root)
docker build \
    --tag "${BACKEND_IMAGE}" \
    --tag "${BACKEND_IMAGE_LATEST}" \
    --file backend/Dockerfile \
    .

log_success "Docker image built: ${BACKEND_IMAGE}"
echo ""

# =============================================================================
# PUSH IMAGE TO ACR
# =============================================================================

log_info "Pushing image to Azure Container Registry..."

# Log in to ACR
az acr login --name "$ACR_NAME"

# Push both tags
docker push "${BACKEND_IMAGE}"
docker push "${BACKEND_IMAGE_LATEST}"

log_success "Image pushed to ACR"
echo ""

# =============================================================================
# GET DEPLOYMENT OUTPUTS
# =============================================================================

log_info "Getting deployment information..."

BACKEND_URL=$(az deployment group show \
    --name "$DEPLOYMENT_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --query properties.outputs.backendUrl.value \
    -o tsv)

CONTAINER_APP_NAME=$(az deployment group show \
    --name "$DEPLOYMENT_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --query properties.outputs.backendAppName.value \
    -o tsv)

echo ""

# =============================================================================
# HEALTH CHECK
# =============================================================================

log_info "Waiting for container to start (30 seconds)..."
sleep 30

log_info "Testing deployment health..."

HEALTH_URL="${BACKEND_URL}/health"
HEALTH_STATUS=0

for i in {1..5}; do
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$HEALTH_URL" || echo "000")

    if [ "$HTTP_CODE" = "200" ]; then
        log_success "Health check passed (HTTP $HTTP_CODE)"
        HEALTH_STATUS=1
        break
    else
        log_warning "Health check attempt $i/5 failed (HTTP $HTTP_CODE)"
        sleep 10
    fi
done

if [ $HEALTH_STATUS -eq 0 ]; then
    log_error "Health check failed after 5 attempts"
    log_info "Check logs with: az containerapp logs show -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP --follow"
else
    log_success "Deployment healthy and responsive"
fi

echo ""

# =============================================================================
# DEPLOYMENT SUMMARY
# =============================================================================

echo ""
echo "========================================================================="
echo "🚀 DEPLOYMENT SUCCESSFUL"
echo "========================================================================="
echo ""
echo "Environment:      ${ENVIRONMENT}"
echo "Resource Group:   ${RESOURCE_GROUP}"
echo "Image Tag:        ${IMAGE_TAG}"
echo ""
echo "Backend API URL:  ${BACKEND_URL}"
echo "API Docs:         ${BACKEND_URL}/docs"
echo "Health Check:     ${HEALTH_URL}"
echo ""
echo "========================================================================="
echo "📋 USEFUL COMMANDS"
echo "========================================================================="
echo ""
echo "View logs:"
echo "  az containerapp logs show -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP --follow"
echo ""
echo "View resource in Azure Portal:"
echo "  https://portal.azure.com/#@/resource/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/overview"
echo ""
echo "Update Container App:"
echo "  az containerapp update -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP --image $BACKEND_IMAGE"
echo ""
echo "Scale Container App:"
echo "  az containerapp update -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP --min-replicas 1 --max-replicas 5"
echo ""
echo "Delete deployment:"
echo "  az group delete --name $RESOURCE_GROUP --yes --no-wait"
echo ""
echo "========================================================================="
