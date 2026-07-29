import { MOCK_REVIEWS, MOCK_AGENT_HEALTH, MOCK_PR_COSTS, MOCK_TRACE_SPANS } from './fixtures';
import { ReviewState, AgentHealth, PRCost, TraceSpan } from './types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function fetchHealth(): Promise<{ status: string; service: string; version: string }> {
  try {
    const res = await fetch(`${API_BASE}/health`);
    if (!res.ok) throw new Error('Health check failed');
    return await res.json();
  } catch {
    return { status: 'healthy (fixture mode)', service: 'pr-prep-backend', version: '0.1.0' };
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

export async function fetchAgentHealth(): Promise<AgentHealth[]> {
  return MOCK_AGENT_HEALTH;
}

export async function fetchPRCosts(): Promise<PRCost[]> {
  return MOCK_PR_COSTS;
}

export async function fetchTraceSpans(reviewId: string): Promise<TraceSpan[]> {
  return MOCK_TRACE_SPANS;
}
