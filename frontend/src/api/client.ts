/**
 * API Client Service for Factory Agent Backend
 *
 * Centralized Axios-based API client with:
 * - Request/response interceptors
 * - Error handling and formatting
 * - Type-safe API methods
 * - Timeout and retry configuration
 */

import axios, { type AxiosInstance, type AxiosError, type AxiosResponse } from 'axios';
import type {
  HealthResponse,
  OEEMetrics,
  ScrapMetrics,
  QualityIssues,
  DowntimeAnalysis,
  ChatRequest,
  ChatResponse,
  SetupRequest,
  SetupResponse,
  StatsResponse,
  MachineInfo,
  DateRangeResponse,
  MetricsQueryParams,
  ApiError,
  Supplier,
  SupplierImpact,
  ProductionBatch,
  BackwardTrace,
  ForwardTrace,
  Order,
  OrderBatches,
} from '../types/api';

// ============================================================================
// Configuration
// ============================================================================

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const REQUEST_TIMEOUT = 30000; // 30 seconds

// ============================================================================
// Axios Instance Configuration
// ============================================================================

/**
 * Create axios instance with base configuration
 */
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: REQUEST_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ============================================================================
// Interceptors
// ============================================================================

/**
 * Request interceptor
 * - Logs outgoing requests in development mode
 * - Can be extended to add auth tokens
 */
apiClient.interceptors.request.use(
  (config) => {
    // Log requests in development
    if (import.meta.env.DEV) {
      console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`, config.params || '');
    }
    return config;
  },
  (error) => {
    console.error('[API] Request error:', error);
    return Promise.reject(error);
  }
);

/**
 * Response interceptor
 * - Logs responses in development mode
 * - Handles common error scenarios
 */
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    // Log responses in development
    if (import.meta.env.DEV) {
      console.log(`[API] Response from ${response.config.url}:`, response.status);
    }
    return response;
  },
  (error: AxiosError) => {
    // Log errors
    console.error('[API] Response error:', {
      url: error.config?.url,
      status: error.response?.status,
      message: error.message,
      data: error.response?.data,
    });

    // Format error for consistent handling
    return Promise.reject(formatApiError(error));
  }
);

// ============================================================================
// Error Handling Utilities
// ============================================================================

/**
 * Formatted API error for consistent error handling
 */
export interface FormattedApiError {
  message: string;
  status?: number;
  code?: string;
  isNetworkError: boolean;
  isTimeoutError: boolean;
  isServerError: boolean;
  isClientError: boolean;
  originalError: AxiosError;
}

/**
 * Format Axios errors into consistent error structure
 */
function formatApiError(error: AxiosError): FormattedApiError {
  const formatted: FormattedApiError = {
    message: 'An unexpected error occurred',
    isNetworkError: !error.response,
    isTimeoutError: error.code === 'ECONNABORTED',
    isServerError: false,
    isClientError: false,
    originalError: error,
  };

  // Network or timeout errors
  if (formatted.isNetworkError) {
    formatted.message = formatted.isTimeoutError
      ? 'Request timeout - please try again'
      : 'Network error - please check your connection';
    return formatted;
  }

  // HTTP status errors
  if (error.response) {
    formatted.status = error.response.status;

    // Server errors (5xx)
    if (error.response.status >= 500) {
      formatted.isServerError = true;
      formatted.message = 'Server error - please try again later';
    }
    // Client errors (4xx)
    else if (error.response.status >= 400) {
      formatted.isClientError = true;

      // Extract error message from response
      const responseData = error.response.data as ApiError | { detail?: string };
      if (responseData && 'error' in responseData) {
        formatted.message = responseData.error;
      } else if (responseData && 'detail' in responseData && responseData.detail) {
        formatted.message = responseData.detail;
      } else {
        // Default messages for common status codes
        switch (error.response.status) {
          case 400:
            formatted.message = 'Invalid request';
            break;
          case 404:
            formatted.message = 'Resource not found';
            break;
          case 429:
            formatted.message = 'Too many requests - please wait and try again';
            break;
          default:
            formatted.message = `Request failed with status ${error.response.status}`;
        }
      }
    }
  }

  return formatted;
}

/**
 * Extract error message from FormattedApiError
 */
export function getErrorMessage(error: unknown): string {
  if (typeof error === 'string') {
    return error;
  }
  if (error && typeof error === 'object' && 'message' in error) {
    return (error as FormattedApiError).message;
  }
  return 'An unexpected error occurred';
}

/**
 * Check if a successful API response contains a business error
 * Some endpoints return { error: string } with 200 OK status when there's no data
 *
 * Example: GET /api/metrics/oee returns { error: "No data found" } with 200 OK
 * when there are no production records matching the query parameters.
 */
export function isBusinessError(data: unknown): data is ApiError {
  return (
    data !== null &&
    typeof data === 'object' &&
    'error' in data &&
    typeof (data as ApiError).error === 'string'
  );
}

// ============================================================================
// API Service Methods
// ============================================================================

/**
 * API Service - centralized API calls to backend
 * All methods return Axios responses with typed data
 */
export const apiService = {
  // ========================================
  // Health Check
  // ========================================

  /**
   * Check API health status
   * GET /health
   */
  checkHealth: async (): Promise<HealthResponse> => {
    const response = await apiClient.get<HealthResponse>('/health');
    return response.data;
  },

  // ========================================
  // Data Management
  // ========================================

  /**
   * Generate production data
   * POST /api/setup
   * Rate limit: 5 requests/minute
   */
  generateData: async (request?: SetupRequest): Promise<SetupResponse> => {
    const response = await apiClient.post<SetupResponse>('/api/setup', request || {});
    return response.data;
  },

  /**
   * Get data statistics
   * GET /api/stats
   */
  getStats: async (): Promise<StatsResponse> => {
    const response = await apiClient.get<StatsResponse>('/api/stats');
    return response.data;
  },

  /**
   * Get list of machines
   * GET /api/machines
   */
  getMachines: async (): Promise<MachineInfo[]> => {
    const response = await apiClient.get<MachineInfo[]>('/api/machines');
    return response.data;
  },

  /**
   * Get date range of available data
   * GET /api/date-range
   * Returns 404 if no data exists
   */
  getDateRange: async (): Promise<DateRangeResponse> => {
    const response = await apiClient.get<DateRangeResponse>('/api/date-range');
    return response.data;
  },

  // ========================================
  // Metrics Endpoints
  // ========================================

  /**
   * Get OEE (Overall Equipment Effectiveness) metrics
   * GET /api/metrics/oee
   */
  getOEE: async (params?: MetricsQueryParams): Promise<OEEMetrics> => {
    const response = await apiClient.get<OEEMetrics | ApiError>('/api/metrics/oee', {
      params: {
        ...(params?.start_date && { start_date: params.start_date }),
        ...(params?.end_date && { end_date: params.end_date }),
        ...(params?.machine && { machine: params.machine }),
      },
    });

    // Check for business error in successful response
    if (isBusinessError(response.data)) {
      throw new Error(response.data.error);
    }

    return response.data;
  },

  /**
   * Get scrap/waste metrics
   * GET /api/metrics/scrap
   */
  getScrap: async (params?: MetricsQueryParams): Promise<ScrapMetrics> => {
    const response = await apiClient.get<ScrapMetrics | ApiError>('/api/metrics/scrap', {
      params: {
        ...(params?.start_date && { start_date: params.start_date }),
        ...(params?.end_date && { end_date: params.end_date }),
        ...(params?.machine && { machine: params.machine }),
      },
    });

    // Check for business error in successful response
    if (isBusinessError(response.data)) {
      throw new Error(response.data.error);
    }

    return response.data;
  },

  /**
   * Get quality issues
   * GET /api/metrics/quality
   */
  getQuality: async (params?: MetricsQueryParams): Promise<QualityIssues> => {
    const response = await apiClient.get<QualityIssues | ApiError>('/api/metrics/quality', {
      params: {
        ...(params?.start_date && { start_date: params.start_date }),
        ...(params?.end_date && { end_date: params.end_date }),
        ...(params?.machine && { machine: params.machine }),
        ...(params?.severity && { severity: params.severity }),
      },
    });

    // Check for business error in successful response
    if (isBusinessError(response.data)) {
      throw new Error(response.data.error);
    }

    return response.data;
  },

  /**
   * Get downtime analysis
   * GET /api/metrics/downtime
   */
  getDowntime: async (params?: MetricsQueryParams): Promise<DowntimeAnalysis> => {
    const response = await apiClient.get<DowntimeAnalysis | ApiError>('/api/metrics/downtime', {
      params: {
        ...(params?.start_date && { start_date: params.start_date }),
        ...(params?.end_date && { end_date: params.end_date }),
        ...(params?.machine && { machine: params.machine }),
      },
    });

    // Check for business error in successful response
    if (isBusinessError(response.data)) {
      throw new Error(response.data.error);
    }

    return response.data;
  },

  // ========================================
  // Chat Endpoint
  // ========================================

  /**
   * Send chat message to AI assistant
   * POST /api/chat
   * Rate limit: 10 requests/minute
   */
  sendChatMessage: async (request: ChatRequest): Promise<ChatResponse> => {
    const response = await apiClient.post<ChatResponse>('/api/chat', request);
    return response.data;
  },

  // ========================================
  // Supply Chain Traceability - Suppliers
  // ========================================

  /**
   * Get list of suppliers
   * GET /api/suppliers
   * @param status - Optional: filter by supplier status (Active, OnHold, Suspended)
   */
  listSuppliers: async (status?: string): Promise<Supplier[]> => {
    const response = await apiClient.get<Supplier[]>('/api/suppliers', {
      params: status ? { status } : undefined,
    });
    return response.data;
  },

  /**
   * Get supplier details by ID
   * GET /api/suppliers/{supplier_id}
   */
  getSupplier: async (supplierId: string): Promise<Supplier> => {
    const response = await apiClient.get<Supplier>(`/api/suppliers/${supplierId}`);
    return response.data;
  },

  /**
   * Get supplier impact analysis
   * GET /api/suppliers/{supplier_id}/impact
   * Analyzes the impact of a supplier on production batches and quality
   */
  getSupplierImpact: async (supplierId: string): Promise<SupplierImpact> => {
    const response = await apiClient.get<SupplierImpact>(`/api/suppliers/${supplierId}/impact`);
    return response.data;
  },

  // ========================================
  // Supply Chain Traceability - Production Batches
  // ========================================

  /**
   * Get list of production batches
   * GET /api/batches
   * @param params - Optional query parameters for filtering
   */
  listBatches: async (params?: {
    machine_id?: number;
    start_date?: string;
    end_date?: string;
    order_id?: string;
    limit?: number;
  }): Promise<ProductionBatch[]> => {
    const response = await apiClient.get<ProductionBatch[]>('/api/batches', { params });
    return response.data;
  },

  /**
   * Get production batch details by ID
   * GET /api/batches/{batch_id}
   */
  getBatch: async (batchId: string): Promise<ProductionBatch> => {
    const response = await apiClient.get<ProductionBatch>(`/api/batches/${batchId}`);
    return response.data;
  },

  // ========================================
  // Supply Chain Traceability - Traceability
  // ========================================

  /**
   * Get backward traceability for a production batch
   * GET /api/traceability/backward/{batch_id}
   * Traces materials and suppliers used in a specific batch
   */
  getBackwardTrace: async (batchId: string): Promise<BackwardTrace> => {
    const response = await apiClient.get<BackwardTrace>(`/api/traceability/backward/${batchId}`);
    return response.data;
  },

  /**
   * Get forward traceability for a supplier
   * GET /api/traceability/forward/{supplier_id}
   * Traces impact of a supplier on batches and orders
   * @param supplierId - Supplier ID
   * @param params - Optional date range filter
   */
  getForwardTrace: async (
    supplierId: string,
    params?: { start_date?: string; end_date?: string }
  ): Promise<ForwardTrace> => {
    const response = await apiClient.get<ForwardTrace>(
      `/api/traceability/forward/${supplierId}`,
      { params }
    );
    return response.data;
  },

  // ========================================
  // Supply Chain Traceability - Orders
  // ========================================

  /**
   * Get list of customer orders
   * GET /api/orders
   * @param params - Optional query parameters for filtering
   */
  listOrders: async (params?: { status?: string; limit?: number }): Promise<Order[]> => {
    const response = await apiClient.get<Order[]>('/api/orders', { params });
    return response.data;
  },

  /**
   * Get order details by ID
   * GET /api/orders/{order_id}
   */
  getOrder: async (orderId: string): Promise<Order> => {
    const response = await apiClient.get<Order>(`/api/orders/${orderId}`);
    return response.data;
  },

  /**
   * Get production batches for an order
   * GET /api/orders/{order_id}/batches
   * Shows which batches have been assigned to fulfill this order
   */
  getOrderBatches: async (orderId: string): Promise<OrderBatches> => {
    const response = await apiClient.get<OrderBatches>(`/api/orders/${orderId}/batches`);
    return response.data;
  },
};

// ============================================================================
// Export
// ============================================================================

export default apiService;

/**
 * Export axios instance for advanced usage
 * (e.g., custom requests, file uploads)
 */
export { apiClient };
