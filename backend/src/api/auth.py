"""Azure AD authentication and JWT token validation.

This module provides Azure AD (Microsoft Account) authentication for protecting
admin endpoints like POST /api/setup.

Security Model:
- Public read access: All GET endpoints work without authentication
- Authenticated write access: POST /api/setup requires valid Azure AD token

How it works:
1. Frontend uses MSAL to get Azure AD JWT token
2. Frontend sends token in Authorization header: "Bearer <token>"
3. This module validates token signature using Azure AD public keys
4. Returns user information (email, name) for logging/audit

Configuration:
- AZURE_AD_TENANT_ID: Your Azure AD tenant ID
- AZURE_AD_CLIENT_ID: Your app registration client ID
"""

import logging
import os
from typing import Dict, Optional, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
import httpx

from shared.config import REQUIRE_AUTH

logger = logging.getLogger(__name__)

# Azure AD Configuration from environment variables
AZURE_AD_TENANT_ID: Optional[str] = os.getenv("AZURE_AD_TENANT_ID")
AZURE_AD_CLIENT_ID: Optional[str] = os.getenv("AZURE_AD_CLIENT_ID")

# Azure AD JWKS URI for fetching public keys
# Format: https://login.microsoftonline.com/{tenant}/discovery/v2.0/keys
if AZURE_AD_TENANT_ID:
    AZURE_AD_JWKS_URI = (
        f"https://login.microsoftonline.com/{AZURE_AD_TENANT_ID}/discovery/v2.0/keys"
    )
    AZURE_AD_ISSUER = f"https://login.microsoftonline.com/{AZURE_AD_TENANT_ID}/v2.0"
else:
    AZURE_AD_JWKS_URI = None
    AZURE_AD_ISSUER = None

# HTTP Bearer scheme for extracting Authorization header
security = HTTPBearer(auto_error=False)  # auto_error=False allows graceful handling


async def get_azure_ad_public_keys() -> Dict[str, Any]:
    """Fetch Azure AD public keys for JWT signature validation.

    Returns:
        Dict containing JWKS (JSON Web Key Set) from Azure AD

    Raises:
        HTTPException: If unable to fetch public keys
    """
    if not AZURE_AD_JWKS_URI:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Azure AD not configured (missing AZURE_AD_TENANT_ID)",
        )

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(AZURE_AD_JWKS_URI, timeout=10.0)
            response.raise_for_status()
            return response.json()
    except httpx.RequestError as e:
        logger.error(f"Failed to fetch Azure AD public keys: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to validate authentication token (Azure AD unavailable)",
        )


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Dict[str, Any]:
    """Validate Azure AD JWT token and return user information.

    This dependency can be added to any FastAPI endpoint to require authentication.

    Args:
        credentials: HTTP Bearer credentials from Authorization header

    Returns:
        Dict containing user information:
        - email: User's email address
        - name: User's display name
        - oid: Object ID (unique user identifier)
        - preferred_username: Username

    Raises:
        HTTPException: 401 if token is missing, invalid, or expired

    Example:
        @router.post("/admin/action")
        async def admin_action(current_user: Dict = Depends(get_current_user)):
            logger.info(f"Admin action by: {current_user['email']}")
            # ... perform admin action ...
    """
    # Check if Azure AD is configured
    if not AZURE_AD_TENANT_ID or not AZURE_AD_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Authentication not configured (missing Azure AD environment variables)",
        )

    # Check if Authorization header was provided
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    try:
        # Fetch Azure AD public keys (JWKS)
        jwks = await get_azure_ad_public_keys()

        # Decode JWT header to get the key ID (kid)
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")

        if not kid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token format (missing key ID)",
            )

        # Find the matching public key
        rsa_key = None
        for key in jwks.get("keys", []):
            if key.get("kid") == kid:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"],
                }
                break

        if not rsa_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token (unable to find matching public key)",
            )

        # Verify JWT signature and decode payload
        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=["RS256"],
            audience=AZURE_AD_CLIENT_ID,  # Verify token is for our app
            issuer=AZURE_AD_ISSUER,  # Verify token is from our tenant
        )

        # Extract user information from token
        user_info = {
            "email": payload.get("email") or payload.get("preferred_username"),
            "name": payload.get("name"),
            "oid": payload.get("oid"),  # Object ID (unique user identifier)
            "preferred_username": payload.get("preferred_username"),
        }

        logger.info(f"Authenticated user: {user_info.get('email')}")
        return user_info

    except JWTError as e:
        logger.warning(f"JWT validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Unexpected error during authentication: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication error",
        )


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[Dict[str, Any]]:
    """Optional authentication dependency.

    Returns user info if valid token provided, None otherwise.
    Useful for endpoints that behave differently for authenticated users
    but don't require authentication.

    Args:
        credentials: HTTP Bearer credentials from Authorization header

    Returns:
        User info dict if authenticated, None otherwise
    """
    # If Azure AD is not configured, return demo user for local development
    if not AZURE_AD_TENANT_ID or not AZURE_AD_CLIENT_ID:
        return {
            "email": "demo@localhost",
            "name": "Demo User",
            "oid": "demo-user-id",
            "preferred_username": "demo@localhost",
        }

    if not credentials:
        return None

    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None


async def get_current_user_conditional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[Dict[str, Any]]:
    """Conditional authentication dependency based on REQUIRE_AUTH setting.

    This dependency provides environment-controlled authentication behavior:
    - When REQUIRE_AUTH=true: Requires valid Azure AD token (production mode)
    - When REQUIRE_AUTH=false: Allows anonymous access with demo user (demo mode)

    This enables the same codebase to work for both:
    1. Local development/demos without Azure AD configured
    2. Production deployments requiring authentication

    Args:
        credentials: HTTP Bearer credentials from Authorization header

    Returns:
        User info dict (authenticated user or demo user)

    Raises:
        HTTPException: 401 if REQUIRE_AUTH=true and token is missing/invalid

    Example:
        @router.post("/protected")
        async def protected_endpoint(
            current_user: Dict = Depends(get_current_user_conditional)
        ):
            logger.info(f"Access by: {current_user['email']}")
    """
    if REQUIRE_AUTH:
        # Production mode: require valid authentication
        logger.debug("REQUIRE_AUTH is enabled - validating authentication")
        user = await get_current_user(credentials)
        logger.info(f"Authenticated user access: {user.get('email')}")
        return user
    else:
        # Demo mode: allow anonymous access with optional authentication
        logger.debug("REQUIRE_AUTH is disabled - using optional authentication")
        user = await get_current_user_optional(credentials)
        if user:
            logger.debug(f"Optional authentication succeeded: {user.get('email')}")
        else:
            logger.debug("Anonymous access (no token provided)")
        return user
