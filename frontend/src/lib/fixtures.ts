import { Finding, ReviewState, AgentHealth, PRCost, TraceSpan } from './types';

export const MOCK_FINDINGS: Finding[] = [
  {
    id: 'f-1',
    agent_type: 'security',
    severity: 'CRITICAL',
    category: 'injection',
    summary: 'Unsanitized string interpolation in SQL query execution',
    file_path: 'backend/api/reviews.py',
    line_start: 42,
    line_end: 46,
    suggestion: 'await db.execute("SELECT * FROM reviews WHERE id = $1", review_id)',
    confidence: 0.96,
    rationale: 'User input raw query parameters directly injected into SQL string on line 44 without parameter binding.',
  },
  {
    id: 'f-2',
    agent_type: 'quality',
    severity: 'HIGH',
    category: 'logic_error',
    summary: 'Potential Null Pointer Dereference on missing token dictionary key',
    file_path: 'backend/integrations/github_client.py',
    line_start: 110,
    line_end: 115,
    suggestion: 'token = auth_data.get("token")\nif not token:\n    raise SecurityError("Missing token")',
    confidence: 0.88,
    rationale: 'Direct dictionary indexing auth_data["token"] without prior null check or default get.',
  },
  {
    id: 'f-3',
    agent_type: 'tests',
    severity: 'MEDIUM',
    category: 'missing_coverage',
    summary: 'Untested exception path in webhook HMAC validator',
    file_path: 'tests/test_webhook.py',
    line_start: 15,
    line_end: 25,
    suggestion: 'def test_hmac_signature_mismatch_raises_security_error(): ...',
    confidence: 0.82,
    rationale: 'HMAC signature verification mismatch branch has 0% coverage in pytest suite.',
  },
  {
    id: 'f-4',
    agent_type: 'docs',
    severity: 'LOW',
    category: 'outdated_doc',
    summary: 'Public function missing docstring arguments parameter description',
    file_path: 'backend/core/workflow_engine.py',
    line_start: 12,
    line_end: 18,
    suggestion: '"""Executes workflow step.\n\nArgs:\n    workflow_id: Unique workflow ID\n"""',
    confidence: 0.90,
    rationale: 'Public abstract method run() missing parameter type descriptions.',
  },
];

export const MOCK_REVIEWS: ReviewState[] = [
  {
    review_id: 'rev-001',
    workflow_id: 'wf-001',
    repository: 'acme/pr-prep-service',
    pr_number: 104,
    commit_sha: 'a1b2c3d4e5f6',
    status: 'ROUTED_TO_HITL',
    findings: MOCK_FINDINGS,
    overall_confidence: 0.89,
    auto_post_eligible: false,
    routing_decision: 'ROUTED_TO_HITL (Mandatory Escalation: CRITICAL finding present)',
    created_at: new Date(Date.now() - 3600000).toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    review_id: 'rev-002',
    workflow_id: 'wf-002',
    repository: 'acme/pr-prep-service',
    pr_number: 103,
    commit_sha: 'f6e5d4c3b2a1',
    status: 'POSTED_AUTOMATICALLY',
    findings: [MOCK_FINDINGS[2], MOCK_FINDINGS[3]],
    overall_confidence: 0.94,
    auto_post_eligible: true,
    routing_decision: 'POSTED_AUTOMATICALLY (High confidence 0.94, no CRITICAL findings)',
    created_at: new Date(Date.now() - 7200000).toISOString(),
    updated_at: new Date(Date.now() - 7100000).toISOString(),
  },
];

export const MOCK_AGENT_HEALTH: AgentHealth[] = [
  { agent: 'security', llm_calls: 1420, cost_usd: 12.45, p95_ms: 1100, rejection_rate: 0.02 },
  { agent: 'quality', llm_calls: 1850, cost_usd: 14.80, p95_ms: 950, rejection_rate: 0.04 },
  { agent: 'tests', llm_calls: 1100, cost_usd: 8.90, p95_ms: 820, rejection_rate: 0.01 },
  { agent: 'docs', llm_calls: 950, cost_usd: 4.30, p95_ms: 650, rejection_rate: 0.01 },
];

export const MOCK_PR_COSTS: PRCost[] = [
  { review_id: 'rev-001', repository: 'acme/pr-prep-service', pr_number: 104, total_cost_usd: 0.042, agents_used: 4, max_confidence: 0.96 },
  { review_id: 'rev-002', repository: 'acme/pr-prep-service', pr_number: 103, total_cost_usd: 0.028, agents_used: 4, max_confidence: 0.94 },
];

export const MOCK_TRACE_SPANS: TraceSpan[] = [
  { span_id: 's-1', agent: 'aggregator', event_type: 'span.start', timestamp: '2026-07-29T14:00:00Z' },
  { span_id: 's-2', parent_span: 's-1', agent: 'security', event_type: 'llm.call', model: 'gpt-4o', cost_usd: 0.012, latency_ms: 1150, outcome: 'findings_produced', confidence: 0.96, timestamp: '2026-07-29T14:00:01Z' },
  { span_id: 's-3', parent_span: 's-1', agent: 'quality', event_type: 'llm.call', model: 'gpt-4o', cost_usd: 0.010, latency_ms: 980, outcome: 'findings_produced', confidence: 0.88, timestamp: '2026-07-29T14:00:01Z' },
  { span_id: 's-4', parent_span: 's-1', agent: 'tests', event_type: 'llm.call', model: 'gpt-4o', cost_usd: 0.008, latency_ms: 810, outcome: 'findings_produced', confidence: 0.82, timestamp: '2026-07-29T14:00:01Z' },
  { span_id: 's-5', parent_span: 's-1', agent: 'docs', event_type: 'llm.call', model: 'gpt-4o', cost_usd: 0.005, latency_ms: 640, outcome: 'findings_produced', confidence: 0.90, timestamp: '2026-07-29T14:00:01Z' },
  { span_id: 's-6', parent_span: 's-1', agent: 'aggregator', event_type: 'decision', outcome: 'ROUTED_TO_HITL', confidence: 0.89, timestamp: '2026-07-29T14:00:03Z' },
];
