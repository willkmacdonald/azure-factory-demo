/**
 * Async Utilities and React Hooks
 *
 * Reusable patterns for async operations including:
 * - useAsyncData hook for loading/error state management
 * - Error formatting utilities
 * - Retry logic with exponential backoff
 * - Loading skeleton component patterns
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import type { FormattedApiError } from '../api/client';
import { getErrorMessage } from '../api/client';

// ============================================================================
// Types
// ============================================================================

/**
 * State for async data fetching
 */
export interface AsyncState<T> {
  /** The fetched data, or null if not yet loaded or on error */
  data: T | null;
  /** True while the async operation is in progress */
  loading: boolean;
  /** Error message if the operation failed, null otherwise */
  error: string | null;
  /** Function to manually trigger a refresh of the data */
  refetch: () => Promise<void>;
}

/**
 * Options for useAsyncData hook
 */
export interface UseAsyncDataOptions {
  /** If true, fetches data immediately on component mount (default: true) */
  immediate?: boolean;
  /** Callback function invoked when data is successfully fetched */
  onSuccess?: () => void;
  /** Callback function invoked when an error occurs, receives error message */
  onError?: (error: string) => void;
}

/**
 * Retry options for retry utility
 */
export interface RetryOptions {
  maxRetries?: number;        // Maximum number of retry attempts (default: 3)
  initialDelay?: number;      // Initial delay in ms (default: 1000)
  maxDelay?: number;          // Maximum delay in ms (default: 10000)
  backoffFactor?: number;     // Exponential backoff multiplier (default: 2)
  shouldRetry?: (error: unknown) => boolean;  // Custom retry condition
}

// ============================================================================
// React Hooks
// ============================================================================

/**
 * useAsyncData - Hook for managing async data fetching with loading/error states
 *
 * This hook handles the common pattern of:
 * 1. Loading state while fetching
 * 2. Error state if fetch fails
 * 3. Data state when successful
 * 4. Refetch function to manually trigger refresh
 *
 * @example
 * ```tsx
 * function MyComponent() {
 *   const { data, loading, error, refetch } = useAsyncData(
 *     async () => await apiService.getMachines(),
 *     { immediate: true }
 *   );
 *
 *   if (loading) return <CircularProgress />;
 *   if (error) return <Alert severity="error">{error}</Alert>;
 *   if (!data) return null;
 *
 *   return <MachineList machines={data} onRefresh={refetch} />;
 * }
 * ```
 */
export function useAsyncData<T>(
  asyncFunction: () => Promise<T>,
  options: UseAsyncDataOptions = {}
): AsyncState<T> {
  const { immediate = true, onSuccess, onError } = options;

  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState<boolean>(immediate);
  const [error, setError] = useState<string | null>(null);

  // Store async function in a ref to avoid recreating fetchData on every render
  // This ensures the useEffect dependency array remains stable
  const asyncFunctionRef = useRef(asyncFunction);
  const onSuccessRef = useRef(onSuccess);
  const onErrorRef = useRef(onError);

  // Update refs when callbacks change (but don't trigger re-render)
  useEffect(() => {
    asyncFunctionRef.current = asyncFunction;
    onSuccessRef.current = onSuccess;
    onErrorRef.current = onError;
  }, [asyncFunction, onSuccess, onError]);

  // Fetch function that can be called manually or automatically
  // Now has stable dependencies since it uses refs
  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const result = await asyncFunctionRef.current();
      setData(result);

      if (onSuccessRef.current) {
        onSuccessRef.current();
      }
    } catch (err) {
      const errorMessage = getErrorMessage(err);
      setError(errorMessage);

      if (onErrorRef.current) {
        onErrorRef.current(errorMessage);
      }
    } finally {
      setLoading(false);
    }
  }, []); // Empty dependency array - stable across renders

  // Auto-fetch on mount if immediate is true
  // fetchData is now stable, so this won't cause unnecessary re-fetches
  useEffect(() => {
    if (immediate) {
      fetchData();
    }
  }, [immediate, fetchData]);

  return {
    data,
    loading,
    error,
    refetch: fetchData,
  };
}

/**
 * useAsyncCallback - Hook for async callbacks (e.g., form submissions)
 *
 * Similar to useAsyncData but doesn't auto-fetch on mount.
 * Useful for user-triggered actions like button clicks.
 *
 * @example
 * ```tsx
 * function ChatForm() {
 *   const [message, setMessage] = useState('');
 *   const { execute, loading, error } = useAsyncCallback(
 *     async () => await apiService.sendChatMessage({ message, history: [] })
 *   );
 *
 *   return (
 *     <form onSubmit={(e) => { e.preventDefault(); execute(); }}>
 *       <TextField value={message} onChange={(e) => setMessage(e.target.value)} />
 *       <Button type="submit" disabled={loading}>Send</Button>
 *       {error && <Alert severity="error">{error}</Alert>}
 *     </form>
 *   );
 * }
 * ```
 */
export function useAsyncCallback<T, Args extends unknown[]>(
  asyncFunction: (...args: Args) => Promise<T>,
  options: UseAsyncDataOptions = {}
): {
  execute: (...args: Args) => Promise<T | null>;
  data: T | null;
  loading: boolean;
  error: string | null;
  reset: () => void;
} {
  const { onSuccess, onError } = options;

  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const execute = useCallback(
    async (...args: Args): Promise<T | null> => {
      try {
        setLoading(true);
        setError(null);

        const result = await asyncFunction(...args);
        setData(result);

        if (onSuccess) {
          onSuccess();
        }

        return result;
      } catch (err) {
        const errorMessage = getErrorMessage(err);
        setError(errorMessage);

        if (onError) {
          onError(errorMessage);
        }

        return null;
      } finally {
        setLoading(false);
      }
    },
    [asyncFunction, onSuccess, onError]
  );

  const reset = useCallback(() => {
    setData(null);
    setError(null);
    setLoading(false);
  }, []);

  return {
    execute,
    data,
    loading,
    error,
    reset,
  };
}

// ============================================================================
// Error Utilities
// ============================================================================

/**
 * Check if error is a network error (no response from server)
 */
export function isNetworkError(error: unknown): boolean {
  if (!error || typeof error !== 'object') return false;
  return (error as FormattedApiError).isNetworkError === true;
}

/**
 * Check if error is a timeout error
 */
export function isTimeoutError(error: unknown): boolean {
  if (!error || typeof error !== 'object') return false;
  return (error as FormattedApiError).isTimeoutError === true;
}

/**
 * Check if error is a server error (5xx status code)
 */
export function isServerError(error: unknown): boolean {
  if (!error || typeof error !== 'object') return false;
  return (error as FormattedApiError).isServerError === true;
}

/**
 * Check if error is a client error (4xx status code)
 */
export function isClientError(error: unknown): boolean {
  if (!error || typeof error !== 'object') return false;
  return (error as FormattedApiError).isClientError === true;
}

/**
 * Check if error is an authentication error (401/403)
 */
export function isAuthError(error: unknown): boolean {
  if (!error || typeof error !== 'object') return false;
  const status = (error as FormattedApiError).status;
  return status === 401 || status === 403;
}

/**
 * Check if error is a rate limit error (429)
 */
export function isRateLimitError(error: unknown): boolean {
  if (!error || typeof error !== 'object') return false;
  return (error as FormattedApiError).status === 429;
}

// ============================================================================
// Retry Logic
// ============================================================================

/**
 * Retry an async operation with exponential backoff
 *
 * @example
 * ```ts
 * const data = await withRetry(
 *   () => apiService.getOEE(),
 *   {
 *     maxRetries: 3,
 *     initialDelay: 1000,
 *     shouldRetry: (error) => isNetworkError(error) || isServerError(error)
 *   }
 * );
 * ```
 */
export async function withRetry<T>(
  asyncFunction: () => Promise<T>,
  options: RetryOptions = {}
): Promise<T> {
  const {
    maxRetries = 3,
    initialDelay = 1000,
    maxDelay = 10000,
    backoffFactor = 2,
    shouldRetry = (error) => isNetworkError(error) || isServerError(error),
  } = options;

  let lastError: unknown;
  let delay = initialDelay;

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await asyncFunction();
    } catch (error) {
      lastError = error;

      // Don't retry if this was the last attempt
      if (attempt === maxRetries) {
        break;
      }

      // Don't retry if custom condition says not to
      if (!shouldRetry(error)) {
        break;
      }

      // Wait before retrying
      await sleep(Math.min(delay, maxDelay));

      // Exponential backoff
      delay *= backoffFactor;
    }
  }

  // All retries exhausted, throw the last error
  throw lastError;
}

/**
 * Sleep utility for delays
 */
function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

// ============================================================================
// Loading Patterns
// ============================================================================

/**
 * Create array of skeleton placeholders for loading states
 * Useful for rendering skeleton loaders
 *
 * @example
 * ```tsx
 * {loading && createSkeletonArray(5).map((_, index) => (
 *   <Skeleton key={index} variant="rectangular" height={60} />
 * ))}
 * ```
 */
export function createSkeletonArray(count: number): number[] {
  return Array.from({ length: count }, (_, i) => i);
}

/**
 * Debounce function to limit function call frequency
 * Useful for search inputs and real-time filtering
 *
 * @example
 * ```tsx
 * const debouncedSearch = useCallback(
 *   debounce((query: string) => {
 *     fetchResults(query);
 *   }, 300),
 *   []
 * );
 * ```
 */
export function debounce<T extends (...args: unknown[]) => unknown>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: ReturnType<typeof setTimeout> | null = null;

  return function executedFunction(...args: Parameters<T>) {
    const later = () => {
      timeout = null;
      func(...args);
    };

    if (timeout !== null) {
      clearTimeout(timeout);
    }
    timeout = setTimeout(later, wait);
  };
}
