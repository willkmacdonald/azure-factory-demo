/**
 * API Health Check Component
 *
 * Simple component to verify API connectivity.
 * Displays connection status and provides manual refresh.
 */

import React from 'react';
import { motion } from 'framer-motion';
import { CheckCircle, XCircle, RefreshCw, Loader2 } from 'lucide-react';
import { useAsyncData } from '../utils/async';
import { apiService } from '../api/client';

/**
 * ApiHealthCheck - Component for testing API connectivity
 *
 * Usage:
 * ```tsx
 * <ApiHealthCheck />
 * ```
 */
export const ApiHealthCheck: React.FC = () => {
  // Use the useAsyncData hook to fetch health status
  const { data, loading, error, refetch } = useAsyncData(
    async () => await apiService.checkHealth(),
    { immediate: true }
  );

  return (
    <div className="max-w-xl mx-auto mt-8">
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-md overflow-hidden">
        <div className="p-6">
          {/* Header */}
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
              API Health Check
            </h2>
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={refetch}
              disabled={loading}
              className="inline-flex items-center gap-2 px-3 py-1.5 text-sm font-medium text-blue-600 dark:text-blue-400 border border-blue-600 dark:border-blue-400 rounded-lg hover:bg-blue-50 dark:hover:bg-blue-900/20 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </motion.button>
          </div>

          {/* Loading State */}
          {loading && (
            <div className="flex items-center gap-3">
              <Loader2 className="w-5 h-5 text-blue-600 dark:text-blue-400 animate-spin" />
              <span className="text-gray-600 dark:text-gray-400">
                Checking API connection...
              </span>
            </div>
          )}

          {/* Error State */}
          {!loading && error && (
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
              <div className="flex items-start gap-3">
                <XCircle className="w-5 h-5 text-red-600 dark:text-red-400 mt-0.5 flex-shrink-0" />
                <div>
                  <p className="font-semibold text-red-800 dark:text-red-200">
                    Connection Failed
                  </p>
                  <p className="text-sm text-red-700 dark:text-red-300 mt-1">
                    {error}
                  </p>
                  <p className="text-xs text-red-600 dark:text-red-400 mt-2">
                    Make sure the backend server is running on port 8000
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Success State */}
          {!loading && !error && data && (
            <div>
              <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4">
                <div className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-green-600 dark:text-green-400 mt-0.5 flex-shrink-0" />
                  <div>
                    <p className="font-semibold text-green-800 dark:text-green-200">
                      API Connected
                    </p>
                    <p className="text-sm text-green-700 dark:text-green-300 mt-1">
                      Backend is healthy and responding normally
                    </p>
                  </div>
                </div>
              </div>

              {/* Status Chips */}
              <div className="flex flex-wrap gap-2 mt-4">
                <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200">
                  Status: {data.status}
                </span>
                <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200">
                  URL: {import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}
                </span>
              </div>
            </div>
          )}

          {/* API Information */}
          <div className="mt-6 p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
            <p className="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-2">
              Backend API Endpoints:
            </p>
            <div className="space-y-1 text-xs text-gray-500 dark:text-gray-400">
              <p>• GET /health - Health check</p>
              <p>• GET /api/metrics/oee - OEE metrics</p>
              <p>• GET /api/metrics/scrap - Scrap metrics</p>
              <p>• GET /api/metrics/quality - Quality issues</p>
              <p>• GET /api/metrics/downtime - Downtime analysis</p>
              <p>• POST /api/chat - Chat with AI</p>
              <p>• POST /api/setup - Generate data</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ApiHealthCheck;
