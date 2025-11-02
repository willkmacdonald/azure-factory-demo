"""FastAPI application for Factory Agent backend.

This module serves as the main entry point for the Factory Agent backend API.
It initializes the FastAPI application, configures Cross-Origin Resource Sharing
(CORS) middleware to allow frontend access, and provides a basic health check
endpoint for monitoring service availability.

Code Flow:
1. Import required dependencies (FastAPI, CORSMiddleware, type hints)
2. Create FastAPI application instance with metadata for auto-generated docs
3. Configure CORS middleware to allow React frontend to make API requests
4. Define health check endpoint for service monitoring

This module provides:
- Health check endpoint at GET /health
- CORS configuration for React frontend (ports 3000 and 5173)
- Automatic API documentation at /docs and /redoc
"""

from typing import Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import metrics, data, chat

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
# Security note: In production, replace ["*"] wildcards with specific origins
app.add_middleware(
    CORSMiddleware,
    # allow_origins: List of origins that are permitted to make cross-origin requests
    # We include both common React development server ports:
    # - 3000: Create React App (CRA) default port
    # - 5173: Vite default port (modern React build tool)
    allow_origins=[
        "http://localhost:3000",  # Create React App default port
        "http://localhost:5173",  # Vite default port
    ],
    # allow_credentials: Allow cookies/authorization headers in cross-origin requests
    # Set to True to support authentication tokens, session cookies, etc.
    allow_credentials=True,
    # allow_methods: HTTP methods permitted for cross-origin requests
    # ["*"] allows all methods (GET, POST, PUT, DELETE, PATCH, OPTIONS, HEAD)
    # In production, restrict to only needed methods (e.g., ["GET", "POST"])
    allow_methods=["*"],
    # allow_headers: HTTP headers permitted in cross-origin requests
    # ["*"] allows all headers including custom ones like "X-Custom-Header"
    # In production, restrict to specific headers for better security
    allow_headers=["*"],
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
app.include_router(chat.router)

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
