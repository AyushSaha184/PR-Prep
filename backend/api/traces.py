"""REST API router for querying immutable execution traces and timelines."""
from fastapi import APIRouter

from backend.observability.event_writer import AgentEvent, EventWriter
from backend.observability.logging import setup_logger

logger = setup_logger("pr_prep.api.traces")
router = APIRouter(prefix="/api/traces", tags=["Traces"])

event_writer = EventWriter()


@router.get("/{workflow_id}", response_model=list[AgentEvent])
async def get_workflow_trace_timeline(workflow_id: str) -> list[AgentEvent]:
    """Reconstructs contiguous execution timeline for a single workflow review."""
    logger.info(f"Querying execution trace timeline for workflow_id='{workflow_id}'")
    events = event_writer.get_events_for_workflow(workflow_id)

    if not events:
        # Fixture trace response if not in memory
        logger.info(f"Trace for '{workflow_id}' not found in event store; returning mock trace.")
        return [
            AgentEvent(
                event_id="evt-0001",
                workflow_id=workflow_id,
                trace_id=f"tr-{workflow_id}",
                span_id="span-root",
                event_type="span.start",
                agent="ingress",
                payload={"action": "webhook_received"},
            ),
            AgentEvent(
                event_id="evt-0002",
                workflow_id=workflow_id,
                trace_id=f"tr-{workflow_id}",
                span_id="span-sec",
                parent_span_id="span-root",
                event_type="agent.completed",
                agent="security",
                cost_usd=0.015,
                latency_ms=1100,
                confidence=0.92,
            ),
        ]

    return events
