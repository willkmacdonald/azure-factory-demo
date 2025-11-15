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

// ============================================================================
// Supply Chain Traceability Types (from backend/src/api/routes/traceability.py)
// ============================================================================

/**
 * Supplier Information
 * GET /api/suppliers, GET /api/suppliers/{supplier_id}
 */
export interface Supplier {
  id: string;                             // e.g., "SUP-001"
  name: string;                           // Supplier name
  type: string;                           // e.g., "Raw Materials", "Components", "Fasteners"
  materials_supplied: string[];           // List of material IDs
  contact: {                              // Contact information
    email?: string;
    phone?: string;
    address?: string;
    [key: string]: string | undefined;
  };
  quality_metrics: {                      // Quality performance metrics
    quality_rating?: number;
    on_time_delivery_rate?: number;
    defect_rate?: number;
    [key: string]: number | undefined;
  };
  certifications: string[];               // e.g., ["ISO9001", "AS9100"]
  status: 'Active' | 'OnHold' | 'Suspended';  // Supplier status
}

/**
 * Material Specification
 * Used in traceability responses
 */
export interface MaterialSpec {
  id: string;                             // e.g., "MAT-001"
  name: string;                           // e.g., "Steel Bar 304 Stainless"
  category: string;                       // e.g., "Steel", "Fasteners", "Components"
  specification: string;                  // e.g., "ASTM A479 Grade 304"
  unit: string;                           // e.g., "kg", "pieces", "meters"
  preferred_suppliers: string[];          // List of preferred supplier IDs
  quality_requirements: Record<string, string>;  // Custom quality requirements
}

/**
 * Material Lot
 * Tracks specific lots of materials received from suppliers
 */
export interface MaterialLot {
  lot_number: string;                     // e.g., "LOT-20240115-001"
  material_id: string;                    // Reference to MaterialSpec.id
  supplier_id: string;                    // Reference to Supplier.id
  received_date: string;                  // YYYY-MM-DD format
  quantity_received: number;              // Quantity received
  quantity_remaining: number;             // Quantity remaining (updated as consumed)
  inspection_results: {                   // Inspection/quality control results
    status?: string;
    inspector?: string;
    notes?: string;
    test_results?: string;
    [key: string]: string | undefined;
  };
  status: 'Available' | 'InUse' | 'Depleted' | 'Quarantine' | 'Rejected';
  quarantine: boolean;                    // Quarantine flag
}

/**
 * Material Usage
 * Tracks materials consumed in production batches
 */
export interface MaterialUsage {
  material_id: string;                    // Reference to MaterialSpec.id
  material_name: string;                  // Material name for display
  lot_number: string;                     // Reference to MaterialLot.lot_number
  quantity_used: number;                  // Quantity consumed
  unit: string;                           // Unit of measurement
}

/**
 * Order Item
 * Line item within an order
 */
export interface OrderItem {
  part_number: string;                    // Part number
  quantity: number;                       // Quantity ordered (>= 1)
  unit_price: number;                     // Unit price (>= 0)
}

/**
 * Customer Order
 * GET /api/orders, GET /api/orders/{order_id}
 */
export interface Order {
  id: string;                             // e.g., "ORD-001"
  order_number: string;                   // e.g., "PO-2024-1000"
  customer: string;                       // Customer name
  items: OrderItem[];                     // Order line items
  due_date: string;                       // Due date (YYYY-MM-DD)
  status: 'Pending' | 'InProgress' | 'Completed' | 'Shipped' | 'Delayed';
  priority: 'Low' | 'Normal' | 'High' | 'Urgent';
  shipping_date: string | null;           // Actual/planned shipping date (YYYY-MM-DD) or null
  total_value: number;                    // Total order value in dollars
}

/**
 * Production Batch
 * GET /api/batches, GET /api/batches/{batch_id}
 */
export interface ProductionBatch {
  batch_id: string;                       // e.g., "BATCH-20240115-CNC001-001"
  date: string;                           // Production date (YYYY-MM-DD)
  machine_id: number;                     // Machine ID
  machine_name: string;                   // Machine name (e.g., "CNC-001")
  shift_id: number;                       // Shift ID (1=Day, 2=Night)
  shift_name: string;                     // Shift name ("Day" or "Night")
  order_id: string | null;                // Associated order ID or null
  part_number: string;                    // Part number produced
  operator: string;                       // Operator name/ID

  // Production quantities
  parts_produced: number;                 // Total parts produced
  good_parts: number;                     // Good parts count
  scrap_parts: number;                    // Scrap parts count

  // Serial number tracking
  serial_start: number | null;            // Starting serial number
  serial_end: number | null;              // Ending serial number

  // Material traceability
  materials_consumed: MaterialUsage[];    // Materials used in this batch

  // Quality tracking
  quality_issues: QualityIssue[];         // Quality issues encountered

  // Process parameters
  process_parameters: Record<string, number> | null;  // temperature, pressure, speed, etc.

  // Timing
  start_time: string | null;              // Start time (HH:MM)
  end_time: string | null;                // End time (HH:MM)
  duration_hours: number | null;          // Duration in hours
}

/**
 * Supplier Impact Analysis
 * GET /api/suppliers/{supplier_id}/impact
 */
export interface SupplierImpact {
  supplier: Supplier;                     // Supplier information
  material_lots_supplied: number;         // Number of lots supplied
  affected_batches_count: number;         // Number of batches using this supplier's materials
  quality_issues_count: number;           // Number of quality issues in affected batches
  total_defects: number;                  // Total defective parts
  estimated_cost_impact: number;          // Estimated cost impact in dollars
  material_lots: MaterialLot[];           // List of material lots supplied
  affected_batches: Array<{               // Batches using this supplier's materials
    batch_id: string;
    date: string;
    machine_name: string;
    parts_produced: number;
    scrap_parts: number;
    materials_consumed: MaterialUsage[];
  }>;
  quality_issues: Array<{                 // Quality issues in affected batches
    batch_id: string;
    date: string;
    defect_count: number;
    defect_types: string[];
  }>;
}

/**
 * Backward Traceability Result
 * GET /api/traceability/backward/{batch_id}
 */
export interface BackwardTrace {
  batch: ProductionBatch;                 // The production batch
  materials_trace: Array<{                // Materials used and their origins
    material_id: string;
    material_name: string;
    material_spec: MaterialSpec | null;
    quantity_used: number;
    unit: string;
    lot_number: string;
    lot_details: MaterialLot;
    supplier_id: string;
    supplier: Supplier | null;
  }>;
  suppliers: Supplier[];                  // All suppliers involved
  supply_chain_summary: {                 // Summary statistics
    materials_count: number;
    suppliers_count: number;
    total_parts_produced: number;
    scrap_parts: number;
    quality_rate: number;
  };
}

/**
 * Forward Traceability Result
 * GET /api/traceability/forward/{supplier_id}
 */
export interface ForwardTrace {
  supplier: Supplier;                     // Supplier information
  material_lots_supplied: number;         // Number of lots supplied
  affected_batches: Array<{               // Batches using this supplier's materials
    batch_id: string;
    date: string;
    machine_name: string;
    parts_produced: number;
    scrap_parts: number;
    order_id?: string;
  }>;
  quality_issues: Array<{                 // Quality issues in affected batches
    batch_id: string;
    date: string;
    defect_count: number;
  }>;
  affected_orders: Order[];               // Orders affected by this supplier
  impact_summary: {                       // Impact summary
    batches_affected: number;
    quality_issues_count: number;
    total_defects: number;
    orders_affected: number;
    estimated_cost_impact: number;
  };
}

/**
 * Order Production Batches
 * GET /api/orders/{order_id}/batches
 */
export interface OrderBatches {
  order: Order;                           // Order information
  assigned_batches: ProductionBatch[];    // Batches assigned to this order
  production_summary: {                   // Production summary for the order
    batches_count: number;
    total_produced: number;
    total_good_parts: number;
    total_scrap: number;
    quality_rate: number;
  };
}
