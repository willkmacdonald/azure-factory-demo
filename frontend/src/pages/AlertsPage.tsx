import React from 'react';
import { Container, Typography, Box, Paper } from '@mui/material';

/**
 * AlertsPage - System alerts and notifications page
 *
 * This is a placeholder for PR12. Will be enhanced in PR14 with:
 * - Alert list with severity indicators
 * - Filtering by machine, severity, and date
 * - Alert acknowledgment and resolution
 * - Alert history and trends
 */
const AlertsPage: React.FC = () => {
  return (
    <Container maxWidth="xl">
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Alerts
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          System alerts and notifications
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
            Alerts View Coming Soon
          </Typography>
          <Typography variant="body1" color="text.secondary">
            PR14 will add alert list, filtering, and management
          </Typography>
        </Box>
      </Paper>
    </Container>
  );
};

export default AlertsPage;
