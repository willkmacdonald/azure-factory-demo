/**
 * ChatPage - AI-powered factory assistant chat interface
 *
 * Features:
 * - Real-time chat with Azure OpenAI backend
 * - Message history with auto-scroll
 * - Suggested prompts for common queries
 * - Loading states and error handling
 * - Tailwind CSS + Framer Motion design
 *
 * Architecture:
 * - Uses custom useChat hook for state management
 * - Integrates with /api/chat endpoint via apiService
 * - Follows React best practices from react.dev
 */

import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Send,
  Trash2,
  Bot,
  User,
  Loader2,
  AlertCircle,
  X,
} from 'lucide-react';
import { useChat } from '../hooks/useChat';
import { apiService } from '../api/client';
import MemoryBadge from '../components/MemoryBadge';
import MemoryPanel from '../components/MemoryPanel';

// ============================================================================
// Suggested Prompts
// ============================================================================

const SUGGESTED_PROMPTS = [
  'What is the current OEE performance?',
  'Show me machines with quality issues',
  'What are the top causes of downtime?',
  'Analyze scrap rates by machine',
  'Which machine has the highest scrap rate?',
  'Compare OEE across all machines',
];

// ============================================================================
// ChatPage Component
// ============================================================================

const ChatPage: React.FC = () => {
  // Custom hook for chat state management (with streaming support)
  const { messages, isLoading, error, streamStatus, sendMessage, clearMessages, clearError } = useChat();

  // Local state for input field
  const [input, setInput] = useState('');

  // Memory panel state
  const [memoryPanelOpen, setMemoryPanelOpen] = useState(false);
  const [openInvestigations, setOpenInvestigations] = useState(0);
  const [pendingFollowups, setPendingFollowups] = useState(0);

  // Ref for auto-scrolling to latest message
  const messagesEndRef = useRef<HTMLDivElement>(null);

  /**
   * Load memory summary on mount and after sending messages
   * Updates badge counts for investigations and follow-ups
   */
  useEffect(() => {
    const loadMemorySummary = async (): Promise<void> => {
      try {
        const summary = await apiService.getMemorySummary();
        // Defensive handling for API response fields
        setOpenInvestigations(
          (summary.open_investigations || 0) + (summary.in_progress_investigations || 0)
        );
        setPendingFollowups(summary.pending_followups || 0);
      } catch (err) {
        // Silently fail - memory badge will show 0
        console.warn('[ChatPage] Failed to load memory summary:', err);
      }
    };

    loadMemorySummary();
  }, [messages.length]); // Refresh when messages change

  /**
   * Auto-scroll to bottom when new messages arrive
   * Uses useEffect with messages dependency to trigger on updates
   */
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  /**
   * Handle form submission
   * - Prevents default form behavior
   * - Sends message via useChat hook
   * - Clears input field on success
   */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!input.trim() || isLoading) {
      return;
    }

    const messageContent = input.trim();
    setInput(''); // Clear input immediately for better UX

    try {
      await sendMessage(messageContent);
    } catch (err) {
      // Error is handled by useChat hook
      console.error('[ChatPage] Failed to send message:', err);
    }
  };

  /**
   * Handle suggested prompt click
   * - Sends message immediately without setting input
   * - Input field remains clear for follow-up questions
   */
  const handlePromptClick = async (prompt: string) => {
    if (isLoading) {
      return;
    }

    await sendMessage(prompt);
  };

  /**
   * Handle clear chat
   * - Confirms with user before clearing
   * - Clears all messages and resets state
   */
  const handleClearChat = () => {
    if (messages.length === 0) {
      return;
    }

    if (window.confirm('Are you sure you want to clear the chat history?')) {
      clearMessages();
      setInput('');
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      {/* Page Header */}
      <div className="mb-6 flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white">
            AI Chat
          </h1>
          <p className="mt-1 text-gray-600 dark:text-gray-400">
            Ask questions about your factory operations - powered by Azure OpenAI
          </p>
        </div>
        <div className="flex items-center gap-2">
          {/* Memory Badge - opens panel to view investigations and actions */}
          <MemoryBadge
            openInvestigations={openInvestigations}
            pendingFollowups={pendingFollowups}
            onClick={() => setMemoryPanelOpen(true)}
            disabled={isLoading}
          />
          {messages.length > 0 && (
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={handleClearChat}
              disabled={isLoading}
              className="p-2 text-red-600 hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-900/20 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              title="Clear chat history"
            >
              <Trash2 className="w-5 h-5" />
            </motion.button>
          )}
        </div>
      </div>

      {/* Main Chat Container */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg flex flex-col" style={{ height: 'calc(100vh - 280px)', minHeight: '500px' }}>
        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 bg-gray-50 dark:bg-gray-900 rounded-t-xl">
          {/* Empty State - Show suggested prompts when no messages */}
          {messages.length === 0 && (
            <div className="text-center mt-12 sm:mt-16">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-100 dark:bg-blue-900/30 rounded-full mb-4">
                <Bot className="w-8 h-8 text-blue-600 dark:text-blue-400" />
              </div>
              <h2 className="text-xl font-semibold text-gray-700 dark:text-gray-300 mb-2">
                Welcome to Factory AI Assistant
              </h2>
              <p className="text-gray-500 dark:text-gray-400 mb-6">
                Get instant insights about your factory operations
              </p>

              {/* Suggested Prompts */}
              <p className="text-sm text-gray-500 dark:text-gray-400 mb-3">
                Try asking:
              </p>
              <div className="flex flex-wrap gap-2 justify-center max-w-2xl mx-auto">
                {SUGGESTED_PROMPTS.map((prompt, index) => (
                  <motion.button
                    key={index}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => handlePromptClick(prompt)}
                    disabled={isLoading}
                    className="px-4 py-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-full text-sm text-gray-700 dark:text-gray-300 hover:bg-blue-50 dark:hover:bg-blue-900/20 hover:border-blue-300 dark:hover:border-blue-700 hover:text-blue-700 dark:hover:text-blue-300 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {prompt}
                  </motion.button>
                ))}
              </div>
            </div>
          )}

          {/* Message History */}
          <AnimatePresence mode="popLayout">
            {messages.map((message) => (
              <motion.div
                key={message.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.2 }}
                className={`flex mb-4 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`flex items-start gap-3 max-w-[85%] sm:max-w-[70%] ${
                    message.role === 'user' ? 'flex-row-reverse' : 'flex-row'
                  }`}
                >
                  {/* Avatar Icon */}
                  <div
                    className={`flex-shrink-0 w-9 h-9 rounded-full flex items-center justify-center ${
                      message.role === 'user'
                        ? 'bg-blue-600 dark:bg-blue-500'
                        : 'bg-purple-600 dark:bg-purple-500'
                    }`}
                  >
                    {message.role === 'user' ? (
                      <User className="w-5 h-5 text-white" />
                    ) : (
                      <Bot className="w-5 h-5 text-white" />
                    )}
                  </div>

                  {/* Message Bubble */}
                  <div
                    className={`px-4 py-3 rounded-2xl ${
                      message.role === 'user'
                        ? 'bg-blue-600 text-white rounded-br-sm'
                        : 'bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 shadow-sm border border-gray-100 dark:border-gray-700 rounded-bl-sm'
                    }`}
                  >
                    <p className="text-sm sm:text-base whitespace-pre-wrap break-words">
                      {message.content}
                      {/* Blinking cursor for streaming messages */}
                      {message.isStreaming && (
                        <span className="inline-block w-0.5 h-4 bg-current ml-1 animate-pulse" />
                      )}
                    </p>
                    {!message.isStreaming && (
                      <p
                        className={`text-xs mt-2 ${
                          message.role === 'user'
                            ? 'text-blue-200'
                            : 'text-gray-400 dark:text-gray-500'
                        }`}
                      >
                        {message.timestamp.toLocaleTimeString()}
                      </p>
                    )}
                  </div>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>

          {/* Streaming Status Indicator */}
          <AnimatePresence>
            {isLoading && streamStatus && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="flex items-center gap-2 mb-4 ml-12"
              >
                <div className="inline-flex items-center gap-2 px-3 py-2 bg-gray-100 dark:bg-gray-800 rounded-full">
                  <Loader2 className="w-4 h-4 text-blue-600 dark:text-blue-400 animate-spin" />
                  <span className="text-sm text-gray-600 dark:text-gray-400">
                    {streamStatus}
                  </span>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Auto-scroll anchor */}
          <div ref={messagesEndRef} />
        </div>

        {/* Error Alert */}
        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="border-t border-gray-200 dark:border-gray-700"
            >
              <div className="p-4">
                <div className="flex items-center gap-3 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
                  <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0" />
                  <p className="text-sm text-red-700 dark:text-red-300 flex-1">{error}</p>
                  <button
                    onClick={clearError}
                    className="p-1 text-red-600 dark:text-red-400 hover:bg-red-100 dark:hover:bg-red-900/30 rounded"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Input Area */}
        <form
          onSubmit={handleSubmit}
          className="p-4 border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 rounded-b-xl"
        >
          <div className="flex gap-3">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask a question about your factory operations..."
              disabled={isLoading}
              rows={1}
              onKeyDown={(e) => {
                // Submit on Enter (without Shift)
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSubmit(e);
                }
              }}
              className="flex-1 px-4 py-3 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none disabled:opacity-50 disabled:cursor-not-allowed"
              style={{ maxHeight: '120px' }}
            />
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              type="submit"
              disabled={!input.trim() || isLoading}
              className="px-5 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 dark:disabled:bg-gray-600 text-white rounded-xl font-medium transition-colors flex items-center gap-2 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <Send className="w-5 h-5" />
              )}
              <span className="hidden sm:inline">Send</span>
            </motion.button>
          </div>

          {/* Suggested Prompts (shown below input when chat has started) */}
          {messages.length > 0 && (
            <div className="mt-3">
              <p className="text-xs text-gray-500 dark:text-gray-400 mb-2">
                Quick prompts:
              </p>
              <div className="flex flex-wrap gap-2">
                {SUGGESTED_PROMPTS.slice(0, 4).map((prompt, index) => (
                  <button
                    key={index}
                    type="button"
                    onClick={() => handlePromptClick(prompt)}
                    disabled={isLoading}
                    className="px-3 py-1.5 text-xs bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-full hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            </div>
          )}
        </form>
      </div>

      {/* Memory Panel - Drawer showing investigations and actions */}
      <MemoryPanel
        open={memoryPanelOpen}
        onClose={() => setMemoryPanelOpen(false)}
      />
    </div>
  );
};

export default ChatPage;
