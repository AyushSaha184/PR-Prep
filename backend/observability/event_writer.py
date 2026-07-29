"""Append-only event writer recording immutable agent_events hypertable records."""
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field

from backend.observability.context import WorkflowContext
from backend.observability.logging import setup_logger

logger = setup_logger("pr_prep.observability.event_writer")


class AgentEvent(BaseModel):
    event_id: str
    workflow_id: str
    trace_id: str
    span_id: str
    parent_span_id: str | None = None
    event_type: str
    agent: str = "orchestrator"
    cost_usd: float = 0.0
    latency_ms: int = 0
    confidence: float = 1.0
    payload: dict[str, Any] = Field(default_factory=dict)
    created_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())


_IMMUTABLE_EVENT_STORE: list[AgentEvent] = []


class EventWriter:
    """Append-only event writer for immutable execution tracing."""

    async def emit_event(
        self,
        event_type: str,
        workflow_id: str,
        agent: str = "orchestrator",
        cost_usd: float = 0.0,
        latency_ms: int = 0,
        confidence: float = 1.0,
        payload: dict[str, Any] | None = None,
    ) -> AgentEvent:
        """Appends an immutable event to the tracing store."""
        ctx = WorkflowContext.get_current_context()
        event_id = f"evt-{len(_IMMUTABLE_EVENT_STORE) + 1:04d}"

        evt = AgentEvent(
            event_id=event_id,
            workflow_id=workflow_id,
            trace_id=ctx["trace_id"],
            span_id=ctx["span_id"],
            parent_span_id=ctx["parent_span_id"],
            event_type=event_type,
            agent=agent,
            cost_usd=cost_usd,
            latency_ms=latency_ms,
            confidence=confidence,
            payload=payload or {},
        )

        _IMMUTABLE_EVENT_STORE.append(evt)
        msg = f"EventWriter appended event '{event_id}' [{event_type}] for wf='{workflow_id}'"
        logger.info(msg)
        return evt

    def get_events_for_workflow(self, workflow_id: str) -> list[AgentEvent]:
        """Returns all contiguous events for a given workflow ordered by timestamp."""
        return [e for e in _IMMUTABLE_EVENT_STORE if e.workflow_id == workflow_id]
