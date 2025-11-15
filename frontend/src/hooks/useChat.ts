/**
 * useChat Hook - Custom React hook for managing chat state
 *
 * Handles:
 * - Message history state management
 * - Sending messages to Azure OpenAI backend
 * - Loading and error states
 * - Auto-scroll to latest messages
 *
 * Based on React documentation patterns for custom hooks:
 * https://react.dev/learn/reusing-logic-with-custom-hooks
 */

import { useState, useCallback } from 'react';
import { apiService, getErrorMessage } from '../api/client';
import type { ChatRequest, ChatResponse } from '../types/api';

// ============================================================================
// Types
// ============================================================================

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export interface UseChatReturn {
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  sendMessage: (content: string) => Promise<void>;
  clearMessages: () => void;
  clearError: () => void;
}

// ============================================================================
// useChat Hook
// ============================================================================

/**
 * Custom hook for managing chat interactions with Azure OpenAI backend
 *
 * Usage:
 * ```tsx
 * const { messages, isLoading, error, sendMessage } = useChat();
 *
 * const handleSubmit = async () => {
 *   await sendMessage(inputValue);
 * };
 * ```
 */
export function useChat(): UseChatReturn {
  // State management
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * Send a message to the AI assistant
   * - Adds user message to history immediately
   * - Calls backend API
   * - Adds assistant response to history
   * - Handles errors gracefully
   */
  const sendMessage = useCallback(async (content: string) => {
    // Clear any previous errors
    setError(null);

    // Validate input
    if (!content.trim()) {
      setError('Message cannot be empty');
      return;
    }

    // Create user message
    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: content.trim(),
      timestamp: new Date(),
    };

    // Add user message to history immediately
    setMessages((prev) => [...prev, userMessage]);

    // Set loading state
    setIsLoading(true);

    try {
      // Prepare request with message history context
      const request: ChatRequest = {
        message: content.trim(),
        // Include recent message history for context (last 10 messages)
        history: messages.slice(-10).map((msg) => ({
          role: msg.role,
          content: msg.content,
        })),
      };

      // Call backend API
      const response: ChatResponse = await apiService.sendChatMessage(request);

      // Create assistant message
      const assistantMessage: Message = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: response.response,
        timestamp: new Date(),
      };

      // Add assistant response to history
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      // Handle errors
      const errorMessage = getErrorMessage(err);
      setError(errorMessage);

      console.error('[useChat] Failed to send message:', err);
    } finally {
      setIsLoading(false);
    }
  }, [messages]);

  /**
   * Clear all messages from chat history
   */
  const clearMessages = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);

  /**
   * Clear error state
   */
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    messages,
    isLoading,
    error,
    sendMessage,
    clearMessages,
    clearError,
  };
}
