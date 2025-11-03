/**
 * TypeScript interfaces matching backend Pydantic models
 *
 * These types correspond to the FastAPI backend API responses
 * defined in backend/src/api/routes/*.py
 */

// ============================================================================
// Metrics Response Types (from backend/shared/models.py)
// ============================================================================

/**
 * OEE (Overall Equipment Effectiveness) Metrics
 * GET /api/metrics/oee
 */
export interface OEEMetrics {
  oee: number;                    // Overall Equipment Effectiveness (0-1)
  availability: number;           // Availability component (0-1)
  performance: number;            // Performance component (0-1)
  quality: number;                // Quality component (0-1)
  total_parts: number;            // Total parts produced
  good_parts: number;             // Good parts produced
  scrap_parts: number;            // Scrap parts produced
}

/**
 * Scrap/Waste Metrics
 * GET /api/metrics/scrap
 */
export interface ScrapMetrics {
  total_scrap: number;            // Total scrap count
  total_parts: number;            // Total parts produced
  scrap_rate: number;             // Scrap rate as percentage (0-100)
  scrap_by_machine?: Record<string, number>;  // Optional: scrap count per machine
}

/**
 * Individual Quality Issue
 * Part of QualityIssues response
 */
export interface QualityIssue {
  type: string;                   // Issue type/category
  description: string;            // Issue description
  parts_affected: number;         // Number of parts affected
  severity: 'Low' | 'Medium' | 'High';  // Issue severity
  date: string;                   // Date in YYYY-MM-DD format
  machine: string;                // Machine identifier
}

/**
 * Quality Issues Collection with Statistics
 * GET /api/metrics/quality
 */
export interface QualityIssues {
  issues: QualityIssue[];         // List of quality issues
  total_issues: number;           // Total count of issues
  total_parts_affected: number;   // Total parts affected across all issues
  severity_breakdown: Record<string, number>;  // Count by severity level
}

/**
 * Major Downtime Event (>2 hours)
 * Part of DowntimeAnalysis response
 */
export interface MajorDowntimeEvent {
  date: string;                   // Date in YYYY-MM-DD format
  machine: string;                // Machine identifier
  reason: string;                 // Downtime reason/category
  description: string;            // Detailed description
  duration_hours: number;         // Duration in hours
}

/**
 * Downtime Analysis Summary
 * GET /api/metrics/downtime
 */
export interface DowntimeAnalysis {
  total_downtime_hours: number;   // Total downtime in hours
  downtime_by_reason: Record<string, number>;  // Hours by reason category
  major_events: MajorDowntimeEvent[];  // Events with duration > 2 hours
}

// ============================================================================
// Chat API Types (from backend/src/api/routes/chat.py)
// ============================================================================

/**
 * Chat Message
 * Used in conversation history
 */
export interface ChatMessage {
  role: 'user' | 'assistant';     // Message sender role
  content: string;                // Message content (1-2000 chars)
}

/**
 * Chat Request Payload
 * POST /api/chat
 */
export interface ChatRequest {
  message: string;                // User message (1-2000 chars)
  history?: ChatMessage[];        // Optional conversation history (max 50 messages)
}

/**
 * Chat Response
 * POST /api/chat
 */
export interface ChatResponse {
  response: string;               // AI assistant response
  history: ChatMessage[];         // Updated conversation history
}

// ============================================================================
// Data Management Types (from backend/src/api/routes/data.py)
// ============================================================================

/**
 * Setup Request Payload
 * POST /api/setup
 */
export interface SetupRequest {
  days?: number;                  // Number of days of data to generate (1-365, default: 30)
}

/**
 * Setup Response
 * POST /api/setup
 */
export interface SetupResponse {
  message: string;                // Success message
  days: number;                   // Days of data generated
  start_date: string;             // Start date (YYYY-MM-DD)
  end_date: string;               // End date (YYYY-MM-DD)
  machines: number;               // Number of machines generated
}

/**
 * Data Statistics Response
 * GET /api/stats
 */
export interface StatsResponse {
  exists: boolean;                // Whether data exists
  start_date?: string;            // Optional: start date if data exists
  end_date?: string;              // Optional: end date if data exists
  total_days?: number;            // Optional: total days if data exists
  total_machines?: number;        // Optional: machine count if data exists
  total_records?: number;         // Optional: total records if data exists
}

/**
 * Machine Information
 * GET /api/machines
 */
export interface MachineInfo {
  id: number;                     // Machine identifier
  name: string;                   // Machine display name
  type: string;                   // Machine type/category
  ideal_cycle_time: number;       // Ideal cycle time in seconds
}

/**
 * Date Range Response
 * GET /api/date-range
 */
export interface DateRangeResponse {
  start_date: string;             // Start date (YYYY-MM-DD)
  end_date: string;               // End date (YYYY-MM-DD)
  total_days: number;             // Total days in range
}

// ============================================================================
// Common Types
// ============================================================================

/**
 * Health Check Response
 * GET /health
 */
export interface HealthResponse {
  status: 'healthy';              // Always returns "healthy" if API is up
}

/**
 * API Error Response
 * Returned when endpoints encounter errors
 */
export interface ApiError {
  error: string;                  // Error message
  detail?: string;                // Optional detailed error information
}

/**
 * Query Parameters for Metrics Endpoints
 * Used by: /api/metrics/oee, /api/metrics/scrap, /api/metrics/quality, /api/metrics/downtime
 */
export interface MetricsQueryParams {
  start_date?: string;            // Optional: filter start date (YYYY-MM-DD)
  end_date?: string;              // Optional: filter end date (YYYY-MM-DD)
  machine?: string;               // Optional: filter by machine name
  severity?: 'Low' | 'Medium' | 'High';  // Optional: filter by severity (quality endpoint only)
}

/**
 * Type guard to check if response is an error
 */
export function isApiError(response: unknown): response is ApiError {
  return (
    typeof response === 'object' &&
    response !== null &&
    'error' in response &&
    typeof (response as ApiError).error === 'string'
  );
}
