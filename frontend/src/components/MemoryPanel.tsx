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
 * - Tailwind CSS + Framer Motion design
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  X,
  Search,
  Wrench,
  FileText,
  Loader2,
  AlertCircle,
} from 'lucide-react';
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

// ============================================================================
// Helper Functions
// ============================================================================

/**
 * Get status badge styles and label
 */
const getStatusStyles = (status: InvestigationStatus): { styles: string; label: string } => {
  switch (status) {
    case 'open':
      return {
        styles: 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300 border-red-200 dark:border-red-800',
        label: 'Open',
      };
    case 'in_progress':
      return {
        styles: 'bg-amber-100 dark:bg-amber-900/30 text-amber-800 dark:text-amber-300 border-amber-200 dark:border-amber-800',
        label: 'In Progress',
      };
    case 'resolved':
      return {
        styles: 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300 border-green-200 dark:border-green-800',
        label: 'Resolved',
      };
    case 'closed':
      return {
        styles: 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-300 border-gray-200 dark:border-gray-600',
        label: 'Closed',
      };
    default:
      return {
        styles: 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-300 border-gray-200 dark:border-gray-600',
        label: status,
      };
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
// Tab Configuration
// ============================================================================

const TABS = [
  { id: 'investigations', label: 'Investigations', icon: Search },
  { id: 'actions', label: 'Actions', icon: Wrench },
  { id: 'summary', label: 'Summary', icon: FileText },
] as const;

type TabId = typeof TABS[number]['id'];

// ============================================================================
// Main Component
// ============================================================================

const MemoryPanel: React.FC<MemoryPanelProps> = ({ open, onClose }) => {
  // State for tabs
  const [activeTab, setActiveTab] = useState<TabId>('investigations');

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

  return (
    <AnimatePresence>
      {open && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="fixed inset-0 bg-black/50 z-40"
            onClick={onClose}
          />

          {/* Panel */}
          <motion.div
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', damping: 25, stiffness: 300 }}
            className="fixed right-0 top-0 h-full w-full sm:w-[400px] bg-white dark:bg-gray-800 shadow-xl z-50 flex flex-col"
          >
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                Agent Memory
              </h2>
              <button
                onClick={onClose}
                className="p-1.5 rounded-lg text-gray-500 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-700 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Loading State */}
            {loading && (
              <div className="flex-1 flex items-center justify-center">
                <Loader2 className="w-8 h-8 text-blue-600 dark:text-blue-400 animate-spin" />
              </div>
            )}

            {/* Error State */}
            {error && (
              <div className="p-4">
                <div className="flex items-start gap-3 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
                  <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
                  <div className="flex-1">
                    <p className="text-sm text-red-700 dark:text-red-300">{error}</p>
                    <button
                      onClick={() => setError(null)}
                      className="text-xs text-red-600 dark:text-red-400 hover:underline mt-1"
                    >
                      Dismiss
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Content */}
            {!loading && !error && (
              <div className="flex-1 flex flex-col overflow-hidden">
                {/* Tabs */}
                <div className="flex border-b border-gray-200 dark:border-gray-700" role="tablist">
                  {TABS.map((tab) => {
                    const Icon = tab.icon;
                    const count = tab.id === 'investigations' ? investigations.length :
                                  tab.id === 'actions' ? actions.length : null;
                    const isActive = activeTab === tab.id;

                    return (
                      <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id)}
                        role="tab"
                        aria-selected={isActive}
                        className={`
                          flex-1 flex items-center justify-center gap-1.5 px-2 py-3 text-sm font-medium
                          border-b-2 transition-colors
                          ${isActive
                            ? 'border-blue-600 text-blue-600 dark:border-blue-400 dark:text-blue-400'
                            : 'border-transparent text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
                          }
                        `}
                      >
                        <Icon className="w-4 h-4" />
                        <span className="hidden sm:inline">{tab.label}</span>
                        {count !== null && (
                          <span className={`
                            px-1.5 py-0.5 text-xs rounded-full
                            ${isActive
                              ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400'
                              : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400'
                            }
                          `}>
                            {count}
                          </span>
                        )}
                      </button>
                    );
                  })}
                </div>

                {/* Tab Panels */}
                <div className="flex-1 overflow-y-auto p-4">
                  {/* Investigations Tab */}
                  {activeTab === 'investigations' && (
                    <div>
                      {investigations.length === 0 ? (
                        <p className="text-center text-gray-500 dark:text-gray-400 mt-8">
                          No investigations yet. Start a conversation with the AI assistant to create one.
                        </p>
                      ) : (
                        <div className="space-y-3">
                          {investigations.map((inv) => {
                            const statusInfo = getStatusStyles(inv.status);
                            return (
                              <div
                                key={inv.id}
                                className="p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg border border-gray-200 dark:border-gray-600"
                              >
                                <div className="flex items-start justify-between gap-2 mb-2">
                                  <h4 className="font-medium text-gray-900 dark:text-white text-sm">
                                    {inv.title}
                                  </h4>
                                  <span className={`px-2 py-0.5 text-xs font-medium rounded-full border ${statusInfo.styles}`}>
                                    {statusInfo.label}
                                  </span>
                                </div>
                                <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                                  {inv.initial_observation}
                                </p>
                                <div className="flex flex-wrap items-center gap-2">
                                  {inv.machine_id && (
                                    <span className="px-2 py-0.5 text-xs bg-gray-200 dark:bg-gray-600 text-gray-700 dark:text-gray-300 rounded-full">
                                      {inv.machine_id}
                                    </span>
                                  )}
                                  {inv.supplier_id && (
                                    <span className="px-2 py-0.5 text-xs bg-gray-200 dark:bg-gray-600 text-gray-700 dark:text-gray-300 rounded-full">
                                      {inv.supplier_id}
                                    </span>
                                  )}
                                  <span className="text-xs text-gray-500 dark:text-gray-400">
                                    Updated: {formatDate(inv.updated_at)}
                                  </span>
                                </div>
                                {inv.findings.length > 0 && (
                                  <div className="mt-2 pt-2 border-t border-gray-200 dark:border-gray-600">
                                    <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">Findings:</p>
                                    <ul className="text-xs text-gray-600 dark:text-gray-300 list-disc list-inside space-y-0.5">
                                      {inv.findings.slice(0, 2).map((finding, idx) => (
                                        <li key={idx}>{finding}</li>
                                      ))}
                                      {inv.findings.length > 2 && (
                                        <li className="text-gray-500 dark:text-gray-400">
                                          +{inv.findings.length - 2} more
                                        </li>
                                      )}
                                    </ul>
                                  </div>
                                )}
                              </div>
                            );
                          })}
                        </div>
                      )}
                    </div>
                  )}

                  {/* Actions Tab */}
                  {activeTab === 'actions' && (
                    <div>
                      {actions.length === 0 ? (
                        <p className="text-center text-gray-500 dark:text-gray-400 mt-8">
                          No actions recorded yet. Ask the AI to track parameter changes or maintenance activities.
                        </p>
                      ) : (
                        <div className="space-y-3">
                          {actions.map((action) => (
                            <div
                              key={action.id}
                              className="p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg border border-gray-200 dark:border-gray-600"
                            >
                              <div className="flex items-start justify-between gap-2 mb-2">
                                <h4 className="font-medium text-gray-900 dark:text-white text-sm">
                                  {action.description}
                                </h4>
                                <span className="px-2 py-0.5 text-xs font-medium bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300 border border-blue-200 dark:border-blue-800 rounded-full whitespace-nowrap">
                                  {action.action_type.replace('_', ' ')}
                                </span>
                              </div>
                              <p className="text-sm text-gray-600 dark:text-gray-400">
                                Expected: {action.expected_impact}
                              </p>
                              {action.actual_impact && (
                                <p className="text-sm text-green-600 dark:text-green-400 mt-1">
                                  Result: {action.actual_impact}
                                </p>
                              )}
                              <div className="flex flex-wrap items-center gap-2 mt-2">
                                {action.machine_id && (
                                  <span className="px-2 py-0.5 text-xs bg-gray-200 dark:bg-gray-600 text-gray-700 dark:text-gray-300 rounded-full">
                                    {action.machine_id}
                                  </span>
                                )}
                                {action.follow_up_date && !action.actual_impact && (
                                  <span className="px-2 py-0.5 text-xs bg-amber-100 dark:bg-amber-900/30 text-amber-800 dark:text-amber-300 border border-amber-200 dark:border-amber-800 rounded-full">
                                    Follow-up: {action.follow_up_date}
                                  </span>
                                )}
                              </div>
                              <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                                Created: {formatDate(action.created_at)}
                              </p>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}

                  {/* Summary Tab */}
                  {activeTab === 'summary' && (
                    <div>
                      {shiftSummary ? (
                        <div>
                          <h3 className="font-semibold text-gray-900 dark:text-white mb-4">
                            Shift Summary - {shiftSummary.date}
                          </h3>

                          {/* Counts Grid */}
                          <div className="grid grid-cols-3 gap-4 mb-6">
                            <div className="text-center p-3 bg-amber-50 dark:bg-amber-900/20 rounded-lg">
                              <p className="text-2xl font-bold text-amber-600 dark:text-amber-400">
                                {shiftSummary.counts.active_investigations}
                              </p>
                              <p className="text-xs text-gray-600 dark:text-gray-400">Active</p>
                            </div>
                            <div className="text-center p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                              <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                                {shiftSummary.counts.todays_actions}
                              </p>
                              <p className="text-xs text-gray-600 dark:text-gray-400">Today&apos;s Actions</p>
                            </div>
                            <div className="text-center p-3 bg-red-50 dark:bg-red-900/20 rounded-lg">
                              <p className="text-2xl font-bold text-red-600 dark:text-red-400">
                                {shiftSummary.counts.pending_followups}
                              </p>
                              <p className="text-xs text-gray-600 dark:text-gray-400">Follow-ups</p>
                            </div>
                          </div>

                          <hr className="border-gray-200 dark:border-gray-700 mb-4" />

                          {/* Active Investigations */}
                          {shiftSummary.active_investigations.length > 0 && (
                            <div className="mb-4">
                              <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-2">
                                Active Investigations
                              </h4>
                              <div className="space-y-2">
                                {shiftSummary.active_investigations.map((inv) => (
                                  <div
                                    key={inv.id}
                                    className="p-2 bg-gray-100 dark:bg-gray-700 rounded-lg"
                                  >
                                    <p className="text-sm text-gray-900 dark:text-white">{inv.title}</p>
                                    {inv.machine_id && (
                                      <p className="text-xs text-gray-500 dark:text-gray-400">
                                        Machine: {inv.machine_id}
                                      </p>
                                    )}
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}

                          {/* Pending Follow-ups */}
                          {shiftSummary.pending_followups.length > 0 && (
                            <div className="mb-4">
                              <h4 className="text-sm font-medium text-red-600 dark:text-red-400 mb-2">
                                Pending Follow-ups
                              </h4>
                              <div className="space-y-2">
                                {shiftSummary.pending_followups.map((fu) => (
                                  <div
                                    key={fu.id}
                                    className="p-2 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg"
                                  >
                                    <p className="text-sm text-gray-900 dark:text-white">{fu.description}</p>
                                    <p className="text-xs text-gray-500 dark:text-gray-400">
                                      Due: {fu.follow_up_date}
                                    </p>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}

                          {/* Today's Actions */}
                          {shiftSummary.todays_actions.length > 0 && (
                            <div className="mb-4">
                              <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-2">
                                Today&apos;s Actions
                              </h4>
                              <div className="space-y-2">
                                {shiftSummary.todays_actions.map((act) => (
                                  <div
                                    key={act.id}
                                    className="p-2 bg-gray-100 dark:bg-gray-700 rounded-lg"
                                  >
                                    <p className="text-sm text-gray-900 dark:text-white">{act.description}</p>
                                    <p className="text-xs text-gray-500 dark:text-gray-400">
                                      Expected: {act.expected_impact}
                                    </p>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}

                          {/* Empty State */}
                          {shiftSummary.active_investigations.length === 0 &&
                            shiftSummary.pending_followups.length === 0 &&
                            shiftSummary.todays_actions.length === 0 && (
                              <p className="text-center text-gray-500 dark:text-gray-400 mt-8">
                                No activity for today&apos;s shift yet.
                              </p>
                            )}
                        </div>
                      ) : (
                        <p className="text-center text-gray-500 dark:text-gray-400 mt-8">
                          Loading shift summary...
                        </p>
                      )}
                    </div>
                  )}
                </div>
              </div>
            )}
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};

export default MemoryPanel;
