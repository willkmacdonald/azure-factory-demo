/**
 * useChat Hook - Custom React hook for managing chat state
 *
 * Handles:
 * - Message history state management
 * - Sending messages to Azure OpenAI backend with streaming support
 * - Loading and error states
 * - Status updates during AI processing
 * - Auto-scroll to latest messages
 *
 * Based on React documentation patterns for custom hooks:
 * https://react.dev/learn/reusing-logic-with-custom-hooks
 */

import { useState, useCallback, useRef } from 'react';
import { getErrorMessage } from '../api/client';
import type { ChatRequest, ChatStreamEvent } from '../types/api';

// Build-time environment configuration
// VITE_API_BASE_URL is set during CI/CD build for production deployments
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// ============================================================================
// Types
// ============================================================================

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  isStreaming?: boolean;  // True while message is being streamed
}

export interface UseChatReturn {
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  streamStatus: string | null;  // Current status (e.g., "Thinking...", "Executing get_oee_metrics")
  sendMessage: (content: string) => Promise<void>;
  clearMessages: () => void;
  clearError: () => void;
}

// ============================================================================
// useChat Hook
// ============================================================================

/**
 * Custom hook for managing chat interactions with Azure OpenAI backend
 * Supports streaming responses via Server-Sent Events (SSE)
 *
 * Usage:
 * ```tsx
 * const { messages, isLoading, error, streamStatus, sendMessage } = useChat();
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
  const [streamStatus, setStreamStatus] = useState<string | null>(null);

  // Ref to track the current streaming message ID
  const streamingMessageIdRef = useRef<string | null>(null);

  /**
   * Send a message to the AI assistant with streaming support
   * - Adds user message to history immediately
   * - Opens SSE connection to /api/chat/stream
   * - Updates assistant message as chunks arrive
   * - Handles tool call status updates
   */
  const sendMessage = useCallback(async (content: string) => {
    // Clear any previous errors
    setError(null);
    setStreamStatus(null);

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

    // Create placeholder assistant message for streaming
    const assistantMessageId = `assistant-${Date.now()}`;
    streamingMessageIdRef.current = assistantMessageId;

    const assistantMessage: Message = {
      id: assistantMessageId,
      role: 'assistant',
      content: '',
      timestamp: new Date(),
      isStreaming: true,
    };

    // Add empty assistant message that will be filled by streaming
    setMessages((prev) => [...prev, assistantMessage]);

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

      // Use fetch with streaming for SSE
      const response = await fetch(`${API_BASE_URL}/api/chat/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('No response body');
      }

      const decoder = new TextDecoder();
      let buffer = '';

      // Read the stream
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });

        // Process complete SSE events (data: {...}\n\n)
        const events = buffer.split('\n\n');
        buffer = events.pop() || ''; // Keep incomplete event in buffer

        for (const eventStr of events) {
          if (!eventStr.startsWith('data: ')) continue;

          try {
            const jsonStr = eventStr.slice(6); // Remove 'data: ' prefix
            const event: ChatStreamEvent = JSON.parse(jsonStr);

            switch (event.type) {
              case 'status':
                setStreamStatus(event.content || null);
                break;

              case 'delta':
                // Append text chunk to the streaming message
                setMessages((prev) =>
                  prev.map((msg) =>
                    msg.id === assistantMessageId
                      ? { ...msg, content: msg.content + (event.content || '') }
                      : msg
                  )
                );
                break;

              case 'tool_call':
                setStreamStatus(`Calling ${event.name}...`);
                break;

              case 'tool_result':
                setStreamStatus(`${event.name} complete`);
                break;

              case 'done':
                // Mark message as complete
                setMessages((prev) =>
                  prev.map((msg) =>
                    msg.id === assistantMessageId
                      ? { ...msg, content: event.content || msg.content, isStreaming: false }
                      : msg
                  )
                );
                setStreamStatus(null);
                break;

              case 'error':
                setError(event.content || 'An error occurred');
                // Remove the empty streaming message on error
                setMessages((prev) =>
                  prev.filter((msg) => msg.id !== assistantMessageId || msg.content.length > 0)
                );
                break;
            }
          } catch (parseError) {
            console.error('[useChat] Failed to parse SSE event:', parseError, eventStr);
          }
        }
      }
    } catch (err) {
      // Handle errors
      const errorMessage = getErrorMessage(err);
      setError(errorMessage);
      console.error('[useChat] Failed to send message:', err);

      // Remove empty streaming message on error
      setMessages((prev) =>
        prev.filter((msg) => msg.id !== assistantMessageId || msg.content.length > 0)
      );
    } finally {
      setIsLoading(false);
      setStreamStatus(null);
      streamingMessageIdRef.current = null;
    }
  }, [messages]);

  /**
   * Clear all messages from chat history
   */
  const clearMessages = useCallback(() => {
    setMessages([]);
    setError(null);
    setStreamStatus(null);
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
    streamStatus,
    sendMessage,
    clearMessages,
    clearError,
  };
}
