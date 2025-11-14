#!/bin/bash
# =============================================================================
# Factory Agent - Local Build and Test Script
# =============================================================================
# This script builds and tests the Docker image locally before deployment.
#
# Prerequisites:
# - Docker installed and running
#
# Usage:
#   ./scripts/build-local.sh
#
# What this script does:
# 1. Validates Docker is running
# 2. Builds backend Docker image
# 3. Runs the container locally
# 4. Tests health endpoint
# 5. Shows logs and access information
# =============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="factory-agent"
CONTAINER_NAME="${APP_NAME}-backend-local"
IMAGE_NAME="${APP_NAME}/backend:local"
PORT=8000

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

log_success "Prerequisites validated"
echo ""

# =============================================================================
# ENVIRONMENT VARIABLES
# =============================================================================

log_info "Checking environment variables..."

# Load .env file if it exists
if [ -f ".env" ]; then
    log_info "Loading environment variables from .env file"
    set -a
    source .env
    set +a
else
    log_warning ".env file not found. Using environment variables only."
fi

# Check required variables
REQUIRED_VARS=(
    "AZURE_OPENAI_ENDPOINT"
    "AZURE_OPENAI_KEY"
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
    echo "Create a .env file with these variables or set them in your environment."
    echo "See .env.example for reference."
    exit 1
fi

log_success "Environment variables loaded"
echo ""

# =============================================================================
# CLEANUP EXISTING CONTAINER
# =============================================================================

if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    log_info "Stopping and removing existing container..."
    docker stop "$CONTAINER_NAME" &> /dev/null || true
    docker rm "$CONTAINER_NAME" &> /dev/null || true
    log_success "Existing container removed"
fi

echo ""

# =============================================================================
# BUILD DOCKER IMAGE
# =============================================================================

log_info "Building Docker image..."

# Build from project root (required for accessing shared/ directory)
docker build \
    --tag "$IMAGE_NAME" \
    --file backend/Dockerfile \
    .

log_success "Docker image built: ${IMAGE_NAME}"
echo ""

# =============================================================================
# RUN CONTAINER
# =============================================================================

log_info "Starting container..."

docker run -d \
    --name "$CONTAINER_NAME" \
    --publish "${PORT}:8000" \
    --env DEBUG=true \
    --env LOG_LEVEL=debug \
    --env STORAGE_MODE=local \
    --env AZURE_OPENAI_ENDPOINT="${AZURE_OPENAI_ENDPOINT}" \
    --env AZURE_OPENAI_KEY="${AZURE_OPENAI_KEY}" \
    --env AZURE_OPENAI_DEPLOYMENT="${AZURE_OPENAI_DEPLOYMENT:-gpt-4}" \
    --env AZURE_OPENAI_API_VERSION="${AZURE_OPENAI_API_VERSION:-2024-02-15-preview}" \
    --env ALLOWED_ORIGINS="http://localhost:3000,http://localhost:5173" \
    --volume "$(pwd)/backend/data:/code/data" \
    --volume "$(pwd)/shared:/code/shared:ro" \
    "$IMAGE_NAME"

log_success "Container started: ${CONTAINER_NAME}"
echo ""

# =============================================================================
# WAIT FOR STARTUP
# =============================================================================

log_info "Waiting for container to start (10 seconds)..."
sleep 10

# =============================================================================
# HEALTH CHECK
# =============================================================================

log_info "Testing health endpoint..."

HEALTH_URL="http://localhost:${PORT}/health"
HEALTH_STATUS=0

for i in {1..5}; do
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$HEALTH_URL" 2>/dev/null || echo "000")

    if [ "$HTTP_CODE" = "200" ]; then
        log_success "Health check passed (HTTP $HTTP_CODE)"
        HEALTH_RESPONSE=$(curl -s "$HEALTH_URL")
        echo "Response: $HEALTH_RESPONSE"
        HEALTH_STATUS=1
        break
    else
        log_warning "Health check attempt $i/5 failed (HTTP $HTTP_CODE)"
        sleep 5
    fi
done

if [ $HEALTH_STATUS -eq 0 ]; then
    log_error "Health check failed after 5 attempts"
    log_info "Container logs:"
    docker logs "$CONTAINER_NAME"
    exit 1
fi

echo ""

# =============================================================================
# SHOW LOGS
# =============================================================================

log_info "Recent container logs:"
echo ""
docker logs --tail 20 "$CONTAINER_NAME"

echo ""

# =============================================================================
# SUMMARY
# =============================================================================

echo ""
echo "========================================================================="
echo "🚀 CONTAINER RUNNING SUCCESSFULLY"
echo "========================================================================="
echo ""
echo "Backend API:      http://localhost:${PORT}"
echo "API Docs:         http://localhost:${PORT}/docs"
echo "ReDoc:            http://localhost:${PORT}/redoc"
echo "Health Check:     http://localhost:${PORT}/health"
echo ""
echo "Container Name:   ${CONTAINER_NAME}"
echo "Image:            ${IMAGE_NAME}"
echo ""
echo "========================================================================="
echo "📋 USEFUL COMMANDS"
echo "========================================================================="
echo ""
echo "View logs (follow):"
echo "  docker logs -f $CONTAINER_NAME"
echo ""
echo "View logs (last 100 lines):"
echo "  docker logs --tail 100 $CONTAINER_NAME"
echo ""
echo "Stop container:"
echo "  docker stop $CONTAINER_NAME"
echo ""
echo "Remove container:"
echo "  docker rm $CONTAINER_NAME"
echo ""
echo "Restart container:"
echo "  docker restart $CONTAINER_NAME"
echo ""
echo "Execute shell in container:"
echo "  docker exec -it $CONTAINER_NAME /bin/bash"
echo ""
echo "Test API endpoint:"
echo "  curl http://localhost:${PORT}/health | jq '.'"
echo ""
echo "========================================================================="
echo ""
echo "Press Ctrl+C to stop following logs, or run:"
echo "  docker logs -f $CONTAINER_NAME"
echo ""
