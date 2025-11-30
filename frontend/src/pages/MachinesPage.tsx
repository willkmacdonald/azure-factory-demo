import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  CheckCircle,
  AlertTriangle,
  XCircle,
  Settings,
  Loader2,
  AlertCircle,
  Info,
} from 'lucide-react';
import { apiService, getErrorMessage } from '../api/client';
import type { MachineInfo, OEEMetrics, StatsResponse } from '../types/api';

/**
 * Progress bar color classes based on status
 */
interface ProgressBarColors {
  bg: string;
  fill: string;
}

/**
 * MachinesPage Component
 *
 * Displays machine status cards with real-time performance metrics.
 * Shows OEE, status indicators, and machine details in a grid layout.
 */
const MachinesPage: React.FC = () => {
  // State for machines list
  const [machines, setMachines] = useState<MachineInfo[]>([]);
  // State for OEE data per machine
  const [oeeData, setOeeData] = useState<Record<string, OEEMetrics>>({});
  // State for date range
  const [stats, setStats] = useState<StatsResponse | null>(null);
  // Loading and error states
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch machines and OEE data on mount
  useEffect(() => {
    const fetchMachineData = async (): Promise<void> => {
      try {
        setLoading(true);
        setError(null);

        // Fetch stats first to get date range
        const statsResponse = await apiService.getStats();
        setStats(statsResponse);

        // Fetch machines list
        const machinesResponse = await apiService.getMachines();
        setMachines(machinesResponse);

        // If data exists, fetch OEE for each machine
        if (statsResponse.exists && statsResponse.start_date && statsResponse.end_date) {
          // Fetch OEE for each machine in parallel
          const oeePromises = machinesResponse.map(async (machine) => {
            try {
              const oee = await apiService.getOEE({
                start_date: statsResponse.start_date,
                end_date: statsResponse.end_date,
                machine: machine.name,
              });
              return { machineName: machine.name, oee };
            } catch (err) {
              console.error(`Failed to fetch OEE for ${machine.name}:`, err);
              return null;
            }
          });

          const oeeResults = await Promise.all(oeePromises);

          // Build OEE data map
          const oeeMap: Record<string, OEEMetrics> = {};
          oeeResults.forEach((result) => {
            if (result) {
              oeeMap[result.machineName] = result.oee;
            }
          });
          setOeeData(oeeMap);
        }
      } catch (err) {
        setError(getErrorMessage(err));
        console.error('Failed to fetch machine data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchMachineData();
  }, []);

  // Helper function to determine machine status based on OEE
  const getMachineStatus = (oee?: OEEMetrics): 'operational' | 'warning' | 'error' | 'unknown' => {
    if (!oee) return 'unknown';

    const oeePercent = oee.oee * 100;

    if (oeePercent >= 75) return 'operational';
    if (oeePercent >= 50) return 'warning';
    return 'error';
  };

  // Helper function to get status badge styles
  const getStatusBadgeStyles = (status: string): string => {
    switch (status) {
      case 'operational':
        return 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300 border-green-200 dark:border-green-800';
      case 'warning':
        return 'bg-amber-100 dark:bg-amber-900/30 text-amber-800 dark:text-amber-300 border-amber-200 dark:border-amber-800';
      case 'error':
        return 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300 border-red-200 dark:border-red-800';
      default:
        return 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-300 border-gray-200 dark:border-gray-600';
    }
  };

  // Helper function to get progress bar colors
  const getProgressColors = (status: string): ProgressBarColors => {
    switch (status) {
      case 'operational':
        return { bg: 'bg-green-200 dark:bg-green-900/50', fill: 'bg-green-500 dark:bg-green-400' };
      case 'warning':
        return { bg: 'bg-amber-200 dark:bg-amber-900/50', fill: 'bg-amber-500 dark:bg-amber-400' };
      case 'error':
        return { bg: 'bg-red-200 dark:bg-red-900/50', fill: 'bg-red-500 dark:bg-red-400' };
      default:
        return { bg: 'bg-gray-200 dark:bg-gray-700', fill: 'bg-gray-400 dark:bg-gray-500' };
    }
  };

  // Helper function to get status icon
  const getStatusIcon = (status: string): React.ReactElement => {
    switch (status) {
      case 'operational':
        return <CheckCircle className="w-4 h-4" />;
      case 'warning':
        return <AlertTriangle className="w-4 h-4" />;
      case 'error':
        return <XCircle className="w-4 h-4" />;
      default:
        return <Settings className="w-4 h-4" />;
    }
  };

  // Helper function to format percentage
  const formatPercent = (value: number): string => {
    return `${(value * 100).toFixed(1)}%`;
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
              Machines
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Monitor machine status and performance
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

  // Main content
  return (
    <div className="p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            Machines
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Real-time machine status and performance monitoring
          </p>
        </div>

        {/* Machines Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {machines.map((machine, index) => {
            const oee = oeeData[machine.name];
            const status = getMachineStatus(oee);
            const progressColors = getProgressColors(status);

            return (
              <motion.div
                key={machine.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-6"
              >
                {/* Machine Name and Status */}
                <div className="flex justify-between items-center mb-4">
                  <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                    {machine.name}
                  </h2>
                  <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border ${getStatusBadgeStyles(status)}`}>
                    {getStatusIcon(status)}
                    {status.toUpperCase()}
                  </span>
                </div>

                {/* Machine Type */}
                <p className="text-sm text-gray-500 dark:text-gray-400 mb-1">
                  {machine.type}
                </p>

                {/* Ideal Cycle Time */}
                <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
                  Ideal Cycle: {machine.ideal_cycle_time}s
                </p>

                {/* OEE Metrics */}
                {oee ? (
                  <>
                    {/* Overall OEE */}
                    <div className="mb-4">
                      <div className="flex justify-between mb-1">
                        <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                          OEE
                        </span>
                        <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                          {formatPercent(oee.oee)}
                        </span>
                      </div>
                      <div className={`w-full h-2 rounded-full ${progressColors.bg}`}>
                        <div
                          className={`h-full rounded-full transition-all duration-500 ${progressColors.fill}`}
                          style={{ width: `${Math.min(oee.oee * 100, 100)}%` }}
                        />
                      </div>
                    </div>

                    {/* Availability */}
                    <div className="mb-2">
                      <div className="flex justify-between mb-1">
                        <span className="text-xs text-gray-500 dark:text-gray-400">
                          Availability
                        </span>
                        <span className="text-xs text-gray-500 dark:text-gray-400">
                          {formatPercent(oee.availability)}
                        </span>
                      </div>
                      <div className="w-full h-1 rounded-full bg-gray-200 dark:bg-gray-700">
                        <div
                          className="h-full rounded-full bg-blue-500 dark:bg-blue-400 transition-all duration-500"
                          style={{ width: `${Math.min(oee.availability * 100, 100)}%` }}
                        />
                      </div>
                    </div>

                    {/* Performance */}
                    <div className="mb-2">
                      <div className="flex justify-between mb-1">
                        <span className="text-xs text-gray-500 dark:text-gray-400">
                          Performance
                        </span>
                        <span className="text-xs text-gray-500 dark:text-gray-400">
                          {formatPercent(oee.performance)}
                        </span>
                      </div>
                      <div className="w-full h-1 rounded-full bg-gray-200 dark:bg-gray-700">
                        <div
                          className="h-full rounded-full bg-blue-500 dark:bg-blue-400 transition-all duration-500"
                          style={{ width: `${Math.min(oee.performance * 100, 100)}%` }}
                        />
                      </div>
                    </div>

                    {/* Quality */}
                    <div className="mb-4">
                      <div className="flex justify-between mb-1">
                        <span className="text-xs text-gray-500 dark:text-gray-400">
                          Quality
                        </span>
                        <span className="text-xs text-gray-500 dark:text-gray-400">
                          {formatPercent(oee.quality)}
                        </span>
                      </div>
                      <div className="w-full h-1 rounded-full bg-gray-200 dark:bg-gray-700">
                        <div
                          className="h-full rounded-full bg-blue-500 dark:bg-blue-400 transition-all duration-500"
                          style={{ width: `${Math.min(oee.quality * 100, 100)}%` }}
                        />
                      </div>
                    </div>

                    {/* Production Stats */}
                    <div className="flex justify-between pt-4 border-t border-gray-200 dark:border-gray-700">
                      <div>
                        <p className="text-xs text-gray-500 dark:text-gray-400">
                          Total Parts
                        </p>
                        <p className="text-sm font-medium text-gray-900 dark:text-white">
                          {oee.total_parts.toLocaleString()}
                        </p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-500 dark:text-gray-400">
                          Good Parts
                        </p>
                        <p className="text-sm font-medium text-green-600 dark:text-green-400">
                          {oee.good_parts.toLocaleString()}
                        </p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-500 dark:text-gray-400">
                          Scrap
                        </p>
                        <p className="text-sm font-medium text-red-600 dark:text-red-400">
                          {oee.scrap_parts.toLocaleString()}
                        </p>
                      </div>
                    </div>
                  </>
                ) : (
                  <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-3 mt-2 flex items-start gap-2">
                    <Info className="w-4 h-4 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
                    <p className="text-sm text-blue-800 dark:text-blue-200">
                      No data available
                    </p>
                  </div>
                )}
              </motion.div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default MachinesPage;
