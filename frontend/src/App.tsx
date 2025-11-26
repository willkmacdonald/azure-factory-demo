import { useEffect } from 'react';
import { Routes, Route } from 'react-router-dom';
import { MsalProvider } from '@azure/msal-react';
import { PublicClientApplication } from '@azure/msal-browser';
import MainLayout from './components/layout/MainLayout';
import DashboardPage from './pages/DashboardPage';
import MachinesPage from './pages/MachinesPage';
import AlertsPage from './pages/AlertsPage';
import TraceabilityPage from './pages/TraceabilityPage';
import ChatPage from './pages/ChatPage';
import { msalConfig, isAzureAdConfigured } from './auth/authConfig';
import { setMsalInstance } from './api/client';
import './App.css';

/**
 * Main Application Component for Factory Agent
 *
 * PR24B: Added Azure AD authentication with MSAL
 * - MsalProvider wraps entire app for authentication context
 * - Authentication is optional (gracefully handles unconfigured Azure AD)
 * - API client automatically adds Bearer tokens to protected endpoints
 * - AuthButton component in MainLayout provides sign in/out UI
 *
 * Authentication Flow:
 * 1. MSAL instance initialized with config from authConfig.ts
 * 2. MsalProvider makes MSAL available to all components via useMsal hook
 * 3. AuthButton uses useMsal to trigger login/logout
 * 4. API client intercepts requests and adds Bearer token from MSAL
 * 5. Backend validates token on protected endpoints (POST /api/setup)
 *
 * Environment Variables Required (Optional):
 * - VITE_AZURE_AD_CLIENT_ID: Azure AD application (client) ID
 * - VITE_AZURE_AD_TENANT_ID: Azure AD tenant ID (defaults to 'common')
 *
 * If not configured, app runs in "Demo Mode" without authentication.
 */

// Initialize MSAL instance
// Note: Only initialize if Azure AD is configured to avoid unnecessary errors
let msalInstance: PublicClientApplication | null = null;

if (isAzureAdConfigured()) {
  msalInstance = new PublicClientApplication(msalConfig);
  console.log('[App] MSAL initialized with Azure AD configuration');
} else {
  console.log('[App] Running in Demo Mode (Azure AD not configured)');
}

function AppContent() {
  useEffect(() => {
    // Set MSAL instance in API client for automatic token attachment
    if (msalInstance) {
      setMsalInstance(msalInstance);
      console.log('[App] MSAL instance configured in API client');
    }
  }, []);

  return (
    <Routes>
      {/* Main layout route with nested child routes */}
      <Route path="/" element={<MainLayout />}>
        {/* Index route - Dashboard */}
        <Route index element={<DashboardPage />} />

        {/* Machines route */}
        <Route path="machines" element={<MachinesPage />} />

        {/* Alerts route */}
        <Route path="alerts" element={<AlertsPage />} />

        {/* Traceability route */}
        <Route path="traceability" element={<TraceabilityPage />} />

        {/* AI Chat route */}
        <Route path="chat" element={<ChatPage />} />
      </Route>
    </Routes>
  );
}

function App() {
  // Wrap app in MsalProvider if MSAL is configured, otherwise render directly
  if (msalInstance) {
    return (
      <MsalProvider instance={msalInstance}>
        <AppContent />
      </MsalProvider>
    );
  }

  // Demo mode: No MSAL provider
  return <AppContent />;
}

export default App;
