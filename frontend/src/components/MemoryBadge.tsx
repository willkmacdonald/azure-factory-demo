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
 * - Tailwind CSS + Framer Motion design
 */

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Brain } from 'lucide-react';

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
  const [showTooltip, setShowTooltip] = useState(false);

  // Calculate total items needing attention
  const totalActive = openInvestigations + pendingFollowups;

  // Determine badge color based on status
  const getBadgeStyles = (): string => {
    if (pendingFollowups > 0) return 'bg-red-500 text-white';
    if (openInvestigations > 0) return 'bg-amber-500 text-white';
    return 'bg-gray-400 dark:bg-gray-600 text-white';
  };

  return (
    <div className="relative">
      {/* Button with badge */}
      <motion.button
        onClick={onClick}
        disabled={disabled}
        onMouseEnter={() => setShowTooltip(true)}
        onMouseLeave={() => setShowTooltip(false)}
        onFocus={() => setShowTooltip(true)}
        onBlur={() => setShowTooltip(false)}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        animate={totalActive > 0 ? {
          scale: [1, 1.05, 1],
        } : {}}
        transition={totalActive > 0 ? {
          duration: 2,
          repeat: Infinity,
          ease: "easeInOut",
        } : {}}
        className={`
          relative p-2 rounded-lg transition-colors
          text-gray-600 dark:text-gray-400
          hover:bg-gray-100 dark:hover:bg-gray-700
          focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:focus:ring-offset-gray-800
          disabled:opacity-50 disabled:cursor-not-allowed
        `}
        aria-label={`Open agent memory: ${openInvestigations} investigation${openInvestigations !== 1 ? 's' : ''}, ${pendingFollowups} follow-up${pendingFollowups !== 1 ? 's' : ''}`}
      >
        <Brain className="w-5 h-5" />

        {/* Badge */}
        {totalActive > 0 && (
          <span
            className={`
              absolute -top-1 -right-1
              min-w-[18px] h-[18px]
              flex items-center justify-center
              text-xs font-medium
              rounded-full
              ${getBadgeStyles()}
            `}
          >
            {totalActive > 99 ? '99+' : totalActive}
          </span>
        )}
      </motion.button>

      {/* Tooltip */}
      <AnimatePresence>
        {showTooltip && (
          <motion.div
            initial={{ opacity: 0, y: 5 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 5 }}
            transition={{ duration: 0.15 }}
            className="absolute top-full right-0 mt-2 z-50"
          >
            <div className="bg-gray-900 dark:bg-gray-700 text-white text-sm rounded-lg shadow-lg p-3 min-w-[180px]">
              {/* Arrow */}
              <div className="absolute -top-1 right-4 w-2 h-2 bg-gray-900 dark:bg-gray-700 rotate-45" />

              <p className="font-semibold mb-1">Agent Memory</p>
              <p className="text-gray-300">
                {openInvestigations} open investigation{openInvestigations !== 1 ? 's' : ''}
              </p>
              <p className="text-gray-300">
                {pendingFollowups} pending follow-up{pendingFollowups !== 1 ? 's' : ''}
              </p>
              <p className="text-gray-400 text-xs mt-2">
                Click to view details
              </p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default MemoryBadge;
