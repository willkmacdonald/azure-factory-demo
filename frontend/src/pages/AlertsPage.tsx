import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  CircularProgress,
  Alert,
  Chip,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  type SelectChangeEvent,
  Stack,
} from '@mui/material';
import {
  Error as ErrorIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
} from '@mui/icons-material';
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
  const handleSeverityFilterChange = (event: SelectChangeEvent<string>): void => {
    setSeverityFilter(event.target.value);
  };

  // Handler for page change
  const handleChangePage = (_event: unknown, newPage: number): void => {
    setPage(newPage);
  };

  // Handler for rows per page change
  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>): void => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  // Helper function to get severity color
  const getSeverityColor = (severity: string): 'error' | 'warning' | 'info' => {
    switch (severity) {
      case 'High':
        return 'error';
      case 'Medium':
        return 'warning';
      case 'Low':
        return 'info';
      default:
        return 'info';
    }
  };

  // Helper function to get severity icon
  const getSeverityIcon = (severity: string): React.ReactElement => {
    switch (severity) {
      case 'High':
        return <ErrorIcon />;
      case 'Medium':
        return <WarningIcon />;
      case 'Low':
        return <InfoIcon />;
      default:
        return <InfoIcon />;
    }
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
            Alerts
          </Typography>
          <Typography variant="subtitle1" color="text.secondary">
            Quality issues and system alerts
          </Typography>
        </Box>
        <Alert severity="info">
          No production data available. Please generate data using the setup endpoint.
        </Alert>
      </Container>
    );
  }

  // Calculate pagination
  const paginatedIssues = filteredIssues.slice(
    page * rowsPerPage,
    page * rowsPerPage + rowsPerPage
  );

  // Main content
  return (
    <Container maxWidth="xl">
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Alerts
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          Quality issues and system alerts
        </Typography>
      </Box>

      {/* Summary Cards */}
      {qualityData && (
        <Stack direction="row" spacing={2} sx={{ mb: 3 }}>
          <Paper sx={{ p: 2, flex: 1 }}>
            <Typography variant="caption" color="text.secondary" display="block">
              Total Issues
            </Typography>
            <Typography variant="h4">{qualityData.total_issues}</Typography>
          </Paper>
          <Paper sx={{ p: 2, flex: 1 }}>
            <Typography variant="caption" color="text.secondary" display="block">
              Parts Affected
            </Typography>
            <Typography variant="h4">{qualityData.total_parts_affected.toLocaleString()}</Typography>
          </Paper>
          <Paper sx={{ p: 2, flex: 1 }}>
            <Typography variant="caption" color="text.secondary" display="block">
              High Severity
            </Typography>
            <Typography variant="h4" color="error.main">
              {qualityData.severity_breakdown.High || 0}
            </Typography>
          </Paper>
          <Paper sx={{ p: 2, flex: 1 }}>
            <Typography variant="caption" color="text.secondary" display="block">
              Medium Severity
            </Typography>
            <Typography variant="h4" color="warning.main">
              {qualityData.severity_breakdown.Medium || 0}
            </Typography>
          </Paper>
          <Paper sx={{ p: 2, flex: 1 }}>
            <Typography variant="caption" color="text.secondary" display="block">
              Low Severity
            </Typography>
            <Typography variant="h4" color="info.main">
              {qualityData.severity_breakdown.Low || 0}
            </Typography>
          </Paper>
        </Stack>
      )}

      {/* Filters */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Stack direction="row" spacing={2} alignItems="center">
          <FormControl size="small" sx={{ minWidth: 200 }}>
            <InputLabel id="severity-filter-label">Severity</InputLabel>
            <Select
              labelId="severity-filter-label"
              id="severity-filter"
              value={severityFilter}
              label="Severity"
              onChange={handleSeverityFilterChange}
            >
              <MenuItem value="all">All Severities</MenuItem>
              <MenuItem value="High">High</MenuItem>
              <MenuItem value="Medium">Medium</MenuItem>
              <MenuItem value="Low">Low</MenuItem>
            </Select>
          </FormControl>

          <Typography variant="body2" color="text.secondary">
            Showing {filteredIssues.length} of {qualityData?.total_issues || 0} issues
          </Typography>
        </Stack>
      </Paper>

      {/* Issues Table */}
      <Paper>
        <TableContainer>
          <Table sx={{ minWidth: 650 }} aria-label="quality issues table">
            <TableHead>
              <TableRow>
                <TableCell>Date</TableCell>
                <TableCell>Machine</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Description</TableCell>
                <TableCell align="center">Severity</TableCell>
                <TableCell align="right">Parts Affected</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {paginatedIssues.length > 0 ? (
                paginatedIssues.map((issue, index) => (
                  <TableRow
                    key={`${issue.date}-${issue.machine}-${index}`}
                    hover
                    sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
                  >
                    <TableCell>{issue.date}</TableCell>
                    <TableCell>{issue.machine}</TableCell>
                    <TableCell>{issue.type}</TableCell>
                    <TableCell>{issue.description}</TableCell>
                    <TableCell align="center">
                      <Chip
                        icon={getSeverityIcon(issue.severity)}
                        label={issue.severity}
                        color={getSeverityColor(issue.severity)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell align="right">{issue.parts_affected.toLocaleString()}</TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={6} align="center">
                    <Typography variant="body2" color="text.secondary" sx={{ py: 4 }}>
                      No issues found matching the current filters
                    </Typography>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>

        {/* Pagination */}
        <TablePagination
          rowsPerPageOptions={[5, 10, 25, 50]}
          component="div"
          count={filteredIssues.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      </Paper>
    </Container>
  );
};

export default AlertsPage;
