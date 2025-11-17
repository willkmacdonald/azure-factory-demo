import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { MsalProvider } from '@azure/msal-react'
import { PublicClientApplication } from '@azure/msal-browser'
import './index.css'
import App from './App.tsx'
import { isAzureAdConfigured } from './auth/authConfig'
import { setMsalInstance } from './api/client'

/**
 * Initialize and render the application
 * Handles both with and without Azure AD configuration
 */
async function initializeApp() {
  const rootElement = document.getElementById('root');
  if (!rootElement) {
    throw new Error('Root element not found');
  }

  // Create MSAL instance (even with minimal config when Azure AD is not set up)
  // This ensures MsalProvider always has a valid instance
  const config = isAzureAdConfigured()
    ? {
        auth: {
          clientId: import.meta.env.VITE_AZURE_AD_CLIENT_ID || '',
          authority: `https://login.microsoftonline.com/${import.meta.env.VITE_AZURE_AD_TENANT_ID || 'common'}`,
          redirectUri: window.location.origin,
        },
        cache: {
          cacheLocation: 'localStorage',
          storeAuthStateInCookie: false,
        },
      }
    : {
        // Stub configuration when Azure AD is not configured
        auth: {
          clientId: '00000000-0000-0000-0000-000000000000', // Placeholder GUID
          authority: 'https://login.microsoftonline.com/common',
          redirectUri: window.location.origin,
        },
        cache: {
          cacheLocation: 'localStorage',
          storeAuthStateInCookie: false,
        },
      };

  console.log(
    isAzureAdConfigured()
      ? 'Azure AD configured, initializing MSAL...'
      : 'Azure AD not configured, using stub MSAL instance...'
  );

  const msalInstance = new PublicClientApplication(config);
  await msalInstance.initialize();

  // Only set MSAL instance for API client if Azure AD is actually configured
  if (isAzureAdConfigured()) {
    setMsalInstance(msalInstance);
  }

  createRoot(rootElement).render(
    <StrictMode>
      <MsalProvider instance={msalInstance}>
        <BrowserRouter>
          <App />
        </BrowserRouter>
      </MsalProvider>
    </StrictMode>,
  );
}

// Start the app
initializeApp().catch((error) => {
  console.error('Failed to initialize app:', error);
  document.body.innerHTML = `<div style="padding: 20px; color: red;">
    <h1>Application Error</h1>
    <p>Failed to initialize the application. Check the console for details.</p>
    <pre>${error.message}</pre>
  </div>`;
});
