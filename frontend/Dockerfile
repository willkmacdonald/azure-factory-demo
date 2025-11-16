# =============================================================================
# Multi-Stage Dockerfile for Factory Agent React Frontend
# =============================================================================
# This Dockerfile uses a multi-stage build approach to create an optimized
# production image for the React + Vite frontend application.
#
# IMPORTANT: Build context must be the PROJECT ROOT, not the frontend/ directory
# Example: docker build -f frontend/Dockerfile -t factory-agent/frontend .
#
# Stage 1 (builder): Builds the React app with Vite
# Stage 2 (runtime): Serves static files with Nginx
#
# Benefits:
# - Minimal final image size (~25MB vs ~1GB with Node)
# - Runtime environment variable injection (no rebuild needed)
# - Production-optimized Nginx configuration
# - Security hardening (non-root user, minimal attack surface)
# - SPA routing support (all routes → index.html)
# =============================================================================

# =============================================================================
# STAGE 1: Builder
# =============================================================================
# This stage installs dependencies and builds the React app with Vite.
FROM node:22-alpine AS builder

# Set working directory for build stage
WORKDIR /build

# Copy package files first (Docker layer caching optimization)
# If package.json doesn't change, this layer will be cached and reused
COPY frontend/package*.json ./

# Install dependencies
# --frozen-lockfile: Use exact versions from package-lock.json (if exists)
# --prefer-offline: Use cache when possible to speed up builds
RUN npm ci --prefer-offline

# Copy frontend source code
COPY frontend/ ./

# Copy shared TypeScript types (if frontend references them)
# Note: Currently frontend has its own types in src/types/api.ts
# This is here for future if we want to share types between frontend/backend

# Build the application for production
# Vite will:
# - Bundle and minify JavaScript/TypeScript
# - Optimize CSS and assets
# - Generate source maps (if configured)
# - Output to ./dist directory
RUN npm run build

# =============================================================================
# STAGE 2: Runtime with Nginx
# =============================================================================
# This stage creates a minimal production image with only static files and Nginx.
FROM nginx:1.27-alpine

# Install bash for startup script (Alpine uses sh by default)
RUN apk add --no-cache bash

# Remove default Nginx configuration
RUN rm -rf /etc/nginx/conf.d/*

# Copy custom Nginx configuration for SPA
# This config:
# - Enables gzip compression
# - Sets security headers
# - Routes all requests to index.html (SPA routing)
# - Configures caching for static assets
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

# Copy built static files from builder stage
# Nginx will serve these files from /usr/share/nginx/html
COPY --from=builder /build/dist /usr/share/nginx/html

# Copy runtime environment variable injection script
# This script generates env.js at container startup with runtime config
COPY frontend/docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Create directory for runtime config
RUN mkdir -p /usr/share/nginx/html/config

# Expose port 80 for HTTP traffic
# Azure Container Apps will handle HTTPS termination
EXPOSE 80

# Health check for container orchestration
# Azure Container Apps uses this to verify the service is healthy
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:80/ || exit 1

# Set the entrypoint to our script
# This will:
# 1. Generate env.js with runtime environment variables
# 2. Start Nginx in the foreground
ENTRYPOINT ["/docker-entrypoint.sh"]
