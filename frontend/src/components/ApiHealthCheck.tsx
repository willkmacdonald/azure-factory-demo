/**
 * API Health Check Component
 *
 * Simple component to verify API connectivity.
 * Displays connection status and provides manual refresh.
 */

import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  CircularProgress,
  Alert,
  Chip,
} from '@mui/material';
import { CheckCircle, Error, Refresh } from '@mui/icons-material';
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
    <Card sx={{ maxWidth: 600, margin: 'auto', mt: 4 }}>
      <CardContent>
        <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
          <Typography variant="h5" component="h2">
            API Health Check
          </Typography>
          <Button
            variant="outlined"
            size="small"
            startIcon={<Refresh />}
            onClick={refetch}
            disabled={loading}
          >
            Refresh
          </Button>
        </Box>

        {/* Loading State */}
        {loading && (
          <Box display="flex" alignItems="center" gap={2}>
            <CircularProgress size={24} />
            <Typography color="text.secondary">Checking API connection...</Typography>
          </Box>
        )}

        {/* Error State */}
        {!loading && error && (
          <Alert severity="error" icon={<Error />}>
            <Typography variant="subtitle2" fontWeight="bold">
              Connection Failed
            </Typography>
            <Typography variant="body2">{error}</Typography>
            <Typography variant="caption" display="block" mt={1}>
              Make sure the backend server is running on port 8000
            </Typography>
          </Alert>
        )}

        {/* Success State */}
        {!loading && !error && data && (
          <Box>
            <Alert severity="success" icon={<CheckCircle />}>
              <Typography variant="subtitle2" fontWeight="bold">
                API Connected
              </Typography>
              <Typography variant="body2">
                Backend is healthy and responding normally
              </Typography>
            </Alert>

            <Box mt={2} display="flex" gap={1} flexWrap="wrap">
              <Chip label={`Status: ${data.status}`} color="success" size="small" />
              <Chip
                label={`URL: ${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}`}
                size="small"
              />
            </Box>
          </Box>
        )}

        {/* API Information */}
        <Box mt={3} p={2} bgcolor="grey.50" borderRadius={1}>
          <Typography variant="caption" component="div" color="text.secondary" gutterBottom>
            <strong>Backend API Endpoints:</strong>
          </Typography>
          <Typography variant="caption" component="div" color="text.secondary">
            • GET /health - Health check
          </Typography>
          <Typography variant="caption" component="div" color="text.secondary">
            • GET /api/metrics/oee - OEE metrics
          </Typography>
          <Typography variant="caption" component="div" color="text.secondary">
            • GET /api/metrics/scrap - Scrap metrics
          </Typography>
          <Typography variant="caption" component="div" color="text.secondary">
            • GET /api/metrics/quality - Quality issues
          </Typography>
          <Typography variant="caption" component="div" color="text.secondary">
            • GET /api/metrics/downtime - Downtime analysis
          </Typography>
          <Typography variant="caption" component="div" color="text.secondary">
            • POST /api/chat - Chat with AI
          </Typography>
          <Typography variant="caption" component="div" color="text.secondary">
            • POST /api/setup - Generate data
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
};

export default ApiHealthCheck;
