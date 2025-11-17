import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
  Grid,
  Card,
  CardContent,
  CircularProgress,
  Alert,
  Button,
  Snackbar,
} from '@mui/material';
import { Add as AddIcon, Login as LoginIcon } from '@mui/icons-material';
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
      <Container maxWidth="xl">
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 400 }}>
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  /**
   * Render error state
   */
  if (error) {
    return (
      <Container maxWidth="xl">
        <Box sx={{ mt: 4 }}>
          <Alert severity="error">{error}</Alert>
        </Box>
      </Container>
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
      <Container maxWidth="xl">
        <Box sx={{ mb: 4 }}>
          <Typography variant="h4" component="h1" gutterBottom>
            Dashboard
          </Typography>
          <Typography variant="subtitle1" color="text.secondary">
            Production metrics and performance overview
          </Typography>
        </Box>
        <Alert severity="info" sx={{ mb: 3 }}>
          No production data available.
          {azureAdConfigured && !isAuthenticated
            ? ' Please sign in with your Microsoft account to generate demo data.'
            : ' Click the button below to generate synthetic production data for testing.'}
        </Alert>
        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
          {/* Sign-in button (only if Azure AD is configured and user is not authenticated) */}
          {showSignInButton && (
            <Button
              variant="outlined"
              color="primary"
              startIcon={<LoginIcon />}
              onClick={handleSignIn}
              size="large"
            >
              Sign in with Microsoft
            </Button>
          )}

          {/* Generate Data button (only if not Azure AD or user is authenticated) */}
          {showGenerateButton && (
            <Button
              variant="contained"
              color="primary"
              startIcon={<AddIcon />}
              onClick={handleGenerateData}
              disabled={generating}
              size="large"
            >
              {generating ? 'Generating Data...' : 'Generate Demo Data (30 days)'}
            </Button>
          )}
        </Box>

        {/* Success message snackbar */}
        <Snackbar
          open={!!successMessage}
          autoHideDuration={6000}
          onClose={() => setSuccessMessage(null)}
          message={successMessage}
        />
      </Container>
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

  return (
    <Container maxWidth="xl">
      {/* Page Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Dashboard
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          Production metrics and performance overview
        </Typography>
        {stats && (
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            Data from {stats.start_date} to {stats.end_date} ({stats.total_days} days, {stats.total_machines} machines)
          </Typography>
        )}
      </Box>

      {/* Key Metrics Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {/* Overall Equipment Effectiveness (OEE) */}
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom variant="body2">
                Overall OEE
              </Typography>
              <Typography variant="h3" component="div">
                {oee ? formatPercent(oee.oee) : '—'}
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                Equipment Effectiveness
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Availability */}
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom variant="body2">
                Availability
              </Typography>
              <Typography variant="h3" component="div">
                {oee ? formatPercent(oee.availability) : '—'}
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                Uptime vs. Downtime
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Performance */}
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom variant="body2">
                Performance
              </Typography>
              <Typography variant="h3" component="div">
                {oee ? formatPercent(oee.performance) : '—'}
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                Speed vs. Ideal
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Quality */}
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom variant="body2">
                Quality
              </Typography>
              <Typography variant="h3" component="div">
                {oee ? formatPercent(oee.quality) : '—'}
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                Good Parts Ratio
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Charts Grid */}
      <Grid container spacing={3}>
        {/* OEE Components Bar Chart */}
        <Grid size={{ xs: 12, md: 6 }}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              OEE Components
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Breakdown of Overall Equipment Effectiveness
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={oeeComponentsData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis domain={[0, 100]} />
                <Tooltip formatter={(value: number) => `${value.toFixed(1)}%`} />
                <Bar dataKey="value" fill="#8884d8" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Downtime Analysis Bar Chart */}
        <Grid size={{ xs: 12, md: 6 }}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Downtime Analysis
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Total downtime: {downtime ? `${downtime.total_downtime_hours.toFixed(1)} hours` : '—'}
              {downtime && downtime.major_events.length > 0 && ` (${downtime.major_events.length} major events > 2 hours)`}
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={downtimeData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="reason" />
                <YAxis label={{ value: 'Hours', angle: -90, position: 'insideLeft' }} />
                <Tooltip formatter={(value: number) => `${value} hours`} />
                <Legend />
                <Bar dataKey="hours" fill="#ff7300" name="Downtime Hours" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Scrap Rate Card with Production Stats */}
        <Grid size={{ xs: 12 }}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Production Quality
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Parts production and scrap statistics
            </Typography>
            <Grid container spacing={2}>
              <Grid size={{ xs: 6, sm: 3 }}>
                <Box sx={{ textAlign: 'center', p: 2 }}>
                  <Typography variant="h4" color="primary">
                    {oee?.total_parts.toLocaleString() ?? '—'}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Parts
                  </Typography>
                </Box>
              </Grid>
              <Grid size={{ xs: 6, sm: 3 }}>
                <Box sx={{ textAlign: 'center', p: 2 }}>
                  <Typography variant="h4" color="success.main">
                    {oee?.good_parts.toLocaleString() ?? '—'}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Good Parts
                  </Typography>
                </Box>
              </Grid>
              <Grid size={{ xs: 6, sm: 3 }}>
                <Box sx={{ textAlign: 'center', p: 2 }}>
                  <Typography variant="h4" color="error.main">
                    {scrap?.total_scrap.toLocaleString() ?? '—'}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Scrap Parts
                  </Typography>
                </Box>
              </Grid>
              <Grid size={{ xs: 6, sm: 3 }}>
                <Box sx={{ textAlign: 'center', p: 2 }}>
                  <Typography variant="h4" color="warning.main">
                    {scrap ? `${scrap.scrap_rate.toFixed(1)}%` : '—'}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Scrap Rate
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default DashboardPage;
