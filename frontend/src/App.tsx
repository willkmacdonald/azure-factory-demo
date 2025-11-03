import { useState } from 'react';
import { Box, Container, Paper, Typography } from '@mui/material';
import './App.css';

/**
 * Main Application Component for Factory Agent
 *
 * This is the initial PR11 setup with a basic layout structure.
 * Future PRs will add:
 * - PR12: Split-pane layout with Dashboard and Console panels
 * - PR13: Dashboard visualizations (OEE, charts, tables)
 * - PR14: Chat console with AI integration
 */
function App() {
  const [selectedMachine] = useState<string | undefined>();
  const [dateRange] = useState({
    startDate: '2024-10-01',
    endDate: '2024-10-31',
  });

  // Suppress unused variable warnings for future PRs
  // These will be used when filters are added in PR12
  void selectedMachine;

  return (
    <Container maxWidth="xl" sx={{ height: '100vh', py: 2 }}>
      <Typography variant="h3" component="h1" gutterBottom>
        Factory Agent
      </Typography>
      <Typography variant="subtitle1" color="text.secondary" gutterBottom>
        AI-Powered Factory Operations Dashboard
      </Typography>

      <Box sx={{ display: 'flex', gap: 2, height: 'calc(100% - 100px)', mt: 2 }}>
        {/* Dashboard Panel (left) - Placeholder for PR12 */}
        <Paper sx={{ flex: 1, overflow: 'auto', p: 2 }}>
          <Typography variant="h5" gutterBottom>
            Dashboard Panel
          </Typography>
          <Typography color="text.secondary">
            Dashboard components will be added in PR12 and PR13.
            This will include OEE gauges, trend charts, downtime tables, and quality metrics.
          </Typography>
          <Box sx={{ mt: 2 }}>
            <Typography variant="body2">
              Selected Machine: {selectedMachine || 'All Machines'}
            </Typography>
            <Typography variant="body2">
              Date Range: {dateRange.startDate} to {dateRange.endDate}
            </Typography>
          </Box>
        </Paper>

        {/* Console Panel (right) - Placeholder for PR14 */}
        <Paper
          sx={{
            flex: 1,
            overflow: 'auto',
            p: 2,
            display: 'flex',
            flexDirection: 'column',
          }}
        >
          <Typography variant="h5" gutterBottom>
            AI Console Panel
          </Typography>
          <Typography color="text.secondary">
            Chat console will be added in PR14.
            This will include message history, input field, and AI-powered responses.
          </Typography>
        </Paper>
      </Box>
    </Container>
  );
}

export default App;
