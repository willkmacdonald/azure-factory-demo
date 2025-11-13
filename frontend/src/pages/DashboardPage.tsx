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
} from '@mui/material';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { apiService, getErrorMessage } from '../services/api';
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
  // State for metrics data
  const [oee, setOee] = useState<OEEMetrics | null>(null);
  const [scrap, setScrap] = useState<ScrapMetrics | null>(null);
  const [downtime, setDowntime] = useState<DowntimeAnalysis | null>(null);
  const [stats, setStats] = useState<StatsResponse | null>(null);

  // Loading and error states
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

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
        <Alert severity="info">
          No production data available. Please generate data using the setup endpoint.
        </Alert>
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
        <Grid item xs={12} sm={6} md={3}>
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
        <Grid item xs={12} sm={6} md={3}>
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
        <Grid item xs={12} sm={6} md={3}>
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
        <Grid item xs={12} sm={6} md={3}>
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
        <Grid item xs={12} md={6}>
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

        {/* Scrap Rate Card with Production Stats */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Production Quality
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Parts production and scrap statistics
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <Box sx={{ textAlign: 'center', p: 2 }}>
                  <Typography variant="h4" color="primary">
                    {oee?.total_parts.toLocaleString() ?? '—'}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Parts
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={6}>
                <Box sx={{ textAlign: 'center', p: 2 }}>
                  <Typography variant="h4" color="success.main">
                    {oee?.good_parts.toLocaleString() ?? '—'}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Good Parts
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={6}>
                <Box sx={{ textAlign: 'center', p: 2 }}>
                  <Typography variant="h4" color="error.main">
                    {scrap?.total_scrap.toLocaleString() ?? '—'}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Scrap Parts
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={6}>
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

        {/* Downtime Analysis Bar Chart */}
        <Grid item xs={12}>
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
      </Grid>
    </Container>
  );
};

export default DashboardPage;
