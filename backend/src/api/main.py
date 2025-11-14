"""FastAPI application for Factory Agent backend.

This module serves as the main entry point for the Factory Agent backend API.
It initializes the FastAPI application, configures Cross-Origin Resource Sharing
(CORS) middleware to allow frontend access, adds rate limiting for security,
and provides a basic health check endpoint for monitoring service availability.

Code Flow:
1. Import required dependencies (FastAPI, CORSMiddleware, SlowAPI, type hints)
2. Create FastAPI application instance with metadata for auto-generated docs
3. Configure rate limiting with SlowAPI (prevents DoS attacks)
4. Configure CORS middleware with specific allowed origins from config
5. Define health check endpoint for service monitoring

This module provides:
- Rate limiting to prevent abuse (configurable per endpoint)
- Health check endpoint at GET /health
- CORS configuration for React frontend (configurable origins)
- Automatic API documentation at /docs and /redoc
"""

import logging
from typing import Dict

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from shared.config import ALLOWED_ORIGINS, DEBUG

from .routes import metrics, data, chat, traceability

# =============================================================================
# APPLICATION INITIALIZATION
# =============================================================================

# Create the main FastAPI application instance with metadata
# These metadata fields are used to generate the automatic API documentation
# available at http://localhost:8000/docs (Swagger UI) and /redoc (ReDoc)
app = FastAPI(
    title="Factory Agent API",
    description="Backend API for factory operations monitoring and analysis",
    version="1.0.0",
)

# =============================================================================
# SECURITY WARNINGS
# =============================================================================

# Warn if DEBUG mode is enabled (security risk in production)
# DEBUG mode exposes detailed error messages to clients, which can leak
# internal implementation details, file paths, and stack traces.
# This is acceptable for local development but should NEVER be enabled
# in production deployments.
if DEBUG:
    logging.warning(
        "⚠️  DEBUG MODE ENABLED - Detailed errors will be exposed to clients. "
        "Set DEBUG=false for production deployments."
    )

# =============================================================================
# RATE LIMITING CONFIGURATION
# =============================================================================

# Initialize rate limiter to prevent DoS attacks and API abuse
# The limiter uses the client's IP address (from get_remote_address) to track
# request counts. Each endpoint can specify its own rate limit using decorators.
#
# How rate limiting works:
# 1. Client sends request to API endpoint
# 2. SlowAPI extracts client IP address
# 3. Checks request count for that IP in the current time window
# 4. If under limit: processes request normally
# 5. If over limit: returns 429 Too Many Requests error
# 6. Rate limit counters reset after the time window expires
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# =============================================================================
# MIDDLEWARE CONFIGURATION
# =============================================================================

# Configure Cross-Origin Resource Sharing (CORS) middleware
# CORS is a security feature that restricts web pages from making requests to
# a different domain than the one that served the web page. Since our React
# frontend runs on a different port (3000 or 5173) than our backend (8000),
# we need to explicitly allow cross-origin requests.
#
# How this works:
# 1. Browser sends a "preflight" OPTIONS request before the actual request
# 2. CORSMiddleware intercepts and responds with allowed origins/methods/headers
# 3. Browser checks the response and allows/blocks the actual request
# 4. If allowed, the browser sends the real request (GET, POST, etc.)
#
# Security improvements (PR7):
# - Origins restricted to specific domains from ALLOWED_ORIGINS config
# - Methods restricted to GET and POST only (no PUT, DELETE, PATCH)
# - Headers restricted to common headers (no wildcard)
app.add_middleware(
    CORSMiddleware,
    # allow_origins: List of origins permitted to make cross-origin requests
    # Now loaded from config (ALLOWED_ORIGINS environment variable)
    # Default includes common React development server ports:
    # - 3000: Create React App (CRA) default port
    # - 5173: Vite default port (modern React build tool)
    # Production can override with specific domains via environment variable
    allow_origins=ALLOWED_ORIGINS,
    # allow_credentials: Allow cookies/authorization headers in cross-origin requests
    # Set to True to support authentication tokens, session cookies, etc.
    allow_credentials=True,
    # allow_methods: HTTP methods permitted for cross-origin requests
    # Restricted to GET and POST only for better security (was ["*"])
    # This prevents CSRF attacks via PUT/DELETE from unauthorized origins
    allow_methods=["GET", "POST"],
    # allow_headers: HTTP headers permitted in cross-origin requests
    # Restricted to common headers for better security (was ["*"])
    # Includes standard headers plus common auth headers
    allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
)

# =============================================================================
# ROUTER REGISTRATION
# =============================================================================

# Include the metrics router with all its endpoints
# This adds all endpoints from metrics.py to the main app
app.include_router(metrics.router)

# Include the data router with all its endpoints
# This adds all endpoints from data.py to the main app
app.include_router(data.router)

# Include the chat router with all its endpoints
# This adds all endpoints from chat.py to the main app
# Note: Chat and setup endpoints have rate limiting applied via decorators
app.include_router(chat.router)

# Include the traceability router with all its endpoints
# This adds all endpoints from traceability.py to the main app
# Provides supply chain traceability: suppliers, batches, orders, and trace queries
app.include_router(traceability.router)

# =============================================================================
# API ENDPOINTS
# =============================================================================


@app.get("/health", tags=["Health"])
async def health_check() -> Dict[str, str]:
    """Health check endpoint for service monitoring.

    This endpoint provides a simple way to verify that the API service is
    running and responsive. It's commonly used by:
    - Load balancers to determine if the service is healthy
    - Monitoring systems to track service uptime
    - Container orchestration platforms (e.g., Azure Container Apps) for liveness probes
    - CI/CD pipelines to verify successful deployment

    The endpoint uses an async function (async def) to enable non-blocking
    I/O operations. While this simple endpoint doesn't perform any I/O,
    using async establishes the pattern for future endpoints that will
    interact with databases, external APIs, or file systems.

    Flow:
    1. Client sends GET request to /health
    2. FastAPI router matches the request to this function
    3. Function immediately returns a dictionary with status
    4. FastAPI automatically serializes the dict to JSON response
    5. Response is sent back to client with 200 OK status code

    Returns:
        Dict[str, str]: JSON response with a single "status" field set to "healthy"
            Example: {"status": "healthy"}

    HTTP Response:
        Status Code: 200 OK
        Content-Type: application/json
        Body: {"status": "healthy"}

    Example usage:
        curl http://localhost:8000/health
        # Response: {"status":"healthy"}

        # With full headers
        curl -i http://localhost:8000/health
        # HTTP/1.1 200 OK
        # content-type: application/json
        # {"status":"healthy"}
    """
    # Return a simple dictionary with status information
    # FastAPI automatically converts this to a JSON response
    # The type hint Dict[str, str] ensures type safety and helps with
    # auto-generated API documentation
    return {"status": "healthy"}
