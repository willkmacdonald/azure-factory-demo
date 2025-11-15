import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  CircularProgress,
  Alert,
  Chip,
  LinearProgress,
} from '@mui/material';
import {
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material';
import { apiService, getErrorMessage } from '../api/client';
import type { MachineInfo, OEEMetrics, StatsResponse } from '../types/api';

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

  // Helper function to get status color for Chip
  const getStatusColorChip = (status: string): 'success' | 'warning' | 'error' | 'default' => {
    switch (status) {
      case 'operational':
        return 'success';
      case 'warning':
        return 'warning';
      case 'error':
        return 'error';
      default:
        return 'default';
    }
  };

  // Helper function to get status color for LinearProgress
  const getStatusColorProgress = (status: string): 'success' | 'warning' | 'error' | 'inherit' => {
    switch (status) {
      case 'operational':
        return 'success';
      case 'warning':
        return 'warning';
      case 'error':
        return 'error';
      default:
        return 'inherit';
    }
  };

  // Helper function to get status icon
  const getStatusIcon = (status: string): React.ReactElement => {
    switch (status) {
      case 'operational':
        return <CheckCircleIcon />;
      case 'warning':
        return <WarningIcon />;
      case 'error':
        return <ErrorIcon />;
      default:
        return <SettingsIcon />;
    }
  };

  // Helper function to format percentage
  const formatPercent = (value: number): string => {
    return `${(value * 100).toFixed(1)}%`;
  };

  // Loading state
  if (loading) {
    return (
      <Container maxWidth="xl">
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 400 }}>
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  // Error state
  if (error) {
    return (
      <Container maxWidth="xl">
        <Box sx={{ mt: 4 }}>
          <Alert severity="error">{error}</Alert>
        </Box>
      </Container>
    );
  }

  // Empty state
  if (!stats?.exists) {
    return (
      <Container maxWidth="xl">
        <Box sx={{ mb: 4 }}>
          <Typography variant="h4" component="h1" gutterBottom>
            Machines
          </Typography>
          <Typography variant="subtitle1" color="text.secondary">
            Monitor machine status and performance
          </Typography>
        </Box>
        <Alert severity="info">
          No production data available. Please generate data using the setup endpoint.
        </Alert>
      </Container>
    );
  }

  // Main content
  return (
    <Container maxWidth="xl">
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Machines
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          Real-time machine status and performance monitoring
        </Typography>
      </Box>

      {/* Machines Grid */}
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: {
            xs: '1fr',
            sm: 'repeat(2, 1fr)',
            md: 'repeat(3, 1fr)',
          },
          gap: 3,
        }}
      >
        {machines.map((machine) => {
          const oee = oeeData[machine.name];
          const status = getMachineStatus(oee);
          const statusColorChip = getStatusColorChip(status);
          const statusColorProgress = getStatusColorProgress(status);
          const statusIcon = getStatusIcon(status);

          return (
            <Box key={machine.id}>
              <Card>
                <CardContent>
                  {/* Machine Name and Status */}
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                    <Typography variant="h6" component="div">
                      {machine.name}
                    </Typography>
                    <Chip
                      icon={statusIcon}
                      label={status.toUpperCase()}
                      color={statusColorChip}
                      size="small"
                    />
                  </Box>

                  {/* Machine Type */}
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    {machine.type}
                  </Typography>

                  {/* Ideal Cycle Time */}
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    Ideal Cycle: {machine.ideal_cycle_time}s
                  </Typography>

                  {/* OEE Metrics */}
                  {oee ? (
                    <>
                      {/* Overall OEE */}
                      <Box sx={{ mb: 2 }}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                          <Typography variant="body2" fontWeight="medium">
                            OEE
                          </Typography>
                          <Typography variant="body2" fontWeight="medium">
                            {formatPercent(oee.oee)}
                          </Typography>
                        </Box>
                        <LinearProgress
                          variant="determinate"
                          value={oee.oee * 100}
                          color={statusColorProgress}
                          sx={{ height: 8, borderRadius: 4 }}
                        />
                      </Box>

                      {/* Availability */}
                      <Box sx={{ mb: 1 }}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                          <Typography variant="caption" color="text.secondary">
                            Availability
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {formatPercent(oee.availability)}
                          </Typography>
                        </Box>
                        <LinearProgress
                          variant="determinate"
                          value={oee.availability * 100}
                          sx={{ height: 4, borderRadius: 2 }}
                        />
                      </Box>

                      {/* Performance */}
                      <Box sx={{ mb: 1 }}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                          <Typography variant="caption" color="text.secondary">
                            Performance
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {formatPercent(oee.performance)}
                          </Typography>
                        </Box>
                        <LinearProgress
                          variant="determinate"
                          value={oee.performance * 100}
                          sx={{ height: 4, borderRadius: 2 }}
                        />
                      </Box>

                      {/* Quality */}
                      <Box sx={{ mb: 2 }}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                          <Typography variant="caption" color="text.secondary">
                            Quality
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {formatPercent(oee.quality)}
                          </Typography>
                        </Box>
                        <LinearProgress
                          variant="determinate"
                          value={oee.quality * 100}
                          sx={{ height: 4, borderRadius: 2 }}
                        />
                      </Box>

                      {/* Production Stats */}
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', pt: 1, borderTop: 1, borderColor: 'divider' }}>
                        <Box>
                          <Typography variant="caption" color="text.secondary" display="block">
                            Total Parts
                          </Typography>
                          <Typography variant="body2" fontWeight="medium">
                            {oee.total_parts.toLocaleString()}
                          </Typography>
                        </Box>
                        <Box>
                          <Typography variant="caption" color="text.secondary" display="block">
                            Good Parts
                          </Typography>
                          <Typography variant="body2" fontWeight="medium" color="success.main">
                            {oee.good_parts.toLocaleString()}
                          </Typography>
                        </Box>
                        <Box>
                          <Typography variant="caption" color="text.secondary" display="block">
                            Scrap
                          </Typography>
                          <Typography variant="body2" fontWeight="medium" color="error.main">
                            {oee.scrap_parts.toLocaleString()}
                          </Typography>
                        </Box>
                      </Box>
                    </>
                  ) : (
                    <Alert severity="info" sx={{ mt: 2 }}>
                      No data available
                    </Alert>
                  )}
                </CardContent>
              </Card>
            </Box>
          );
        })}
      </Box>
    </Container>
  );
};

export default MachinesPage;
