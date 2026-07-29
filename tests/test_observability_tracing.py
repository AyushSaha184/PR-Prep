"""Unit tests for Phase 10 ContextVar WorkflowContext, EventWriter, and Trace API."""
import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.observability.context import WorkflowContext
from backend.observability.event_writer import EventWriter

client = TestClient(app)


def test_workflow_context_propagation() -> None:
    WorkflowContext.set_context(
        trace_id="tr-test-100", repository="owner/repo", span_id="span-root"
    )
    ctx = WorkflowContext.get_current_context()
    assert ctx["trace_id"] == "tr-test-100"
    assert ctx["repository"] == "owner/repo"
    assert ctx["span_id"] == "span-root"


@pytest.mark.asyncio
async def test_event_writer_append_only() -> None:
    writer = EventWriter()
    WorkflowContext.set_context(trace_id="tr-101", repository="owner/repo")

    evt = await writer.emit_event(
        event_type="agent.completed",
        workflow_id="wf-obs-001",
        agent="security",
        cost_usd=0.012,
        latency_ms=450,
    )

    assert evt.event_id.startswith("evt-")
    assert evt.workflow_id == "wf-obs-001"
    assert evt.agent == "security"

    events = writer.get_events_for_workflow("wf-obs-001")
    assert len(events) >= 1
    assert events[0].event_type == "agent.completed"


def test_traces_api_endpoint() -> None:
    response = client.get("/api/traces/wf-obs-001")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert "event_id" in data[0]
