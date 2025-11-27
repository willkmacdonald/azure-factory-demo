/**
 * MemoryPanel - Drawer panel displaying agent memory details
 *
 * Shows investigations, actions, and shift summary information.
 * Provides context for AI conversations and allows viewing
 * ongoing factory investigations.
 *
 * Features:
 * - Investigations list with status badges
 * - Actions log with impact indicators
 * - Shift summary section
 * - Loading and error states
 */

import React, { useState, useEffect } from 'react';
import {
  Drawer,
  Box,
  Typography,
  IconButton,
  Divider,
  List,
  ListItem,
  Chip,
  CircularProgress,
  Alert,
  Tabs,
  Tab,
  Stack,
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import SearchIcon from '@mui/icons-material/Search';
import BuildIcon from '@mui/icons-material/Build';
import SummarizeIcon from '@mui/icons-material/Summarize';
import { apiService } from '../api/client';
import type {
  Investigation,
  Action,
  InvestigationStatus,
  ShiftSummaryResponse,
} from '../types/api';

// ============================================================================
// Types
// ============================================================================

interface MemoryPanelProps {
  open: boolean;
  onClose: () => void;
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

// ============================================================================
// Helper Components
// ============================================================================

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index }) => (
  <Box
    role="tabpanel"
    hidden={value !== index}
    sx={{ p: 2, overflow: 'auto', height: 'calc(100% - 48px)' }}
  >
    {value === index && children}
  </Box>
);

/**
 * Get status chip color and label
 */
const getStatusChip = (status: InvestigationStatus): { color: 'error' | 'warning' | 'success' | 'default'; label: string } => {
  switch (status) {
    case 'open':
      return { color: 'error', label: 'Open' };
    case 'in_progress':
      return { color: 'warning', label: 'In Progress' };
    case 'resolved':
      return { color: 'success', label: 'Resolved' };
    case 'closed':
      return { color: 'default', label: 'Closed' };
    default:
      return { color: 'default', label: status };
  }
};

/**
 * Format timestamp to readable date
 */
const formatDate = (isoString: string): string => {
  const date = new Date(isoString);
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

// ============================================================================
// Main Component
// ============================================================================

const MemoryPanel: React.FC<MemoryPanelProps> = ({ open, onClose }) => {
  // State for tabs
  const [tabValue, setTabValue] = useState(0);

  // Data states
  const [investigations, setInvestigations] = useState<Investigation[]>([]);
  const [actions, setActions] = useState<Action[]>([]);
  const [shiftSummary, setShiftSummary] = useState<ShiftSummaryResponse | null>(null);

  // Loading and error states
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * Load memory data when panel opens
   */
  useEffect(() => {
    if (open) {
      loadMemoryData();
    }
  }, [open]);

  /**
   * Fetch all memory data
   */
  const loadMemoryData = async (): Promise<void> => {
    setLoading(true);
    setError(null);

    try {
      // Fetch all data in parallel
      const [investigationsRes, actionsRes, summaryRes] = await Promise.all([
        apiService.getInvestigations(),
        apiService.getActions(),
        apiService.getShiftSummary(),
      ]);

      setInvestigations(investigationsRes.investigations);
      setActions(actionsRes.actions);
      setShiftSummary(summaryRes);
    } catch (err) {
      console.error('[MemoryPanel] Failed to load memory data:', err);
      const message = err instanceof Error ? err.message : 'Unknown error';
      setError(`Unable to load agent memory: ${message}. Please try again.`);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Handle tab change
   */
  const handleTabChange = (_event: React.SyntheticEvent, newValue: number): void => {
    setTabValue(newValue);
  };

  return (
    <Drawer
      anchor="right"
      open={open}
      onClose={onClose}
      sx={{
        '& .MuiDrawer-paper': {
          width: { xs: '100%', sm: 400 },
          maxWidth: '100%',
        },
      }}
    >
      {/* Header */}
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          p: 2,
          borderBottom: 1,
          borderColor: 'divider',
        }}
      >
        <Typography variant="h6">Agent Memory</Typography>
        <IconButton onClick={onClose} size="small">
          <CloseIcon />
        </IconButton>
      </Box>

      {/* Loading State */}
      {loading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
          <CircularProgress />
        </Box>
      )}

      {/* Error State */}
      {error && (
        <Box sx={{ p: 2 }}>
          <Alert severity="error" onClose={() => setError(null)}>
            {error}
          </Alert>
        </Box>
      )}

      {/* Content */}
      {!loading && !error && (
        <Box sx={{ height: 'calc(100% - 64px)', display: 'flex', flexDirection: 'column' }}>
          {/* Tabs */}
          <Tabs
            value={tabValue}
            onChange={handleTabChange}
            variant="fullWidth"
            sx={{ borderBottom: 1, borderColor: 'divider' }}
          >
            <Tab
              icon={<SearchIcon />}
              label={`Investigations (${investigations.length})`}
              iconPosition="start"
              sx={{ minHeight: 48 }}
            />
            <Tab
              icon={<BuildIcon />}
              label={`Actions (${actions.length})`}
              iconPosition="start"
              sx={{ minHeight: 48 }}
            />
            <Tab
              icon={<SummarizeIcon />}
              label="Summary"
              iconPosition="start"
              sx={{ minHeight: 48 }}
            />
          </Tabs>

          {/* Investigations Tab */}
          <TabPanel value={tabValue} index={0}>
            {investigations.length === 0 ? (
              <Typography color="text.secondary" sx={{ textAlign: 'center', mt: 4 }}>
                No investigations yet. Start a conversation with the AI assistant to create one.
              </Typography>
            ) : (
              <List disablePadding>
                {investigations.map((inv) => {
                  const statusChip = getStatusChip(inv.status);
                  return (
                    <ListItem
                      key={inv.id}
                      sx={{
                        flexDirection: 'column',
                        alignItems: 'flex-start',
                        borderBottom: 1,
                        borderColor: 'divider',
                        py: 2,
                      }}
                    >
                      <Box sx={{ display: 'flex', width: '100%', justifyContent: 'space-between', mb: 1 }}>
                        <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
                          {inv.title}
                        </Typography>
                        <Chip
                          label={statusChip.label}
                          color={statusChip.color}
                          size="small"
                        />
                      </Box>
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                        {inv.initial_observation}
                      </Typography>
                      <Stack direction="row" spacing={1} sx={{ flexWrap: 'wrap', gap: 0.5 }}>
                        {inv.machine_id && (
                          <Chip label={inv.machine_id} size="small" variant="outlined" />
                        )}
                        {inv.supplier_id && (
                          <Chip label={inv.supplier_id} size="small" variant="outlined" />
                        )}
                        <Typography variant="caption" color="text.secondary">
                          Updated: {formatDate(inv.updated_at)}
                        </Typography>
                      </Stack>
                      {inv.findings.length > 0 && (
                        <Box sx={{ mt: 1 }}>
                          <Typography variant="caption" color="text.secondary">
                            Findings:
                          </Typography>
                          <ul style={{ margin: 0, paddingLeft: 16 }}>
                            {inv.findings.slice(0, 2).map((finding, idx) => (
                              <li key={idx}>
                                <Typography variant="caption">{finding}</Typography>
                              </li>
                            ))}
                            {inv.findings.length > 2 && (
                              <Typography variant="caption" color="text.secondary">
                                +{inv.findings.length - 2} more
                              </Typography>
                            )}
                          </ul>
                        </Box>
                      )}
                    </ListItem>
                  );
                })}
              </List>
            )}
          </TabPanel>

          {/* Actions Tab */}
          <TabPanel value={tabValue} index={1}>
            {actions.length === 0 ? (
              <Typography color="text.secondary" sx={{ textAlign: 'center', mt: 4 }}>
                No actions recorded yet. Ask the AI to track parameter changes or maintenance activities.
              </Typography>
            ) : (
              <List disablePadding>
                {actions.map((action) => (
                  <ListItem
                    key={action.id}
                    sx={{
                      flexDirection: 'column',
                      alignItems: 'flex-start',
                      borderBottom: 1,
                      borderColor: 'divider',
                      py: 2,
                    }}
                  >
                    <Box sx={{ display: 'flex', width: '100%', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
                        {action.description}
                      </Typography>
                      <Chip
                        label={action.action_type.replace('_', ' ')}
                        size="small"
                        color="primary"
                        variant="outlined"
                      />
                    </Box>
                    <Typography variant="body2" color="text.secondary">
                      Expected: {action.expected_impact}
                    </Typography>
                    {action.actual_impact && (
                      <Typography variant="body2" color="success.main" sx={{ mt: 0.5 }}>
                        Result: {action.actual_impact}
                      </Typography>
                    )}
                    <Stack direction="row" spacing={1} sx={{ mt: 1 }}>
                      {action.machine_id && (
                        <Chip label={action.machine_id} size="small" variant="outlined" />
                      )}
                      {action.follow_up_date && !action.actual_impact && (
                        <Chip
                          label={`Follow-up: ${action.follow_up_date}`}
                          size="small"
                          color="warning"
                        />
                      )}
                    </Stack>
                    <Typography variant="caption" color="text.secondary" sx={{ mt: 1 }}>
                      Created: {formatDate(action.created_at)}
                    </Typography>
                  </ListItem>
                ))}
              </List>
            )}
          </TabPanel>

          {/* Summary Tab */}
          <TabPanel value={tabValue} index={2}>
            {shiftSummary ? (
              <Box>
                <Typography variant="subtitle1" sx={{ fontWeight: 'bold', mb: 2 }}>
                  Shift Summary - {shiftSummary.date}
                </Typography>

                {/* Counts */}
                <Stack direction="row" spacing={2} sx={{ mb: 3 }}>
                  <Box sx={{ textAlign: 'center', flex: 1 }}>
                    <Typography variant="h4" color="warning.main">
                      {shiftSummary.counts.active_investigations}
                    </Typography>
                    <Typography variant="caption">Active</Typography>
                  </Box>
                  <Box sx={{ textAlign: 'center', flex: 1 }}>
                    <Typography variant="h4" color="primary.main">
                      {shiftSummary.counts.todays_actions}
                    </Typography>
                    <Typography variant="caption">Today&apos;s Actions</Typography>
                  </Box>
                  <Box sx={{ textAlign: 'center', flex: 1 }}>
                    <Typography variant="h4" color="error.main">
                      {shiftSummary.counts.pending_followups}
                    </Typography>
                    <Typography variant="caption">Follow-ups</Typography>
                  </Box>
                </Stack>

                <Divider sx={{ my: 2 }} />

                {/* Active Investigations */}
                {shiftSummary.active_investigations.length > 0 && (
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="subtitle2" sx={{ mb: 1 }}>
                      Active Investigations
                    </Typography>
                    {shiftSummary.active_investigations.map((inv) => (
                      <Box key={inv.id} sx={{ mb: 1, p: 1, bgcolor: 'action.hover', borderRadius: 1 }}>
                        <Typography variant="body2">{inv.title}</Typography>
                        {inv.machine_id && (
                          <Typography variant="caption" color="text.secondary">
                            Machine: {inv.machine_id}
                          </Typography>
                        )}
                      </Box>
                    ))}
                  </Box>
                )}

                {/* Pending Follow-ups */}
                {shiftSummary.pending_followups.length > 0 && (
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="subtitle2" sx={{ mb: 1, color: 'error.main' }}>
                      Pending Follow-ups
                    </Typography>
                    {shiftSummary.pending_followups.map((fu) => (
                      <Box key={fu.id} sx={{ mb: 1, p: 1, bgcolor: 'error.light', borderRadius: 1 }}>
                        <Typography variant="body2">{fu.description}</Typography>
                        <Typography variant="caption" color="text.secondary">
                          Due: {fu.follow_up_date}
                        </Typography>
                      </Box>
                    ))}
                  </Box>
                )}

                {/* Today's Actions */}
                {shiftSummary.todays_actions.length > 0 && (
                  <Box>
                    <Typography variant="subtitle2" sx={{ mb: 1 }}>
                      Today&apos;s Actions
                    </Typography>
                    {shiftSummary.todays_actions.map((act) => (
                      <Box key={act.id} sx={{ mb: 1, p: 1, bgcolor: 'action.hover', borderRadius: 1 }}>
                        <Typography variant="body2">{act.description}</Typography>
                        <Typography variant="caption" color="text.secondary">
                          Expected: {act.expected_impact}
                        </Typography>
                      </Box>
                    ))}
                  </Box>
                )}

                {/* Empty State */}
                {shiftSummary.active_investigations.length === 0 &&
                  shiftSummary.pending_followups.length === 0 &&
                  shiftSummary.todays_actions.length === 0 && (
                    <Typography color="text.secondary" sx={{ textAlign: 'center', mt: 4 }}>
                      No activity for today&apos;s shift yet.
                    </Typography>
                  )}
              </Box>
            ) : (
              <Typography color="text.secondary" sx={{ textAlign: 'center', mt: 4 }}>
                Loading shift summary...
              </Typography>
            )}
          </TabPanel>
        </Box>
      )}
    </Drawer>
  );
};

export default MemoryPanel;
