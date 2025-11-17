/**
 * MSAL (Microsoft Authentication Library) Configuration
 *
 * Configures Azure AD authentication for the Factory Agent frontend.
 * Uses environment variables for flexible deployment across environments.
 */

import type { Configuration, PopupRequest } from '@azure/msal-browser';

/**
 * Azure AD Application (Client) ID
 * Register your app in Azure Portal > Azure Active Directory > App Registrations
 */
const CLIENT_ID = import.meta.env.VITE_AZURE_AD_CLIENT_ID || '';

/**
 * Azure AD Tenant ID
 * Found in Azure Portal > Azure Active Directory > Overview
 */
const TENANT_ID = import.meta.env.VITE_AZURE_AD_TENANT_ID || 'common';

/**
 * Redirect URI after authentication
 * Must match the redirect URI configured in Azure AD app registration
 */
const REDIRECT_URI = window.location.origin;

/**
 * MSAL Configuration
 * See: https://github.com/AzureAD/microsoft-authentication-library-for-js/blob/dev/lib/msal-browser/docs/configuration.md
 */
export const msalConfig: Configuration = {
  auth: {
    clientId: CLIENT_ID,
    authority: `https://login.microsoftonline.com/${TENANT_ID}`,
    redirectUri: REDIRECT_URI,
  },
  cache: {
    cacheLocation: 'localStorage', // Store tokens in localStorage (persistent across sessions)
    storeAuthStateInCookie: false, // Set to true if you're having issues on IE11 or Edge
  },
  system: {
    loggerOptions: {
      loggerCallback: (_level, message, containsPii) => {
        if (containsPii) {
          return; // Don't log PII (Personally Identifiable Information)
        }
        // Log MSAL messages in development mode
        if (import.meta.env.DEV) {
          console.log(`[MSAL] ${message}`);
        }
      },
    },
  },
};

/**
 * Scopes to request during login
 * These permissions determine what the app can access
 */
export const loginRequest: PopupRequest = {
  scopes: ['User.Read'], // Basic Microsoft Graph permission to read user profile
};

/**
 * Check if Azure AD is configured
 * Returns false if CLIENT_ID is missing (development mode without AD)
 */
export function isAzureAdConfigured(): boolean {
  const configured = !!CLIENT_ID && CLIENT_ID !== '';
  console.log('[Auth] Azure AD configured:', configured, 'CLIENT_ID:', CLIENT_ID ? 'present' : 'missing');
  return configured;
}

/**
 * Get user display name from account
 */
export function getUserDisplayName(account: any): string {
  return account?.name || account?.username || 'User';
}
