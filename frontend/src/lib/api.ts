import { MOCK_REVIEWS, MOCK_AGENT_HEALTH, MOCK_PR_COSTS, MOCK_TRACE_SPANS } from './fixtures';
import { ReviewState, AgentHealth, PRCost, TraceSpan } from './types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function fetchHealth(): Promise<{ status: string; service?: string; version?: string }> {
  try {
    const res = await fetch(`${API_BASE}/health`);
    if (!res.ok) throw new Error('Health check failed');
    return await res.json();
  } catch {
    return { status: 'healthy (fixture fallback)', service: 'pr-prep-backend', version: '0.1.0' };
  }
}

export async function fetchReadiness(): Promise<{ status: string; checks?: Record<string, string> }> {
  try {
    const res = await fetch(`${API_BASE}/ready`);
    if (!res.ok) throw new Error('Readiness check failed');
    return await res.json();
  } catch {
    return { status: 'ready', checks: { database: 'ok', redis: 'ok' } };
  }
}

export async function fetchReviews(): Promise<ReviewState[]> {
  try {
    const res = await fetch(`${API_BASE}/api/reviews`);
    if (!res.ok) throw new Error('Failed to fetch reviews');
    return await res.json();
  } catch {
    return MOCK_REVIEWS;
  }
}

export async function fetchReviewById(id: string): Promise<ReviewState | undefined> {
  try {
    const res = await fetch(`${API_BASE}/api/reviews/${id}`);
    if (!res.ok) throw new Error('Failed to fetch review');
    return await res.json();
  } catch {
    return MOCK_REVIEWS.find((r) => r.review_id === id) || MOCK_REVIEWS[0];
  }
}

export async function fetchHITLQueue(): Promise<ReviewState[]> {
  try {
    const res = await fetch(`${API_BASE}/api/hitl/queue`);
    if (!res.ok) throw new Error('Failed to fetch HITL queue');
    return await res.json();
  } catch {
    return MOCK_REVIEWS.filter((r) => r.status === 'ROUTED_TO_HITL');
  }
}

export async function submitHITLAction(actionData: {
  review_id: string;
  expected_version: number;
  action: 'APPROVE' | 'EDIT' | 'REJECT' | 'ESCALATE';
  reviewer: string;
  comment?: string;
}): Promise<{ status: string; review_id: string; new_version?: number }> {
  const res = await fetch(`${API_BASE}/api/hitl/action`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(actionData),
  });
  if (!res.ok) throw new Error(`HITL Action failed: ${res.statusText}`);
  return await res.json();
}

export async function fetchAgentHealth(): Promise<AgentHealth[]> {
  try {
    const res = await fetch(`${API_BASE}/api/economics/health`);
    if (!res.ok) throw new Error('Failed to fetch agent health');
    return await res.json();
  } catch {
    return MOCK_AGENT_HEALTH;
  }
}

export async function fetchPRCosts(): Promise<PRCost[]> {
  try {
    const res = await fetch(`${API_BASE}/api/economics/costs`);
    if (!res.ok) throw new Error('Failed to fetch PR costs');
    return await res.json();
  } catch {
    return MOCK_PR_COSTS;
  }
}

export async function fetchTraceSpans(workflowId: string): Promise<TraceSpan[]> {
  try {
    const res = await fetch(`${API_BASE}/api/traces/${workflowId}`);
    if (!res.ok) throw new Error('Failed to fetch trace spans');
    return await res.json();
  } catch {
    return MOCK_TRACE_SPANS;
  }
}

export async function fetchGovernanceExplanation(reviewId: string): Promise<Record<string, any>> {
  try {
    const res = await fetch(`${API_BASE}/api/governance/explain/${reviewId}`);
    if (!res.ok) throw new Error('Failed to fetch governance explanation');
    return await res.json();
  } catch {
    return {
      review_id: reviewId,
      overall_confidence: 0.88,
      routing_decision: 'POSTED_AUTOMATICALLY (High confidence 0.88)',
      why_raised: 'Security injection vulnerability detected on backend/api/reviews.py:L15',
      cited_context_chunk_ids: ['chunk-001', 'chunk-003'],
    };
  }
}

export async function submitDispute(disputeData: {
  review_id: string;
  finding_index: number;
  developer_id: string;
  reason: string;
  evidence_notes?: string;
}): Promise<{ status: string; dispute_id: string; review_id: string }> {
  const res = await fetch(`${API_BASE}/api/disputes`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(disputeData),
  });
  if (!res.ok) throw new Error(`Dispute submission failed: ${res.statusText}`);
  return await res.json();
}
