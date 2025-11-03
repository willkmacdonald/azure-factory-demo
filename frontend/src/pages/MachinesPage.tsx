import React from 'react';
import { Container, Typography, Box, Paper } from '@mui/material';

/**
 * MachinesPage - Machine status and monitoring page
 *
 * This is a placeholder for PR12. Will be enhanced in PR14 with:
 * - Machine status cards with health indicators
 * - Real-time status updates
 * - Machine performance metrics
 * - Alert history for each machine
 */
const MachinesPage: React.FC = () => {
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
            Machine Status View Coming Soon
          </Typography>
          <Typography variant="body1" color="text.secondary">
            PR14 will add machine cards, status indicators, and alerts
          </Typography>
        </Box>
      </Paper>
    </Container>
  );
};

export default MachinesPage;
