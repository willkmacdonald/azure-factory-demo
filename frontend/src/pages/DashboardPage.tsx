import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Plus, LogIn, Loader2 } from 'lucide-react';
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
 * DashboardPage - Main dashboard overview page
 *
 * Now using Tailwind CSS for styling, Framer Motion for animations,
 * and Lucide React for icons to match the my-website project style.
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
   * Handle user sign-in with Azure AD
   */
  const handleSignIn = async (): Promise<void> => {
    try {
      await instance.loginPopup(loginRequest);
    } catch (err) {
      console.error('Failed to sign in:', err);
      setError('Failed to sign in with Microsoft account');
    }
  };

  /**
   * Handle data generation
   * - Requires user authentication
   * - Calls backend API to generate synthetic data
   * - Refreshes dashboard after success
   */
  const handleGenerateData = async (): Promise<void> => {
    try {
      setGenerating(true);
      setError(null);
      setSuccessMessage(null);

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
      <div className="min-h-screen bg-white dark:bg-gray-900 flex items-center justify-center">
        <Loader2 className="w-12 h-12 text-blue-600 dark:text-blue-400 animate-spin" />
      </div>
    );
  }

  /**
   * Render error state
   */
  if (error) {
    return (
      <div className="min-h-screen bg-white dark:bg-gray-900 p-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="max-w-7xl mx-auto"
        >
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 text-red-800 dark:text-red-200">
            {error}
          </div>
        </motion.div>
      </div>
    );
  }

  /**
   * Render empty state if no data exists
   */
  if (!stats?.exists) {
    // Determine which button to show based on Azure AD configuration and auth state
    const showSignInButton = azureAdConfigured && !isAuthenticated;
    const showGenerateButton = !azureAdConfigured || isAuthenticated;

    return (
      <div className="min-h-screen bg-white dark:bg-gray-900 p-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="max-w-7xl mx-auto"
        >
          <div className="mb-8">
            <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
              Dashboard
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Production metrics and performance overview
            </p>
          </div>

          <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4 mb-6">
            <p className="text-blue-800 dark:text-blue-200">
              No production data available.
              {azureAdConfigured && !isAuthenticated
                ? ' Please sign in with your Microsoft account to generate demo data.'
                : ' Click the button below to generate synthetic production data for testing.'}
            </p>
          </div>

          <div className="flex gap-4 flex-wrap">
            {showSignInButton && (
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleSignIn}
                className="inline-flex items-center gap-2 px-6 py-3 border-2 border-blue-600 dark:border-blue-400 text-blue-600 dark:text-blue-400 rounded-lg font-medium hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-colors"
              >
                <LogIn className="w-5 h-5" />
                Sign in with Microsoft
              </motion.button>
            )}

            {showGenerateButton && (
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleGenerateData}
                disabled={generating}
                className="inline-flex items-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {generating ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Generating Data...
                  </>
                ) : (
                  <>
                    <Plus className="w-5 h-5" />
                    Generate Demo Data (30 days)
                  </>
                )}
              </motion.button>
            )}
          </div>

          {/* Success message */}
          {successMessage && (
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-6 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4 text-green-800 dark:text-green-200"
            >
              {successMessage}
            </motion.div>
          )}
        </motion.div>
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
      fill: '#3b82f6',
    },
    {
      name: 'Performance',
      value: oee ? oee.performance * 100 : 0,
      fill: '#10b981',
    },
    {
      name: 'Quality',
      value: oee ? oee.quality * 100 : 0,
      fill: '#f59e0b',
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

  return (
    <div className="min-h-screen bg-white dark:bg-gray-900 p-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="max-w-7xl mx-auto"
      >
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
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
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.1 }}
            whileHover={{ y: -8 }}
            className="bg-white dark:bg-gray-800 rounded-xl shadow-md hover:shadow-xl transition-shadow duration-300 p-6"
          >
            <p className="text-gray-600 dark:text-gray-400 text-sm mb-2">Overall OEE</p>
            <p className="text-4xl font-bold text-gray-900 dark:text-white">
              {oee ? formatPercent(oee.oee) : '—'}
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-500 mt-2">
              Equipment Effectiveness
            </p>
          </motion.div>

          {/* Availability */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.2 }}
            whileHover={{ y: -8 }}
            className="bg-white dark:bg-gray-800 rounded-xl shadow-md hover:shadow-xl transition-shadow duration-300 p-6"
          >
            <p className="text-gray-600 dark:text-gray-400 text-sm mb-2">Availability</p>
            <p className="text-4xl font-bold text-blue-600 dark:text-blue-400">
              {oee ? formatPercent(oee.availability) : '—'}
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-500 mt-2">
              Uptime vs. Downtime
            </p>
          </motion.div>

          {/* Performance */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.3 }}
            whileHover={{ y: -8 }}
            className="bg-white dark:bg-gray-800 rounded-xl shadow-md hover:shadow-xl transition-shadow duration-300 p-6"
          >
            <p className="text-gray-600 dark:text-gray-400 text-sm mb-2">Performance</p>
            <p className="text-4xl font-bold text-green-600 dark:text-green-400">
              {oee ? formatPercent(oee.performance) : '—'}
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-500 mt-2">
              Speed vs. Ideal
            </p>
          </motion.div>

          {/* Quality */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.4 }}
            whileHover={{ y: -8 }}
            className="bg-white dark:bg-gray-800 rounded-xl shadow-md hover:shadow-xl transition-shadow duration-300 p-6"
          >
            <p className="text-gray-600 dark:text-gray-400 text-sm mb-2">Quality</p>
            <p className="text-4xl font-bold text-amber-600 dark:text-amber-400">
              {oee ? formatPercent(oee.quality) : '—'}
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-500 mt-2">
              Good Parts Ratio
            </p>
          </motion.div>
        </div>

        {/* Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* OEE Components Bar Chart */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.5 }}
            className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-6"
          >
            <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
              OEE Components
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
              Breakdown of Overall Equipment Effectiveness
            </p>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={oeeComponentsData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="name" stroke="#9ca3af" />
                <YAxis domain={[0, 100]} stroke="#9ca3af" />
                <Tooltip
                  formatter={(value: number) => `${value.toFixed(1)}%`}
                  contentStyle={{
                    backgroundColor: '#1f2937',
                    border: '1px solid #374151',
                    borderRadius: '0.5rem',
                    color: '#f3f4f6',
                  }}
                />
                <Bar dataKey="value" />
              </BarChart>
            </ResponsiveContainer>
          </motion.div>

          {/* Downtime Analysis Bar Chart */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.6 }}
            className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-6"
          >
            <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
              Downtime Analysis
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
              Total downtime: {downtime ? `${downtime.total_downtime_hours.toFixed(1)} hours` : '—'}
              {downtime && downtime.major_events.length > 0 && ` (${downtime.major_events.length} major events > 2 hours)`}
            </p>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={downtimeData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="reason" stroke="#9ca3af" />
                <YAxis stroke="#9ca3af" />
                <Tooltip
                  formatter={(value: number) => `${value} hours`}
                  contentStyle={{
                    backgroundColor: '#1f2937',
                    border: '1px solid #374151',
                    borderRadius: '0.5rem',
                    color: '#f3f4f6',
                  }}
                />
                <Legend />
                <Bar dataKey="hours" fill="#ff7300" name="Downtime Hours" />
              </BarChart>
            </ResponsiveContainer>
          </motion.div>
        </div>

        {/* Scrap Rate Card with Production Stats */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.7 }}
          className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-6"
        >
          <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
            Production Quality
          </h3>
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-6">
            Parts production and scrap statistics
          </p>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="text-center p-4">
              <p className="text-4xl font-bold text-blue-600 dark:text-blue-400">
                {oee?.total_parts.toLocaleString() ?? '—'}
              </p>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">
                Total Parts
              </p>
            </div>
            <div className="text-center p-4">
              <p className="text-4xl font-bold text-green-600 dark:text-green-400">
                {oee?.good_parts.toLocaleString() ?? '—'}
              </p>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">
                Good Parts
              </p>
            </div>
            <div className="text-center p-4">
              <p className="text-4xl font-bold text-red-600 dark:text-red-400">
                {scrap?.total_scrap.toLocaleString() ?? '—'}
              </p>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">
                Scrap Parts
              </p>
            </div>
            <div className="text-center p-4">
              <p className="text-4xl font-bold text-amber-600 dark:text-amber-400">
                {scrap ? `${scrap.scrap_rate.toFixed(1)}%` : '—'}
              </p>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">
                Scrap Rate
              </p>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </div>
  );
};

export default DashboardPage;
