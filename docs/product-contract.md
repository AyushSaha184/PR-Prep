# PR Prep — Product Contract and Autonomy Policy

## 1. Product Boundaries

### Ingress Trigger
- **Event:** GitHub `pull_request` webhook (`opened`, `synchronize`, `reopened`).
- **Input Payload:** GitHub event JSON carrying repository details, PR metadata, commit SHA, and delivery ID (`X-GitHub-Delivery`).
- **Validation:** HMAC-SHA256 signature verification via `X-Hub-Signature-256` before parsing or processing.
- **Idempotency:** Unique reservation on `X-GitHub-Delivery` key. Replayed deliveries return HTTP `200 OK` immediately without re-executing review jobs.

### Structured Output
- **Primary Contract:** A unified `Review` containing zero or more evidence-backed `Finding` records.
- **Finding Fields:**
  - `agent_type`: `security`, `quality`, `tests`, or `docs`
  - `severity`: `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, `INFO`
  - `category`: Category string (e.g., `injection`, `logic_error`, `missing_coverage`, `outdated_doc`)
  - `summary`: One-line summary
  - `file_path`: Exact repository file path
  - `line_start` / `line_end`: Precise line numbers validated against PR diff
  - `suggestion`: Remediation code snippet or guidance
  - `confidence`: Calibrated float score `[0.0, 1.0]`
  - `rationale`: Auditable reasoning citing retrieved repository evidence

### Target Users & Stated Purpose
- **Target Audience:** Senior software engineers, engineering managers, and security auditors.
- **Core Purpose:** Reclaim senior reviewer attention by automating mechanical pattern recognition (code smells, missing edge cases, security vulnerabilities, documentation drift) while escalating high-consequence or ambiguous cases to human judgment.
- **Quality Stance:** Selective, high-precision posture. Zero tolerance for ungrounded comments or comment flooding.

### Non-Goals
- Formatting/linting enforcement (handled by deterministic static linters in CI).
- Automated PR merging or direct code commits.
- Processing un-signed or untrusted external trigger sources.
- Autonomous prompt/model policy mutation from single-user feedback.

---

## 2. Human-in-the-Loop (HITL) Policy & Autonomy Matrix

PR Prep operates at Level 3 ("Human handles exceptions") of the HITL Spectrum.

| Case Condition | Action | Rationale |
| --- | --- | --- |
| High confidence ($\ge 0.85$), no `CRITICAL` findings, clean fan-out | Auto-post review to GitHub | Proven maturity earns autonomy for routine high-confidence findings. |
| Any `CRITICAL` finding (regardless of confidence) | Enqueue to HITL Approval Queue | High consequence of error; security/critical risks demand human review. |
| Aggregated review confidence $< 0.85$ | Enqueue to HITL Approval Queue | Uncertainty requires human verification before posting. |
| Incomplete agent execution or timeout | Enqueue to HITL Approval Queue | System degrades to slower-but-correct; never post partial/failed output. |
| Finding location invalid against PR diff | Enqueue to HITL Approval Queue / Summary fallback | Prevents misattributed inline comments. |
| Developer dispute filed on posted review | Enqueue to Dispute Queue & record feedback | Reversibility; audit trail and feedback loop integration. |

### Escalation SLAs & Ownership
- **Queue Priorities:** `CRITICAL` issues are assigned Priority 1 (SLA: 2 hours). High/Medium issues are Priority 2 (SLA: 24 hours).
- **Ownership:** Reviews in the HITL queue are claimed by authorized team reviewers.
- **Reviewer Actions:** Reviewers can `Approve` (post as-is), `Edit & Approve` (modify findings before posting), `Reject` (discard findings), or `Escalate` (page security/lead team).

---

## 3. Measurable Success Metrics

| Metric | Target Value | Description |
| --- | --- | --- |
| **Precision / Acceptance Rate** | $\ge 90\%$ | Percentage of posted findings approved or un-disputed by developers. |
| **Reviewer Time Saved** | $\ge 40\%$ | Reduction in human time spent reviewing routine PR diffs. |
| **Queue Age** | $< 4$ hours (p95) | Time an escalated review stays in the HITL queue before human action. |
| **Review Latency** | $< 3$ minutes (p95) | Ingress to review completion (post or queue insertion). |
| **Duplicate Post Rate** | $0.0\%$ | Duplicate GitHub reviews posted for the same delivery or commit. |
| **Retrieval Freshness** | 100% commit match | Context retrieval matches the exact commit SHA being reviewed. |
| **Daily Cost Limit** | Controlled by BudgetGuard | Max USD spend per day across all model/tool invocations. |
| **Developer Dispute Rate** | $< 5\%$ | Percentage of auto-posted reviews disputed by developers. |

---

## 4. Security & Data Handling Rules

1. **Secret Masking:** API keys, tokens, and credentials must be sanitized from logs, traces, event payloads, and UI displays.
2. **Untrusted Data Isolation:** PR descriptions, commit messages, diffs, and repository files are untrusted data. They are never interpreted as system instructions or tool execution commands.
3. **Data Retention:**
   - Detailed event traces: 90 days in `agent_events` hypertable.
   - Relational review records & audit logs: Indefinite (or per legal hold requirement).
4. **Audit Access:** RBAC rules restrict cross-tenant and raw payload access to authorized admin/auditor roles.
5. **Anti-Poisoning Policy:** Developer disputes and reviewer edits do not alter prompt registry or model routing automatically. Feedback must reach minimum evidence thresholds ($N \ge 20$ audited samples) before candidate evaluation.
