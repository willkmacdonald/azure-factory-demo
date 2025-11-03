// API Client Service for Factory Agent Backend

import axios, { type AxiosInstance } from 'axios';
import type {
  Machine,
  OEEMetrics,
  ScrapMetrics,
  QualityIssues,
  DowntimeAnalysis,
  ChatMessage,
  DateRange,
  DataStats,
} from '../types';

// Create axios instance with base configuration
const apiClient: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 second timeout
});

// Request/Response types for chat endpoint
export interface ChatRequest {
  message: string;
  history: ChatMessage[];
}

export interface ChatResponse {
  response: string;
  history: ChatMessage[];
}

// Setup request interface
export interface SetupRequest {
  days?: number;
}

export interface SetupResponse {
  message: string;
  days: number;
  start_date: string;
  end_date: string;
  machines: number;
}

/**
 * API Service - centralized API calls to backend
 */
export const apiService = {
  // System endpoints
  checkHealth: () => apiClient.get<{ status: string }>('/health'),

  // Data management endpoints
  generateData: (days?: number) =>
    apiClient.post<SetupResponse>('/api/setup', { days: days || 30 }),

  getStats: () => apiClient.get<DataStats>('/api/stats'),

  getMachines: () => apiClient.get<Machine[]>('/api/machines'),

  getDateRange: () => apiClient.get<DateRange>('/api/date-range'),

  // Metrics endpoints
  getOEE: (startDate: string, endDate: string, machine?: string) =>
    apiClient.get<OEEMetrics>('/api/metrics/oee', {
      params: {
        start_date: startDate,
        end_date: endDate,
        ...(machine && { machine }),
      },
    }),

  getScrap: (startDate: string, endDate: string, machine?: string) =>
    apiClient.get<ScrapMetrics>('/api/metrics/scrap', {
      params: {
        start_date: startDate,
        end_date: endDate,
        ...(machine && { machine }),
      },
    }),

  getQuality: (
    startDate: string,
    endDate: string,
    severity?: string,
    machine?: string
  ) =>
    apiClient.get<QualityIssues>('/api/metrics/quality', {
      params: {
        start_date: startDate,
        end_date: endDate,
        ...(severity && { severity }),
        ...(machine && { machine }),
      },
    }),

  getDowntime: (startDate: string, endDate: string, machine?: string) =>
    apiClient.get<DowntimeAnalysis>('/api/metrics/downtime', {
      params: {
        start_date: startDate,
        end_date: endDate,
        ...(machine && { machine }),
      },
    }),

  // Chat endpoint
  chat: (request: ChatRequest) =>
    apiClient.post<ChatResponse>('/api/chat', request),
};

export default apiService;
