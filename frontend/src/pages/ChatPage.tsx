/**
 * ChatPage - AI-powered factory assistant chat interface
 *
 * Features:
 * - Real-time chat with Azure OpenAI backend
 * - Message history with auto-scroll
 * - Suggested prompts for common queries
 * - Loading states and error handling
 * - Clean Material-UI design
 *
 * Architecture:
 * - Uses custom useChat hook for state management
 * - Integrates with /api/chat endpoint via apiService
 * - Follows React best practices from react.dev
 */

import { useState, useRef, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
  TextField,
  Button,
  CircularProgress,
  Alert,
  Chip,
  IconButton,
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import DeleteIcon from '@mui/icons-material/Delete';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import PersonIcon from '@mui/icons-material/Person';
import { useChat } from '../hooks/useChat';

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
  // Custom hook for chat state management
  const { messages, isLoading, error, sendMessage, clearMessages, clearError } = useChat();

  // Local state for input field
  const [input, setInput] = useState('');

  // Ref for auto-scrolling to latest message
  const messagesEndRef = useRef<HTMLDivElement>(null);

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
    <Container maxWidth="xl">
      {/* Page Header */}
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Typography variant="h4" component="h1" gutterBottom>
            AI Chat
          </Typography>
          <Typography variant="subtitle1" color="text.secondary">
            Ask questions about your factory operations - powered by Azure OpenAI
          </Typography>
        </Box>
        {messages.length > 0 && (
          <IconButton
            onClick={handleClearChat}
            color="error"
            title="Clear chat history"
            disabled={isLoading}
          >
            <DeleteIcon />
          </IconButton>
        )}
      </Box>

      {/* Main Chat Container */}
      <Paper
        sx={{
          display: 'flex',
          flexDirection: 'column',
          height: 'calc(100vh - 280px)',
          minHeight: 500,
        }}
      >
        {/* Messages Area */}
        <Box
          sx={{
            flex: 1,
            overflowY: 'auto',
            p: 3,
            backgroundColor: '#f5f5f5',
          }}
        >
          {/* Empty State - Show suggested prompts when no messages */}
          {messages.length === 0 && (
            <Box sx={{ textAlign: 'center', mt: 8 }}>
              <SmartToyIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
              <Typography variant="h6" color="text.secondary" gutterBottom>
                Welcome to Factory AI Assistant
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 4 }}>
                Get instant insights about your factory operations
              </Typography>

              {/* Suggested Prompts */}
              <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 2 }}>
                Try asking:
              </Typography>
              <Box
                sx={{
                  display: 'flex',
                  flexWrap: 'wrap',
                  gap: 1,
                  justifyContent: 'center',
                  maxWidth: 700,
                  mx: 'auto',
                }}
              >
                {SUGGESTED_PROMPTS.map((prompt, index) => (
                  <Chip
                    key={index}
                    label={prompt}
                    onClick={() => handlePromptClick(prompt)}
                    disabled={isLoading}
                    sx={{
                      cursor: 'pointer',
                      '&:hover': {
                        backgroundColor: 'primary.light',
                        color: 'white',
                      },
                    }}
                  />
                ))}
              </Box>
            </Box>
          )}

          {/* Message History */}
          {messages.map((message) => (
            <Box
              key={message.id}
              sx={{
                display: 'flex',
                justifyContent: message.role === 'user' ? 'flex-end' : 'flex-start',
                mb: 2,
              }}
            >
              <Box
                sx={{
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: 1,
                  maxWidth: '70%',
                  flexDirection: message.role === 'user' ? 'row-reverse' : 'row',
                }}
              >
                {/* Avatar Icon */}
                <Box
                  sx={{
                    width: 40,
                    height: 40,
                    borderRadius: '50%',
                    backgroundColor: message.role === 'user' ? 'primary.main' : 'secondary.main',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: 'white',
                    flexShrink: 0,
                  }}
                >
                  {message.role === 'user' ? <PersonIcon /> : <SmartToyIcon />}
                </Box>

                {/* Message Bubble */}
                <Paper
                  elevation={1}
                  sx={{
                    p: 2,
                    backgroundColor: message.role === 'user' ? 'primary.light' : 'white',
                    color: message.role === 'user' ? 'white' : 'text.primary',
                    borderRadius: 2,
                  }}
                >
                  <Typography
                    variant="body1"
                    sx={{
                      whiteSpace: 'pre-wrap',
                      wordBreak: 'break-word',
                    }}
                  >
                    {message.content}
                  </Typography>
                  <Typography
                    variant="caption"
                    sx={{
                      mt: 1,
                      display: 'block',
                      opacity: 0.7,
                    }}
                  >
                    {message.timestamp.toLocaleTimeString()}
                  </Typography>
                </Paper>
              </Box>
            </Box>
          ))}

          {/* Loading Indicator */}
          {isLoading && (
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                gap: 1,
                mb: 2,
              }}
            >
              <Box
                sx={{
                  width: 40,
                  height: 40,
                  borderRadius: '50%',
                  backgroundColor: 'secondary.main',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'white',
                }}
              >
                <SmartToyIcon />
              </Box>
              <Paper
                elevation={1}
                sx={{
                  p: 2,
                  borderRadius: 2,
                  display: 'flex',
                  alignItems: 'center',
                  gap: 1,
                }}
              >
                <CircularProgress size={20} />
                <Typography variant="body2" color="text.secondary">
                  Thinking...
                </Typography>
              </Paper>
            </Box>
          )}

          {/* Auto-scroll anchor */}
          <div ref={messagesEndRef} />
        </Box>

        {/* Error Alert */}
        {error && (
          <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
            <Alert severity="error" onClose={clearError}>
              {error}
            </Alert>
          </Box>
        )}

        {/* Input Area */}
        <Box
          component="form"
          onSubmit={handleSubmit}
          sx={{
            p: 2,
            borderTop: 1,
            borderColor: 'divider',
            backgroundColor: 'white',
          }}
        >
          <Box sx={{ display: 'flex', gap: 1 }}>
            <TextField
              fullWidth
              multiline
              maxRows={4}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask a question about your factory operations..."
              disabled={isLoading}
              onKeyDown={(e) => {
                // Submit on Enter (without Shift)
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSubmit(e);
                }
              }}
              sx={{
                '& .MuiOutlinedInput-root': {
                  backgroundColor: 'white',
                },
              }}
            />
            <Button
              type="submit"
              variant="contained"
              disabled={!input.trim() || isLoading}
              endIcon={isLoading ? <CircularProgress size={20} /> : <SendIcon />}
              sx={{
                minWidth: 100,
                height: 56,
              }}
            >
              Send
            </Button>
          </Box>

          {/* Suggested Prompts (shown below input when chat has started) */}
          {messages.length > 0 && (
            <Box sx={{ mt: 2, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
              <Typography variant="caption" color="text.secondary" sx={{ width: '100%', mb: 0.5 }}>
                Quick prompts:
              </Typography>
              {SUGGESTED_PROMPTS.slice(0, 4).map((prompt, index) => (
                <Chip
                  key={index}
                  label={prompt}
                  size="small"
                  onClick={() => handlePromptClick(prompt)}
                  disabled={isLoading}
                  sx={{
                    cursor: 'pointer',
                    fontSize: '0.75rem',
                  }}
                />
              ))}
            </Box>
          )}
        </Box>
      </Paper>
    </Container>
  );
};

export default ChatPage;
