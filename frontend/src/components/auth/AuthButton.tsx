/**
 * AuthButton Component - Azure AD Sign In/Out Button
 *
 * Displays user authentication status and provides sign in/out functionality.
 * Uses MSAL (Microsoft Authentication Library) for Azure AD authentication.
 *
 * Features:
 * - Shows "Sign In" button when not authenticated
 * - Shows user name/email and "Sign Out" button when authenticated
 * - Handles popup authentication flow
 * - Gracefully handles cases when Azure AD is not configured
 */

import React, { useState } from 'react';
import { useMsal } from '@azure/msal-react';
import { LogIn, LogOut, User } from 'lucide-react';
import { loginRequest, isAzureAdConfigured, getUserDisplayName } from '../../auth/authConfig';

/**
 * AuthButton Component
 *
 * Requirements:
 * - Must be wrapped in MsalProvider (configured in App.tsx)
 * - Requires Azure AD environment variables (optional for demo mode)
 */
const AuthButton: React.FC = () => {
  const { instance, accounts } = useMsal();
  const [isLoading, setIsLoading] = useState<boolean>(false);

  // Check if Azure AD is configured
  const isConfigured = isAzureAdConfigured();

  // Get current user account (if authenticated)
  const account = accounts[0];
  const isAuthenticated = !!account;

  /**
   * Handle sign in with Azure AD popup
   */
  const handleSignIn = async (): Promise<void> => {
    setIsLoading(true);
    try {
      await instance.loginPopup(loginRequest);
      console.log('[Auth] Sign in successful');
    } catch (error) {
      console.error('[Auth] Sign in failed:', error);
      // Show user-friendly error message
      alert('Sign in failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Handle sign out
   */
  const handleSignOut = async (): Promise<void> => {
    setIsLoading(true);
    try {
      await instance.logoutPopup({
        account: account,
      });
      console.log('[Auth] Sign out successful');
    } catch (error) {
      console.error('[Auth] Sign out failed:', error);
      // Show user-friendly error message
      alert('Sign out failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  // Don't render if Azure AD is not configured (demo mode)
  if (!isConfigured) {
    return (
      <div className="flex items-center gap-2 px-3 py-2 text-sm text-gray-500 dark:text-gray-400">
        <User className="w-4 h-4" />
        <span>Demo Mode</span>
      </div>
    );
  }

  // Render authenticated state
  if (isAuthenticated) {
    const displayName = getUserDisplayName(account);

    return (
      <div className="flex items-center gap-3">
        {/* User Info */}
        <div className="flex items-center gap-2 px-3 py-2 bg-green-50 dark:bg-green-900/20 rounded-lg">
          <User className="w-4 h-4 text-green-600 dark:text-green-400" />
          <span className="text-sm font-medium text-green-700 dark:text-green-300 max-w-[150px] truncate">
            {displayName}
          </span>
        </div>

        {/* Sign Out Button */}
        <button
          onClick={handleSignOut}
          disabled={isLoading}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors ${
            isLoading
              ? 'bg-gray-300 dark:bg-gray-600 cursor-not-allowed'
              : 'bg-red-600 hover:bg-red-700 text-white'
          }`}
          aria-label="Sign out"
        >
          <LogOut className="w-4 h-4" />
          <span className="hidden sm:inline">Sign Out</span>
        </button>
      </div>
    );
  }

  // Render unauthenticated state
  return (
    <button
      onClick={handleSignIn}
      disabled={isLoading}
      className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors ${
        isLoading
          ? 'bg-gray-300 dark:bg-gray-600 cursor-not-allowed'
          : 'bg-blue-600 hover:bg-blue-700 text-white'
      }`}
      aria-label="Sign in"
    >
      <LogIn className="w-4 h-4" />
      <span>{isLoading ? 'Signing In...' : 'Sign In'}</span>
    </button>
  );
};

export default AuthButton;
