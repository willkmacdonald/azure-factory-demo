import React from 'react';
import { Container, Typography, Box, Paper } from '@mui/material';

/**
 * ChatPage - AI-powered factory assistant chat interface
 *
 * This is a placeholder for PR12. Will be enhanced in PR15 with:
 * - Chat message history
 * - Message input with Azure OpenAI integration
 * - Real-time streaming responses
 * - Context-aware factory insights
 */
const ChatPage: React.FC = () => {
  return (
    <Container maxWidth="xl">
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          AI Chat
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          Ask questions about your factory operations
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
            AI Chat Interface Coming Soon
          </Typography>
          <Typography variant="body1" color="text.secondary">
            PR15 will add chat functionality with Azure OpenAI integration
          </Typography>
        </Box>
      </Paper>
    </Container>
  );
};

export default ChatPage;
