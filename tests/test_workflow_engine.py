"""Unit tests for WorkflowEngine interface and InMemoryWorkflowEngine."""
import pytest

from backend.core.workflow_engine import InMemoryWorkflowEngine


@pytest.mark.asyncio
async def test_in_memory_workflow_engine_execution() -> None:
    engine = InMemoryWorkflowEngine()
    workflow_id = "wf-test-001"
    input_data = {"repo": "owner/test", "pr": 1, "mock_confidence": 0.92}

    result = await engine.run(workflow_id, input_data)
    assert result["workflow_id"] == workflow_id
    assert result["status"] == "COMPLETED"
    assert result["overall_confidence"] == 0.92

    state = await engine.get_state(workflow_id)
    assert state is not None
    assert state["status"] == "COMPLETED"

    resumed = await engine.resume(workflow_id, {})
    assert resumed["status"] == "RESUMED"
