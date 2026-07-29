# ADR-001: LangGraph behind core/workflow_engine.py Abstract Interface

## Context
PR Prep requires orchestrating four parallel specialist review agents (`security`, `quality`, `tests`, `docs`), running hybrid retrieval before each agent, aggregating findings, and persisting workflow state across steps so worker crashes do not lose work.

## Candidates Considered
1. **LangGraph (Chosen for Phases 1–12):** Python-native graph execution engine with first-class parallel fan-out via `Send` API and Redis checkpointing. Zero additional infrastructure overhead.
2. **Temporal:** Separate orchestration server and worker pool. Battle-hardened at extreme scale, but introduces heavy operational overhead and deployment complexity.

## Decision
Use LangGraph behind an abstract interface in `backend/core/workflow_engine.py`. All application modules interact with orchestration strictly through `WorkflowEngine` methods (`run`, `resume`, `get_state`). No module outside `backend/orchestrator/` imports LangGraph directly.

## Revisit Conditions (Explicit Triggers for Temporal Swap)
Revisit this decision and evaluate a Temporal implementation if:
- Sustained concurrent workflow executions exceed 50 per minute.
- Cross-service multi-language workflow coordination becomes required.
- Redis checkpointing proves insufficient against state loss under high fault injection.
