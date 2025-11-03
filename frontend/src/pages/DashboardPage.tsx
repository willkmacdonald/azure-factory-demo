import React from 'react';
import { Container, Typography, Box, Paper } from '@mui/material';

/**
 * DashboardPage - Main dashboard overview page
 *
 * This is a placeholder for PR12. Will be enhanced in PR13 with:
 * - Production metrics cards
 * - OEE (Overall Equipment Effectiveness) charts
 * - Scrap rate and quality metrics
 * - Real-time data visualization using Recharts
 */
const DashboardPage: React.FC = () => {
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

      <Paper
        sx={{
          p: 4,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: 400,
        }}
      >
        <Box sx={{ textAlign: 'center' }}>
          <Typography variant="h5" color="text.secondary" gutterBottom>
            Dashboard Content Coming Soon
          </Typography>
          <Typography variant="body1" color="text.secondary">
            PR13 will add metrics visualization, charts, and real-time data
          </Typography>
        </Box>
      </Paper>
    </Container>
  );
};

export default DashboardPage;
