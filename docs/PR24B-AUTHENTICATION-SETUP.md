# PR24B: Authentication on Protected Endpoints - Setup Guide

## Overview

PR24B implements Azure AD authentication to secure critical endpoints that modify data. This prevents unauthorized access while maintaining ease of use for demos and development.

## What Was Implemented

### ✅ Backend Changes

1. **POST /api/setup** (REQUIRED Authentication)
   - Now requires valid Azure AD JWT token
   - Only authenticated users can generate/overwrite production data
   - Logs authenticated user email for audit trail
   - Returns HTTP 401 if not authenticated

2. **POST /api/chat** (OPTIONAL Authentication)
   - Authentication is optional but recommended
   - If authenticated: User email logged for cost attribution
   - If not authenticated: Works as anonymous user
   - Enables gradual rollout: demo mode → authenticated mode

### ✅ Frontend Changes

1. **AuthButton Component**
   - Displays "Sign In" button when not authenticated
   - Shows user name/email + "Sign Out" button when authenticated
   - Handles popup authentication flow
   - Shows "Demo Mode" badge when Azure AD not configured

2. **App.tsx with MsalProvider**
   - Initializes MSAL (Microsoft Authentication Library)
   - Wraps app in MsalProvider for authentication context
   - Configures API client to automatically add Bearer tokens
   - Gracefully handles unconfigured Azure AD (demo mode)

3. **MainLayout Integration**
   - AuthButton in bottom of desktop sidebar
   - AuthButton in mobile top bar (compact)
   - Responsive design for mobile and desktop

## Setup Instructions

### Option 1: Run Without Authentication (Demo Mode)

**No setup required!** The app works without Azure AD configuration.

- AuthButton will show "Demo Mode"
- All GET endpoints work normally
- POST /api/setup will fail with HTTP 401 (protected)
- POST /api/chat works anonymously

### Option 2: Enable Authentication (Production Mode)

#### Step 1: Register App in Azure AD

1. Go to [Azure Portal](https://portal.azure.com) → Azure Active Directory → App Registrations
2. Click "New registration"
3. Configure:
   - **Name**: Factory Agent
   - **Supported account types**: Accounts in this organizational directory only
   - **Redirect URI**:
     - Type: Single-page application (SPA)
     - URI: `http://localhost:5173` (for local development)
4. Click "Register"
5. Note down:
   - **Application (client) ID**
   - **Directory (tenant) ID**

#### Step 2: Configure API Permissions

1. In your app registration → API permissions
2. Click "Add a permission" → Microsoft Graph → Delegated permissions
3. Select: `User.Read` (basic profile)
4. Click "Add permissions"
5. Click "Grant admin consent" (if you have admin rights)

#### Step 3: Configure Backend Environment Variables

Create/update `backend/.env`:

```bash
# Azure AD Configuration (Backend)
AZURE_AD_TENANT_ID=your-tenant-id-here
AZURE_AD_CLIENT_ID=your-client-id-here
```

#### Step 4: Configure Frontend Environment Variables

Create/update `frontend/.env`:

```bash
# Azure AD Configuration (Frontend)
VITE_AZURE_AD_TENANT_ID=your-tenant-id-here
VITE_AZURE_AD_CLIENT_ID=your-client-id-here

# API Base URL (should already be configured)
VITE_API_BASE_URL=http://localhost:8000
```

#### Step 5: Test Authentication Flow

1. Start backend:
   ```bash
   cd backend
   PYTHONPATH=/Users/willmacdonald/Documents/Code/azure/factory-agent:$PYTHONPATH venv/bin/uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. Start frontend:
   ```bash
   cd frontend
   npm run dev
   ```

3. Open browser to `http://localhost:5173`

4. Click "Sign In" button (bottom of sidebar or top right on mobile)

5. Complete Azure AD sign-in flow in popup

6. Verify:
   - AuthButton shows your name/email
   - Browser console shows: `[Auth] Sign in successful`
   - API requests include `Authorization: Bearer <token>` header

7. Test protected endpoint:
   - Try generating data (requires backend implementation that uses POST /api/setup)
   - Should succeed if authenticated
   - Should fail with HTTP 401 if not authenticated

## Authentication Flow

```
User clicks "Sign In"
    ↓
AuthButton calls instance.loginPopup()
    ↓
MSAL opens Azure AD popup
    ↓
User signs in with Microsoft account
    ↓
Azure AD returns JWT token
    ↓
MSAL stores token in localStorage
    ↓
API client intercepts requests
    ↓
acquireTokenSilent() gets token from MSAL
    ↓
Adds "Authorization: Bearer <token>" header
    ↓
Backend validates token with Azure AD public keys
    ↓
Returns user info (email, name) to endpoint
    ↓
Endpoint logs user action for audit trail
```

## Security Notes

### What's Protected

- ✅ **POST /api/setup**: Requires authentication (prevents unauthorized data overwrites)
- ✅ **POST /api/chat**: Optional authentication (enables cost tracking)
- ✅ **Token validation**: Backend verifies JWT signature, expiration, audience, issuer
- ✅ **Audit logging**: All authenticated actions logged with user email

### What's Not Protected

- ℹ️ **All GET endpoints**: Public read access (by design for demo)
- ℹ️ **Rate limiting**: Applied to all endpoints regardless of authentication
- ℹ️ **Input validation**: Applied to all endpoints via Pydantic models

### Production Hardening (Future PRs)

For production deployment, consider:

1. **Make chat authentication required** (environment flag)
2. **Add role-based authorization** (admin vs user roles)
3. **Implement per-user rate limits** (instead of per-IP)
4. **Add content filtering** (Azure Content Safety API)
5. **Enable detailed audit logging** (Azure Monitor/Application Insights)
6. **Rotate API keys regularly** (Azure Key Vault integration)

## Troubleshooting

### "MSAL not configured" warning

- Azure AD environment variables not set
- App runs in Demo Mode (expected behavior)
- Solution: Follow "Enable Authentication" steps above

### "Invalid token" error (HTTP 401)

- Token expired (default: 1 hour)
- Solution: Sign out and sign in again
- Token refresh: MSAL handles automatically with `acquireTokenSilent()`

### "Failed to acquire access token" warning

- User not signed in
- Solution: Click "Sign In" button
- Or: Silent token acquisition failed, retry with `loginPopup()`

### CORS errors

- Backend ALLOWED_ORIGINS environment variable doesn't include frontend URL
- Solution: Add `http://localhost:5173` to ALLOWED_ORIGINS in backend/.env

### Popup blocked by browser

- Browser blocked authentication popup
- Solution: Allow popups for localhost in browser settings
- Alternative: Use redirect flow (requires code changes)

## Testing Checklist

- [ ] Demo Mode works without Azure AD configuration
- [ ] AuthButton shows "Demo Mode" when not configured
- [ ] AuthButton shows "Sign In" when configured but not signed in
- [ ] Sign In popup appears when button clicked
- [ ] AuthButton shows user name after sign in
- [ ] Sign Out removes user session
- [ ] API requests include Authorization header when signed in
- [ ] POST /api/setup requires authentication (HTTP 401 if anonymous)
- [ ] POST /api/chat works both authenticated and anonymous
- [ ] Backend logs show user email for authenticated requests
- [ ] Mobile layout shows compact AuthButton in top bar
- [ ] Desktop layout shows AuthButton at bottom of sidebar

## Files Modified

### Backend
- `backend/src/api/routes/data.py` - Added authentication to POST /api/setup
- `backend/src/api/routes/chat.py` - Added optional authentication to POST /api/chat
- `backend/src/api/auth.py` - Already existed (JWT validation logic)

### Frontend
- `frontend/src/components/auth/AuthButton.tsx` - NEW: Sign in/out button component
- `frontend/src/components/layout/MainLayout.tsx` - Added AuthButton to layout
- `frontend/src/App.tsx` - Added MsalProvider and MSAL initialization
- `frontend/src/auth/authConfig.ts` - Already existed (MSAL configuration)
- `frontend/src/api/client.ts` - Already existed (token attachment logic)

## Environment Variables Reference

### Backend (.env)

```bash
# Azure AD Authentication
AZURE_AD_TENANT_ID=          # Azure AD tenant ID (required for auth)
AZURE_AD_CLIENT_ID=          # Azure AD application client ID (required for auth)

# Existing variables (not changed)
AZURE_ENDPOINT=              # Azure OpenAI endpoint
AZURE_API_KEY=               # Azure OpenAI API key
AZURE_DEPLOYMENT_NAME=       # Azure OpenAI deployment name
STORAGE_MODE=local           # local or azure
DEBUG=false                  # Development mode flag
```

### Frontend (.env)

```bash
# Azure AD Authentication
VITE_AZURE_AD_TENANT_ID=     # Azure AD tenant ID (required for auth)
VITE_AZURE_AD_CLIENT_ID=     # Azure AD application client ID (required for auth)

# Existing variables (not changed)
VITE_API_BASE_URL=http://localhost:8000  # Backend API base URL
```

## Next Steps (Future PRs)

- **PR24C**: Data protection enhancements (upload limits, XSS fixes)
- **PR24D**: Quality improvements (Python version check, config validation)
- **PR25**: Comprehensive test suite for authentication flows
- **PR26**: Role-based authorization (admin vs user permissions)

## Questions?

See also:
- `backend/src/api/auth.py` - JWT validation implementation
- `frontend/src/auth/authConfig.ts` - MSAL configuration
- Azure AD Documentation: https://learn.microsoft.com/en-us/azure/active-directory/develop/
- MSAL.js Documentation: https://github.com/AzureAD/microsoft-authentication-library-for-js
