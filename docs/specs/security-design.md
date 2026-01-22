# Security Design Specification

**Document**: Factory Agent Security Architecture
**Version**: 1.0
**Last Updated**: 2026-01-22

---

## Overview

This document describes the authentication and security architecture for the Factory Agent application. The design follows defense-in-depth principles with multiple security layers.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           GitHub Actions                                 │
│  ┌─────────────────┐    ┌─────────────────┐                             │
│  │ AZURE_CREDENTIALS│    │ AZURE_STATIC_   │                             │
│  │ AZURE_API_KEY   │    │ WEB_APPS_TOKEN  │                             │
│  │ STORAGE_CONN_STR│    │ VITE_API_BASE   │                             │
│  └────────┬────────┘    └────────┬────────┘                             │
│           │                      │                                       │
│           ▼                      ▼                                       │
│  ┌─────────────────┐    ┌─────────────────┐                             │
│  │ deploy-backend  │    │ deploy-frontend │                             │
│  └────────┬────────┘    └────────┬────────┘                             │
└───────────┼─────────────────────┼───────────────────────────────────────┘
            │                      │
            ▼                      ▼
┌───────────────────────┐  ┌───────────────────────┐
│   Azure Container     │  │  Azure Static Web     │
│       Apps            │  │       Apps            │
│  ┌─────────────────┐  │  │  ┌─────────────────┐  │
│  │ Managed Identity│──┼──┼──│   React + MSAL  │  │
│  └────────┬────────┘  │  │  └────────┬────────┘  │
│           │           │  │           │           │
│  ┌────────▼────────┐  │  │           │           │
│  │    FastAPI      │◄─┼──┼───────────┘           │
│  │  (JWT Verify)   │  │  │     Bearer Token      │
│  └────────┬────────┘  │  └───────────────────────┘
└───────────┼───────────┘
            │
            ▼
┌───────────────────────────────────────────────────┐
│                  Azure Services                    │
│  ┌─────────────┐  ┌─────────────┐  ┌───────────┐  │
│  │  Key Vault  │  │Blob Storage │  │ Azure AI  │  │
│  │  (Secrets)  │  │   (Data)    │  │ Foundry   │  │
│  └─────────────┘  └─────────────┘  └───────────┘  │
└───────────────────────────────────────────────────┘
```

---

## 1. Azure Key Vault Integration

### Purpose

Centralized, secure storage for all secrets. No credentials are hardcoded in source code.

### Stored Secrets

| Secret Name (Key Vault) | Environment Variable | Description |
|------------------------|---------------------|-------------|
| `AZURE-ENDPOINT` | `AZURE_ENDPOINT` | Azure AI Foundry base URL |
| `AZURE-API-KEY` | `AZURE_API_KEY` | Azure AI Foundry API key |
| `AZURE-STORAGE-CONNECTION-STRING` | `AZURE_STORAGE_CONNECTION_STRING` | Blob Storage connection |
| `AZURE-DEPLOYMENT-NAME` | `AZURE_DEPLOYMENT_NAME` | Model deployment name |

### Retrieval Logic

```python
# shared/config.py - Fallback hierarchy
def get_secret(name: str, default: str = "") -> str:
    # 1. Try Key Vault first (if KEYVAULT_URL configured)
    # 2. Fall back to environment variable
    # 3. Return default value
```

### Authentication to Key Vault

| Context | Method |
|---------|--------|
| Local Development | Azure CLI (`az login`) via `DefaultAzureCredential` |
| Production (Container Apps) | User-assigned Managed Identity |

### Key Implementation Details

- **Naming Convention**: Key Vault uses hyphens (`AZURE-API-KEY`), environment uses underscores (`AZURE_API_KEY`)
- **Quote Stripping**: Handles secrets stored with literal quotes
- **Graceful Fallback**: Logs warning if Key Vault unavailable, continues with env vars

---

## 2. GitHub Actions Secrets

### Backend Deployment Secrets

Used in `.github/workflows/deploy-backend.yml`:

| Secret | Purpose |
|--------|---------|
| `AZURE_CREDENTIALS` | Service Principal JSON for Azure login |
| `AZURE_SUBSCRIPTION_ID` | Target subscription |
| `AZURE_RESOURCE_GROUP` | Target resource group |
| `AZURE_ENDPOINT` | Passed to Container App env vars |
| `AZURE_API_KEY` | Passed to Container App env vars |
| `AZURE_STORAGE_CONNECTION_STRING` | Passed to Container App env vars |
| `AZURE_CONTAINER_REGISTRY` | ACR name for image push |

### Frontend Deployment Secrets

Used in `.github/workflows/deploy-frontend.yml`:

| Secret | Purpose |
|--------|---------|
| `AZURE_STATIC_WEB_APPS_API_TOKEN` | SWA deployment authentication |
| `VITE_API_BASE_URL` | Backend URL injected at build time |

### Security Flow

```
GitHub Secret → Workflow Variable → Bicep @secure() Parameter → Container App Env Var
```

### CI/CD Security Checks

- DEBUG mode validation (prevents `DEBUG=true` in production)
- Hardcoded secret detection in source files
- Service Principal scoped to resource group only

---

## 3. Azure AD Authentication (User Access)

### Purpose

Optional user authentication for administrative operations. The app works in two modes:

| Mode | `REQUIRE_AUTH` | Behavior |
|------|---------------|----------|
| Demo | `false` (default) | Anonymous access allowed, auth optional |
| Production | `true` | Valid Azure AD token required for POST endpoints |

### Frontend (MSAL)

Configuration in `frontend/src/auth/authConfig.ts`:

```typescript
{
  clientId: import.meta.env.VITE_AZURE_AD_CLIENT_ID,
  authority: `https://login.microsoftonline.com/${tenantId}`,
  redirectUri: window.location.origin,
  cacheLocation: 'localStorage',
  scopes: ['User.Read']
}
```

### Token Flow

1. User clicks "Sign In" → MSAL popup
2. User authenticates with Microsoft account
3. Token stored in localStorage
4. Axios interceptor adds `Authorization: Bearer <token>` to requests
5. Backend validates token

### Backend JWT Validation

Implementation in `backend/src/api/auth.py`:

```python
# Validation steps:
1. Fetch Azure AD JWKS from login.microsoftonline.com
2. Extract key ID (kid) from JWT header
3. Find matching RSA public key
4. Verify signature (RS256 algorithm)
5. Validate audience (must match client ID)
6. Validate issuer (must be correct tenant)
7. Extract user info (email, name, oid)
```

### Dependency Functions

| Function | Use Case |
|----------|----------|
| `get_current_user()` | Always require authentication |
| `get_current_user_optional()` | Return demo user if no token |
| `get_current_user_conditional()` | Respect `REQUIRE_AUTH` setting |

---

## 4. Azure OpenAI Authentication

### Method

API Key authentication (key stored in Key Vault).

### Configuration

| Setting | Description |
|---------|-------------|
| `AZURE_ENDPOINT` | Base URL only: `https://<resource>.services.ai.azure.com/` |
| `AZURE_API_KEY` | Secret from Key Vault |
| `AZURE_DEPLOYMENT_NAME` | Model name (e.g., `gpt-4o`) |
| `AZURE_API_VERSION` | API version string |

### Implementation

```python
# shared/chat_service.py
client = AsyncAzureOpenAI(
    azure_endpoint=settings.AZURE_ENDPOINT,
    api_key=settings.AZURE_API_KEY,
    api_version=settings.AZURE_API_VERSION
)
```

**Note**: Uses `AsyncAzureOpenAI` for proper async handling in FastAPI routes.

---

## 5. Azure Blob Storage Authentication

### Method

Connection string authentication (stored in Key Vault).

### Configuration

| Setting | Description |
|---------|-------------|
| `AZURE_STORAGE_CONNECTION_STRING` | Full connection string |
| `AZURE_BLOB_CONTAINER` | Container name (default: `factory-data`) |
| `AZURE_BLOB_NAME` | Blob filename (default: `production.json`) |

### Retry Policy

```
Exponential backoff: delay = initial + (base ^ (retry - 1))
Default delays: 2s, 4s, 8s
```

### Timeouts

| Setting | Default |
|---------|---------|
| Connection timeout | 30 seconds |
| Operation timeout | 60 seconds |

---

## 6. API Security Controls

### CORS

Configured via Bicep `staticWebAppHostname` parameter:

```
Development: http://localhost:3000, http://localhost:5173
Production:  SWA hostname (https://gray-ground-0bab7600f.2.azurestaticapps.net)
```

### Rate Limiting

| Endpoint | Limit |
|----------|-------|
| Chat (`/api/chat`) | 10 requests/minute |
| Setup (authenticated) | 5 requests/minute |
| Setup (anonymous) | 1 request/hour |

### Upload Size Limits

```
AZURE_BLOB_MAX_UPLOAD_SIZE = 50MB (default)
```

### Prompt Injection Protection

| Mode | Behavior |
|------|----------|
| `log` (demo) | Log suspicious patterns, allow request |
| `block` (production) | Reject suspicious patterns |

---

## 7. Infrastructure Identity (Bicep)

### Managed Identity

Created in `infra/shared.bicep`, shared by all Container Apps:

```bicep
resource managedIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: 'factory-agent-${environmentName}-identity'
  location: location
}
```

### Container App Configuration

```bicep
identity: {
  type: 'UserAssigned'
  userAssignedIdentities: {
    '${managedIdentity.id}': {}
  }
}
```

### Permissions

| Resource | Permission |
|----------|------------|
| Azure Container Registry | AcrPull (image pulls) |
| Azure Key Vault | Get secrets |

---

## 8. Environment-Specific Configuration

### Development

```bash
# .env (local)
STORAGE_MODE=local          # Use local JSON file
REQUIRE_AUTH=false          # No authentication required
DEBUG=true                  # Verbose logging
VITE_API_BASE_URL=http://localhost:8000
```

### Production

```bash
# Injected via Bicep
STORAGE_MODE=azure          # Use Blob Storage
REQUIRE_AUTH=false          # Demo mode (change for production)
DEBUG=false                 # Minimal logging
ALLOWED_ORIGINS=<swa-url>   # CORS restriction
```

---

## 9. Security Checklist

### Implemented

- [x] No hardcoded secrets in source code
- [x] All secrets in Key Vault or GitHub Secrets
- [x] JWT token validation with Azure AD public keys
- [x] CORS configured per environment
- [x] Rate limiting on sensitive endpoints
- [x] Upload size limits (DoS protection)
- [x] Prompt injection detection
- [x] DEBUG mode validation in CI/CD
- [x] Managed Identity for Azure service access
- [x] Async patterns for proper concurrent handling

### Optional Enhancements

- [ ] Enable `REQUIRE_AUTH=true` for production
- [ ] Add Application Insights for security monitoring
- [ ] Implement API key rotation schedule
- [ ] Add WAF (Web Application Firewall) for production

---

## 10. Key Files Reference

| File | Purpose |
|------|---------|
| `shared/config.py` | Key Vault + environment variable retrieval |
| `backend/src/api/auth.py` | Azure AD JWT validation |
| `frontend/src/auth/authConfig.ts` | MSAL configuration |
| `frontend/src/api/client.ts` | Axios client with auth interceptor |
| `shared/blob_storage.py` | Azure Blob Storage client |
| `.github/workflows/deploy-backend.yml` | Backend CI/CD |
| `.github/workflows/deploy-frontend.yml` | Frontend CI/CD |
| `infra/shared.bicep` | Managed Identity definition |
| `infra/backend.bicep` | Container App + environment injection |

---

## Appendix: Troubleshooting

### "Key Vault not accessible"

1. Verify `KEYVAULT_URL` is set correctly
2. Run `az login` for local development
3. Check Managed Identity has Key Vault access policies

### "JWT validation failed"

1. Verify `AZURE_AD_CLIENT_ID` matches app registration
2. Check token hasn't expired
3. Verify audience claim matches client ID

### "Blob Storage authentication failed"

1. Check connection string is complete (not truncated)
2. Verify container exists
3. Check for network connectivity to Azure
