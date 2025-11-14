# =============================================================================
# Multi-Stage Dockerfile for Factory Agent FastAPI Backend
# =============================================================================
# This Dockerfile uses a multi-stage build approach to optimize the final
# image size and security by separating the build environment from the
# runtime environment.
#
# IMPORTANT: Build context must be the PROJECT ROOT, not the backend/ directory
# Example: docker build -f backend/Dockerfile -t factory-agent/backend .
#
# Stage 1 (builder): Installs dependencies and prepares the environment
# Stage 2 (runtime): Copies only necessary files and runs the application
#
# Benefits:
# - Smaller final image (no build tools or cached pip files)
# - Better security (fewer packages, reduced attack surface)
# - Faster deployments (smaller image size)
# - Layer caching for faster rebuilds
# =============================================================================

# =============================================================================
# STAGE 1: Builder
# =============================================================================
# This stage installs all Python dependencies and prepares wheels.
# Build tools and cached files will NOT be included in the final image.
FROM python:3.11-slim AS builder

# Set working directory for build stage
WORKDIR /build

# Install system dependencies needed for building Python packages
# - gcc: C compiler for packages with native extensions
# - python3-dev: Python development headers
# These will NOT be in the final image (builder stage only)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    python3-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy only requirements file first (Docker layer caching optimization)
# If requirements.txt doesn't change, this layer will be cached and reused
# Note: Build context must be project root, so path is backend/requirements.txt
COPY backend/requirements.txt .

# Install Python dependencies
# --no-cache-dir: Don't cache pip downloads (reduces image size)
# --upgrade: Ensure latest compatible versions
# --user: Install to user site-packages (easier to copy to final stage)
RUN pip install --no-cache-dir --upgrade --user -r requirements.txt

# =============================================================================
# STAGE 2: Runtime
# =============================================================================
# This stage creates the minimal runtime environment with only what's needed
# to run the application (no build tools, no pip cache, no unnecessary files).
FROM python:3.11-slim

# Set environment variables
# PYTHONUNBUFFERED=1: Force stdout/stderr to be unbuffered (real-time logs)
# PYTHONDONTWRITEBYTECODE=1: Prevent Python from writing .pyc files (not needed)
# PATH: Add user site-packages to PATH for installed dependencies
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH=/root/.local/bin:$PATH

# Set working directory for the application
WORKDIR /code

# Copy Python dependencies from builder stage (user site-packages)
# This includes all installed packages WITHOUT pip cache or build artifacts
COPY --from=builder /root/.local /root/.local

# Copy application source code
# This includes:
# - src/api/: FastAPI application and routes
# - src/__init__.py: Package initialization
# Note: Build context is project root, so path is backend/src
COPY backend/src /code/src

# Copy shared modules from project root
# The shared directory contains models, config, data layer, and metrics
# that are used by both CLI and API
COPY shared /code/shared

# Create data directory for local JSON storage (development mode)
# In production with Azure Blob Storage, this won't be used
RUN mkdir -p /code/data

# Expose port 8000 for the FastAPI application
# This is the default port for Uvicorn and matches Azure Container Apps config
EXPOSE 8000

# Health check configuration for container orchestration
# Azure Container Apps and Docker will use this to verify the service is healthy
# - interval: Check every 30 seconds
# - timeout: Fail if health check takes longer than 10 seconds
# - start-period: Wait 40 seconds before first check (app startup time)
# - retries: Mark unhealthy after 3 consecutive failures
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()"

# Run the FastAPI application with Uvicorn
# Command breakdown:
# - python -m uvicorn: Run uvicorn as a module
# - src.api.main:app: Import path to FastAPI app instance
#   * src.api.main: Python module path
#   * app: Variable name of FastAPI instance
# - --host 0.0.0.0: Listen on all network interfaces (required for Docker)
# - --port 8000: Listen on port 8000 (standard HTTP alternate)
# - --workers 1: Single worker process (Azure Container Apps handles scaling)
# - --log-level info: Log level (info, debug, warning, error)
#
# Why single worker?
# Azure Container Apps handles horizontal scaling by creating multiple container
# instances. Each container should run a single Uvicorn worker for simplicity
# and better resource isolation. The platform handles load balancing.
#
# For local development with higher load, you can override with:
# docker run -e WORKERS=4 <image>
CMD ["python", "-m", "uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--log-level", "info"]
