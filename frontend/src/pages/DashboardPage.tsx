import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Plus, LogIn, Loader2, AlertCircle, CheckCircle, Info } from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { useMsal } from '@azure/msal-react';
import { apiService, getErrorMessage } from '../api/client';
import { loginRequest, isAzureAdConfigured } from '../auth/authConfig';
import type { OEEMetrics, ScrapMetrics, DowntimeAnalysis, StatsResponse } from '../types/api';

/**
 * Custom tooltip props for Recharts dark mode compatibility
 */
interface CustomTooltipProps {
  active?: boolean;
  payload?: Array<{
    value: number | string;
    name: string;
    color?: string;
    dataKey?: string;
  }>;
  label?: string;
}

/**
 * DashboardPage - Main dashboard overview page
 *
 * Displays:
 * - Production metrics cards (OEE components)
 * - OEE trend visualization
 * - Scrap rate metrics
 * - Downtime analysis charts
 * - Real-time data from backend API
 */
const DashboardPage: React.FC = () => {
  // Azure AD authentication
  const { instance, accounts } = useMsal();
  const isAuthenticated = accounts.length > 0;
  const azureAdConfigured = isAzureAdConfigured();

  // State for metrics data
  const [oee, setOee] = useState<OEEMetrics | null>(null);
  const [scrap, setScrap] = useState<ScrapMetrics | null>(null);
  const [downtime, setDowntime] = useState<DowntimeAnalysis | null>(null);
  const [stats, setStats] = useState<StatsResponse | null>(null);

  // Loading and error states
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Data generation states
  const [generating, setGenerating] = useState<boolean>(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  /**
   * Fetch all dashboard metrics on component mount
   */
  useEffect(() => {
    const fetchDashboardData = async (): Promise<void> => {
      try {
        setLoading(true);
        setError(null);

        // Fetch stats first to get date range
        const statsResponse = await apiService.getStats();
        setStats(statsResponse);

        // Only fetch metrics if data exists
        if (!statsResponse.exists) {
          setLoading(false);
          return;
        }

        // Fetch all metrics in parallel using the available date range
        const [oeeResponse, scrapResponse, downtimeResponse] = await Promise.all([
          apiService.getOEE({
            start_date: statsResponse.start_date,
            end_date: statsResponse.end_date,
          }),
          apiService.getScrap({
            start_date: statsResponse.start_date,
            end_date: statsResponse.end_date,
          }),
          apiService.getDowntime({
            start_date: statsResponse.start_date,
            end_date: statsResponse.end_date,
          }),
        ]);

        setOee(oeeResponse);
        setScrap(scrapResponse);
        setDowntime(downtimeResponse);
      } catch (err) {
        setError(getErrorMessage(err));
        console.error('Failed to fetch dashboard data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []); // Run once on mount

  /**
   * Handle data generation
   * - Prompts for sign-in if Azure AD is configured and user is not authenticated
   * - Calls backend API to generate synthetic data
   * - Refreshes dashboard after success
   */
  const handleGenerateData = async (): Promise<void> => {
    try {
      setGenerating(true);
      setError(null);
      setSuccessMessage(null);

      // If Azure AD is configured and user is not authenticated, prompt sign-in first
      if (azureAdConfigured && !isAuthenticated) {
        try {
          await instance.loginPopup(loginRequest);
          // After successful login, continue with data generation
        } catch (loginErr) {
          console.error('Failed to sign in:', loginErr);
          setError('Please sign in with your Microsoft account to generate data');
          setGenerating(false);
          return;
        }
      }

      // Generate data (default 30 days)
      const response = await apiService.generateData({ days: 30 });

      // Show success message
      setSuccessMessage(
        `Successfully generated ${response.days} days of production data for ${response.machines} machines!`
      );

      // Refresh dashboard after 1 second to allow data to settle
      setTimeout(() => {
        window.location.reload();
      }, 1000);
    } catch (err) {
      setError(getErrorMessage(err));
      console.error('Failed to generate data:', err);
    } finally {
      setGenerating(false);
    }
  };

  /**
   * Format numbers as percentages
   */
  const formatPercent = (value: number): string => {
    return `${(value * 100).toFixed(1)}%`;
  };

  /**
   * Render loading state
   */
  if (loading) {
    return (
      <div className="p-8">
        <div className="max-w-7xl mx-auto">
          <div className="flex justify-center items-center min-h-[400px]">
            <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
          </div>
        </div>
      </div>
    );
  }

  /**
   * Render error state
   */
  if (error && !stats?.exists) {
    return (
      <div className="p-8">
        <div className="max-w-7xl mx-auto">
          <div className="mt-8">
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
              <p className="text-red-800 dark:text-red-200">{error}</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  /**
   * Render empty state if no data exists
   */
  if (!stats?.exists) {
    const requiresSignIn = azureAdConfigured && !isAuthenticated;

    return (
      <div className="p-8">
        <div className="max-w-7xl mx-auto">
          {/* Page Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
              Dashboard
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Production metrics and performance overview
            </p>
          </div>

          {/* Info Alert */}
          <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4 mb-6 flex items-start gap-3">
            <Info className="w-5 h-5 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
            <p className="text-blue-800 dark:text-blue-200">
              No production data available.
              {requiresSignIn
                ? ' Click the button below to sign in and generate demo data.'
                : ' Click the button below to generate synthetic production data for testing.'}
            </p>
          </div>

          {/* Error Alert */}
          {error && (
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 mb-6 flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
              <p className="text-red-800 dark:text-red-200">{error}</p>
            </div>
          )}

          {/* Success Alert */}
          {successMessage && (
            <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4 mb-6 flex items-start gap-3">
              <CheckCircle className="w-5 h-5 text-green-600 dark:text-green-400 flex-shrink-0 mt-0.5" />
              <p className="text-green-800 dark:text-green-200">{successMessage}</p>
            </div>
          )}

          {/* Generate Data Button */}
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={handleGenerateData}
            disabled={generating}
            className="px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white rounded-lg font-medium flex items-center gap-2 transition-colors"
          >
            {generating ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                {requiresSignIn ? 'Signing in...' : 'Generating Data...'}
              </>
            ) : (
              <>
                {requiresSignIn ? <LogIn className="w-5 h-5" /> : <Plus className="w-5 h-5" />}
                {requiresSignIn ? 'Sign in & Generate Demo Data' : 'Generate Demo Data (30 days)'}
              </>
            )}
          </motion.button>
        </div>
      </div>
    );
  }

  /**
   * Prepare chart data for OEE components
   */
  const oeeComponentsData = [
    {
      name: 'Availability',
      value: oee ? oee.availability * 100 : 0,
      fill: '#8884d8',
    },
    {
      name: 'Performance',
      value: oee ? oee.performance * 100 : 0,
      fill: '#82ca9d',
    },
    {
      name: 'Quality',
      value: oee ? oee.quality * 100 : 0,
      fill: '#ffc658',
    },
  ];

  /**
   * Prepare chart data for downtime by reason
   */
  const downtimeData = downtime
    ? Object.entries(downtime.downtime_by_reason).map(([reason, hours]) => ({
        reason,
        hours: Number(hours.toFixed(1)),
      }))
    : [];

  /**
   * Custom tooltip for dark mode compatibility
   */
  const CustomTooltip: React.FC<CustomTooltipProps> = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-3 shadow-lg">
          <p className="text-gray-900 dark:text-white font-medium">{label}</p>
          {payload.map((entry, index) => (
            <p key={index} className="text-gray-600 dark:text-gray-300">
              {entry.name}: {typeof entry.value === 'number' ? entry.value.toFixed(1) : entry.value}
              {entry.name === 'value' ? '%' : ' hours'}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="p-8">
      <div className="max-w-7xl mx-auto">
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            Dashboard
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Production metrics and performance overview
          </p>
          {stats && (
            <p className="text-sm text-gray-500 dark:text-gray-500 mt-2">
              Data from {stats.start_date} to {stats.end_date} ({stats.total_days} days, {stats.total_machines} machines)
            </p>
          )}
        </div>

        {/* Key Metrics Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {/* Overall Equipment Effectiveness (OEE) */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-6"
          >
            <p className="text-sm text-gray-500 dark:text-gray-400 mb-1">Overall OEE</p>
            <p className="text-4xl font-bold text-gray-900 dark:text-white">
              {oee ? formatPercent(oee.oee) : '—'}
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
              Equipment Effectiveness
            </p>
          </motion.div>

          {/* Availability */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-6"
          >
            <p className="text-sm text-gray-500 dark:text-gray-400 mb-1">Availability</p>
            <p className="text-4xl font-bold text-blue-600 dark:text-blue-400">
              {oee ? formatPercent(oee.availability) : '—'}
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
              Uptime vs. Downtime
            </p>
          </motion.div>

          {/* Performance */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-6"
          >
            <p className="text-sm text-gray-500 dark:text-gray-400 mb-1">Performance</p>
            <p className="text-4xl font-bold text-green-600 dark:text-green-400">
              {oee ? formatPercent(oee.performance) : '—'}
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
              Speed vs. Ideal
            </p>
          </motion.div>

          {/* Quality */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-6"
          >
            <p className="text-sm text-gray-500 dark:text-gray-400 mb-1">Quality</p>
            <p className="text-4xl font-bold text-amber-600 dark:text-amber-400">
              {oee ? formatPercent(oee.quality) : '—'}
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
              Good Parts Ratio
            </p>
          </motion.div>
        </div>

        {/* Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          {/* OEE Components Bar Chart */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-6"
          >
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-1">
              OEE Components
            </h2>
            <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
              Breakdown of Overall Equipment Effectiveness
            </p>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={oeeComponentsData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.3} />
                <XAxis dataKey="name" stroke="#9CA3AF" />
                <YAxis domain={[0, 100]} stroke="#9CA3AF" />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="value" fill="#8884d8" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </motion.div>

          {/* Scrap Rate Card with Production Stats */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
            className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-6"
          >
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-1">
              Production Quality
            </h2>
            <p className="text-sm text-gray-500 dark:text-gray-400 mb-6">
              Parts production and scrap statistics
            </p>
            <div className="grid grid-cols-2 gap-4">
              <div className="text-center p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                <p className="text-3xl font-bold text-blue-600 dark:text-blue-400">
                  {oee?.total_parts.toLocaleString() ?? '—'}
                </p>
                <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">Total Parts</p>
              </div>
              <div className="text-center p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                <p className="text-3xl font-bold text-green-600 dark:text-green-400">
                  {oee?.good_parts.toLocaleString() ?? '—'}
                </p>
                <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">Good Parts</p>
              </div>
              <div className="text-center p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                <p className="text-3xl font-bold text-red-600 dark:text-red-400">
                  {scrap?.total_scrap.toLocaleString() ?? '—'}
                </p>
                <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">Scrap Parts</p>
              </div>
              <div className="text-center p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                <p className="text-3xl font-bold text-amber-600 dark:text-amber-400">
                  {scrap ? `${scrap.scrap_rate.toFixed(1)}%` : '—'}
                </p>
                <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">Scrap Rate</p>
              </div>
            </div>
          </motion.div>
        </div>

        {/* Downtime Analysis Bar Chart - Full Width */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
          className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-6"
        >
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-1">
            Downtime Analysis
          </h2>
          <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
            Total downtime: {downtime ? `${downtime.total_downtime_hours.toFixed(1)} hours` : '—'}
            {downtime && downtime.major_events.length > 0 && ` (${downtime.major_events.length} major events > 2 hours)`}
          </p>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={downtimeData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.3} />
              <XAxis dataKey="reason" stroke="#9CA3AF" />
              <YAxis stroke="#9CA3AF" label={{ value: 'Hours', angle: -90, position: 'insideLeft', fill: '#9CA3AF' }} />
              <Tooltip content={<CustomTooltip />} />
              <Legend wrapperStyle={{ color: '#9CA3AF' }} />
              <Bar dataKey="hours" fill="#ff7300" name="Downtime Hours" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </motion.div>
      </div>
    </div>
  );
};

export default DashboardPage;
