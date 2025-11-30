import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  XCircle,
  AlertTriangle,
  Info,
  Loader2,
  AlertCircle,
  ChevronLeft,
  ChevronRight,
  Filter,
} from 'lucide-react';
import { apiService, getErrorMessage } from '../api/client';
import type { QualityIssues, QualityIssue, StatsResponse } from '../types/api';

/**
 * AlertsPage Component
 *
 * Displays quality issues (alerts) in a filterable table with severity badges.
 * Allows filtering by severity level and pagination for large datasets.
 */
const AlertsPage: React.FC = () => {
  // State for quality issues data
  const [qualityData, setQualityData] = useState<QualityIssues | null>(null);
  // State for filtered issues
  const [filteredIssues, setFilteredIssues] = useState<QualityIssue[]>([]);
  // State for date range
  const [stats, setStats] = useState<StatsResponse | null>(null);
  // Filter states
  const [severityFilter, setSeverityFilter] = useState<string>('all');
  // Pagination states
  const [page, setPage] = useState<number>(0);
  const [rowsPerPage, setRowsPerPage] = useState<number>(10);
  // Loading and error states
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch quality issues on mount
  useEffect(() => {
    const fetchQualityData = async (): Promise<void> => {
      try {
        setLoading(true);
        setError(null);

        // Fetch stats first to get date range
        const statsResponse = await apiService.getStats();
        setStats(statsResponse);

        // If data exists, fetch quality issues
        if (statsResponse.exists && statsResponse.start_date && statsResponse.end_date) {
          const qualityResponse = await apiService.getQuality({
            start_date: statsResponse.start_date,
            end_date: statsResponse.end_date,
          });
          setQualityData(qualityResponse);
          setFilteredIssues(qualityResponse.issues);
        }
      } catch (err) {
        setError(getErrorMessage(err));
        console.error('Failed to fetch quality data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchQualityData();
  }, []);

  // Apply filters when severity filter changes
  useEffect(() => {
    if (!qualityData) return;

    let filtered = [...qualityData.issues];

    // Filter by severity
    if (severityFilter !== 'all') {
      filtered = filtered.filter((issue) => issue.severity === severityFilter);
    }

    setFilteredIssues(filtered);
    setPage(0); // Reset to first page when filters change
  }, [severityFilter, qualityData]);

  // Handler for severity filter change
  const handleSeverityFilterChange = (event: React.ChangeEvent<HTMLSelectElement>): void => {
    setSeverityFilter(event.target.value);
  };

  // Handler for page change
  const handleChangePage = (newPage: number): void => {
    setPage(newPage);
  };

  // Handler for rows per page change
  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLSelectElement>): void => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  // Helper function to get severity badge styles
  const getSeverityBadgeStyles = (severity: string): string => {
    switch (severity) {
      case 'High':
        return 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300 border-red-200 dark:border-red-800';
      case 'Medium':
        return 'bg-amber-100 dark:bg-amber-900/30 text-amber-800 dark:text-amber-300 border-amber-200 dark:border-amber-800';
      case 'Low':
        return 'bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300 border-blue-200 dark:border-blue-800';
      default:
        return 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-300 border-gray-200 dark:border-gray-600';
    }
  };

  // Helper function to get severity icon
  const getSeverityIcon = (severity: string): React.ReactElement => {
    switch (severity) {
      case 'High':
        return <XCircle className="w-4 h-4" />;
      case 'Medium':
        return <AlertTriangle className="w-4 h-4" />;
      case 'Low':
        return <Info className="w-4 h-4" />;
      default:
        return <Info className="w-4 h-4" />;
    }
  };

  // Helper function to get root cause badge styles
  const getRootCauseBadgeStyles = (rootCause: string): string => {
    if (rootCause === 'supplier_quality') {
      return 'bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-300 border-red-200 dark:border-red-700';
    }
    return 'bg-amber-50 dark:bg-amber-900/20 text-amber-700 dark:text-amber-300 border-amber-200 dark:border-amber-700';
  };

  // Loading state
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

  // Error state
  if (error) {
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

  // Empty state
  if (!stats?.exists) {
    return (
      <div className="p-8">
        <div className="max-w-7xl mx-auto">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
              Alerts
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Quality issues and system alerts
            </p>
          </div>
          <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4 flex items-start gap-3">
            <Info className="w-5 h-5 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
            <p className="text-blue-800 dark:text-blue-200">
              No production data available. Please generate data using the setup endpoint.
            </p>
          </div>
        </div>
      </div>
    );
  }

  // Calculate pagination
  const paginatedIssues = filteredIssues.slice(
    page * rowsPerPage,
    page * rowsPerPage + rowsPerPage
  );
  const totalPages = Math.ceil(filteredIssues.length / rowsPerPage);

  // Main content
  return (
    <div className="p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            Alerts
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Quality issues and system alerts
          </p>
        </div>

        {/* Summary Cards */}
        {qualityData && (
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4 mb-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-4"
            >
              <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">Total Issues</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {qualityData.total_issues}
              </p>
            </motion.div>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.15 }}
              className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-4"
            >
              <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">Parts Affected</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {qualityData.total_parts_affected.toLocaleString()}
              </p>
            </motion.div>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-4"
            >
              <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">High Severity</p>
              <p className="text-2xl font-bold text-red-600 dark:text-red-400">
                {qualityData.severity_breakdown?.High ?? 0}
              </p>
            </motion.div>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.25 }}
              className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-4"
            >
              <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">Medium Severity</p>
              <p className="text-2xl font-bold text-amber-600 dark:text-amber-400">
                {qualityData.severity_breakdown?.Medium ?? 0}
              </p>
            </motion.div>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-4"
            >
              <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">Low Severity</p>
              <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                {qualityData.severity_breakdown?.Low ?? 0}
              </p>
            </motion.div>
          </div>
        )}

        {/* Filters */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.35 }}
          className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-4 mb-6"
        >
          <div className="flex flex-wrap items-center gap-4">
            <div className="flex items-center gap-2">
              <Filter className="w-4 h-4 text-gray-500 dark:text-gray-400" />
              <label htmlFor="severity-filter" className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Severity:
              </label>
              <select
                id="severity-filter"
                value={severityFilter}
                onChange={handleSeverityFilterChange}
                className="px-3 py-1.5 text-sm bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="all">All Severities</option>
                <option value="High">High</option>
                <option value="Medium">Medium</option>
                <option value="Low">Low</option>
              </select>
            </div>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Showing {filteredIssues.length} of {qualityData?.total_issues || 0} issues
            </p>
          </div>
        </motion.div>

        {/* Issues Table */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-white dark:bg-gray-800 rounded-xl shadow-md overflow-hidden"
        >
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead className="bg-gray-50 dark:bg-gray-900/50">
                <tr>
                  <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Date
                  </th>
                  <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Machine
                  </th>
                  <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Type
                  </th>
                  <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Description
                  </th>
                  <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Material/Lot
                  </th>
                  <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Supplier
                  </th>
                  <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Root Cause
                  </th>
                  <th scope="col" className="px-4 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Severity
                  </th>
                  <th scope="col" className="px-4 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Parts
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                {paginatedIssues.length > 0 ? (
                  paginatedIssues.map((issue, index) => (
                    <tr
                      key={`${issue.date}-${issue.machine}-${index}`}
                      className="hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
                    >
                      <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                        {issue.date}
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                        {issue.machine}
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                        {issue.type}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-900 dark:text-gray-100 max-w-xs truncate">
                        {issue.description}
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap text-sm">
                        {issue.material_id && issue.lot_number ? (
                          <div>
                            <p className="font-medium text-gray-900 dark:text-gray-100">
                              {issue.material_id}
                            </p>
                            <p className="text-xs text-gray-500 dark:text-gray-400">
                              Lot: {issue.lot_number}
                            </p>
                          </div>
                        ) : (
                          <span className="text-gray-400 dark:text-gray-500">—</span>
                        )}
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap text-sm">
                        {issue.supplier_name ? (
                          <div>
                            <p className="font-medium text-gray-900 dark:text-gray-100">
                              {issue.supplier_name}
                            </p>
                            <p className="text-xs text-gray-500 dark:text-gray-400">
                              {issue.supplier_id}
                            </p>
                          </div>
                        ) : (
                          <span className="text-gray-400 dark:text-gray-500">—</span>
                        )}
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap text-sm">
                        {issue.root_cause && issue.root_cause !== 'unknown' ? (
                          <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium border ${getRootCauseBadgeStyles(issue.root_cause)}`}>
                            {issue.root_cause.replace('_', ' ')}
                          </span>
                        ) : (
                          <span className="text-gray-400 dark:text-gray-500">—</span>
                        )}
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap text-center">
                        <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium border ${getSeverityBadgeStyles(issue.severity)}`}>
                          {getSeverityIcon(issue.severity)}
                          {issue.severity}
                        </span>
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap text-sm text-right text-gray-900 dark:text-gray-100">
                        {issue.parts_affected.toLocaleString()}
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={9} className="px-4 py-8 text-center">
                      <p className="text-gray-500 dark:text-gray-400">
                        No issues found matching the current filters
                      </p>
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          <div className="px-4 py-3 border-t border-gray-200 dark:border-gray-700 flex flex-wrap items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <label htmlFor="rows-per-page" className="text-sm text-gray-500 dark:text-gray-400">
                Rows per page:
              </label>
              <select
                id="rows-per-page"
                value={rowsPerPage}
                onChange={handleChangeRowsPerPage}
                className="px-2 py-1 text-sm bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
              >
                <option value={5}>5</option>
                <option value={10}>10</option>
                <option value={25}>25</option>
                <option value={50}>50</option>
              </select>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-sm text-gray-500 dark:text-gray-400">
                {page * rowsPerPage + 1}-{Math.min((page + 1) * rowsPerPage, filteredIssues.length)} of {filteredIssues.length}
              </span>
              <div className="flex gap-1">
                <button
                  onClick={() => handleChangePage(page - 1)}
                  disabled={page === 0}
                  className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  aria-label="Previous page"
                >
                  <ChevronLeft className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                </button>
                <button
                  onClick={() => handleChangePage(page + 1)}
                  disabled={page >= totalPages - 1}
                  className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  aria-label="Next page"
                >
                  <ChevronRight className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                </button>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default AlertsPage;
