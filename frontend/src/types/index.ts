// Type definitions for Factory Agent Frontend

export interface Machine {
  id: number;
  name: string;
  type: string;
  ideal_cycle_time: number;
}

export interface OEEMetrics {
  oee: number;
  availability: number;
  performance: number;
  quality: number;
  produced_units: number;
  defective_units: number;
}

export interface ScrapMetrics {
  total_scrap: number;
  scrap_rate: number;
  by_machine: Record<string, number>;
}

export interface QualityIssue {
  date: string;
  machine: string;
  defect_type: string;
  quantity: number;
  severity: 'Low' | 'Medium' | 'High';
  description: string;
}

export interface QualityIssues {
  total_issues: number;
  by_severity: Record<string, number>;
  issues: QualityIssue[];
}

export interface DowntimeEvent {
  date: string;
  machine: string;
  reason: string;
  duration_hours: number;
  severity: 'Critical' | 'Major' | 'Minor';
}

export interface DowntimeAnalysis {
  total_downtime: number;
  by_reason: Record<string, number>;
  major_events: DowntimeEvent[];
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface DateRange {
  start_date: string;
  end_date: string;
  total_days: number;
}

export interface DataStats {
  exists: boolean;
  start_date: string;
  end_date: string;
  total_days: number;
  total_machines: number;
  total_records: number;
}
