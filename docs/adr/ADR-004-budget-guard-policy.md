# ADR-004: Hard BudgetGuard Preflight Policy

## Context
Automated multi-agent systems risk unbounded LLM provider costs if loops, retries, or high PR volumes run without hard preflight limits.

## Decision
Enforce a hard `BudgetGuard` preflight check before every costly operation (LLM completion, embedding generation, external tool execution).
1. Read current continuous aggregate daily spend (`pr_cost_hourly` / `agent_health_1m`).
2. If total spend exceeds `DAILY_BUDGET_CAP_USD`, the execution is immediately hard-blocked.
3. Blocked workflows route safely to the HITL queue or deferred queue with code `BUDGET_EXCEEDED` and an event emitted to `agent_events`.
4. Cheaper/smaller models may never bypass evaluation or security requirements.
