export type Severity = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'INFO';

export type AgentType = 'security' | 'quality' | 'tests' | 'docs' | 'aggregator';

export type ReviewStatus =
  | 'PENDING'
  | 'RUNNING'
  | 'COMPLETED'
  | 'POSTED_AUTOMATICALLY'
  | 'ROUTED_TO_HITL'
  | 'ESCALATED'
  | 'FAILED';

export type QueueState = 'QUEUED' | 'IN_REVIEW' | 'APPROVED' | 'REJECTED' | 'DISPUTED';

export interface Finding {
  id: string;
  agent_type: AgentType;
  severity: Severity;
  category: string;
  summary: string;
  file_path: string;
  line_start: number;
  line_end: number;
  suggestion?: string;
  confidence: number;
  rationale: string;
}

export interface ReviewState {
  review_id: string;
  workflow_id: string;
  repository: string;
  pr_number: number;
  commit_sha: string;
  status: ReviewStatus;
  findings: Finding[];
  overall_confidence: number;
  auto_post_eligible: boolean;
  routing_decision: string;
  created_at: string;
  updated_at: string;
  metadata?: Record<string, any>;
}

export interface AgentHealth {
  agent: AgentType;
  llm_calls: number;
  cost_usd: number;
  p95_ms: number;
  rejection_rate: number;
}

export interface PRCost {
  review_id: string;
  repository: string;
  pr_number: number;
  total_cost_usd: number;
  agents_used: number;
  max_confidence: number;
}

export interface TraceSpan {
  span_id: string;
  parent_span?: string;
  agent: AgentType;
  event_type: string;
  model?: string;
  cost_usd?: number;
  latency_ms?: number;
  outcome?: string;
  confidence?: number;
  timestamp: string;
}
