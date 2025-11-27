/**
 * MemoryBadge - Badge showing agent memory status
 *
 * Displays count of active investigations and pending follow-ups.
 * Click to open MemoryPanel for detailed view.
 *
 * Features:
 * - Shows investigation count with color-coded badge
 * - Indicates pending follow-ups requiring attention
 * - Tooltip with summary on hover
 * - Pulsing animation when items need attention
 */

import React from 'react';
import { Badge, IconButton, Tooltip, Box, Typography } from '@mui/material';
import PsychologyIcon from '@mui/icons-material/Psychology';

// ============================================================================
// Types
// ============================================================================

interface MemoryBadgeProps {
  openInvestigations: number;
  pendingFollowups: number;
  onClick: () => void;
  disabled?: boolean;
}

// ============================================================================
// Component
// ============================================================================

const MemoryBadge: React.FC<MemoryBadgeProps> = ({
  openInvestigations,
  pendingFollowups,
  onClick,
  disabled = false,
}) => {
  // Calculate total items needing attention
  const totalActive = openInvestigations + pendingFollowups;

  // Build tooltip content
  const tooltipContent = (
    <Box sx={{ p: 0.5 }}>
      <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mb: 0.5 }}>
        Agent Memory
      </Typography>
      <Typography variant="body2">
        {openInvestigations} open investigation{openInvestigations !== 1 ? 's' : ''}
      </Typography>
      <Typography variant="body2">
        {pendingFollowups} pending follow-up{pendingFollowups !== 1 ? 's' : ''}
      </Typography>
      <Typography variant="caption" sx={{ mt: 1, display: 'block', opacity: 0.8 }}>
        Click to view details
      </Typography>
    </Box>
  );

  // Determine badge color based on status
  const getBadgeColor = (): 'error' | 'warning' | 'primary' | 'default' => {
    if (pendingFollowups > 0) return 'error';
    if (openInvestigations > 0) return 'warning';
    return 'default';
  };

  return (
    <Tooltip title={tooltipContent} arrow placement="bottom">
      <IconButton
        onClick={onClick}
        disabled={disabled}
        color="inherit"
        aria-label={`Open agent memory: ${openInvestigations} investigation${openInvestigations !== 1 ? 's' : ''}, ${pendingFollowups} follow-up${pendingFollowups !== 1 ? 's' : ''}`}
        sx={{
          // Pulsing animation when items need attention
          ...(totalActive > 0 && {
            animation: 'pulse 2s ease-in-out infinite',
            '@keyframes pulse': {
              '0%, 100%': { transform: 'scale(1)' },
              '50%': { transform: 'scale(1.05)' },
            },
          }),
        }}
      >
        <Badge
          badgeContent={totalActive > 0 ? totalActive : undefined}
          color={getBadgeColor()}
          max={99}
        >
          <PsychologyIcon />
        </Badge>
      </IconButton>
    </Tooltip>
  );
};

export default MemoryBadge;
