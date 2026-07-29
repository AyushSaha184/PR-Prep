"""Unit tests for Phase 4 orchestrator, LangGraphEngine, parallel fan-out, and aggregator join."""
import pytest

from backend.models.enums import ReviewStatus
from backend.orchestrator.langgraph_engine import LangGraphEngine


@pytest.mark.asyncio
async def test_langgraph_engine_parallel_execution() -> None:
    engine = LangGraphEngine()
    input_data = {
        "repository": "owner/test-repo",
        "pr_number": 42,
        "commit_sha": "commit123",
        "diff_content": "+ def new_func(): pass",
    }

    result = await engine.run("wf-test-graph-001", input_data)

    assert result["workflow_id"] == "wf-test-graph-001"
    assert "agent_results" in result
    assert "security" in result["agent_results"]
    assert "quality" in result["agent_results"]
    assert "tests" in result["agent_results"]
    assert "docs" in result["agent_results"]

    # Aggregator result checks
    assert len(result["findings"]) >= 3
    assert result["overall_confidence"] > 0.0
    assert "routing_decision" in result
    assert result["status"] in (ReviewStatus.ROUTED_TO_HITL, ReviewStatus.POSTED_AUTOMATICALLY)


@pytest.mark.asyncio
async def test_langgraph_engine_checkpoint_and_resume() -> None:
    engine = LangGraphEngine()
    workflow_id = "wf-checkpoint-002"

    await engine.run(workflow_id, {"repository": "owner/repo", "pr_number": 10})

    saved_state = await engine.get_state(workflow_id)
    assert saved_state is not None
    assert saved_state["workflow_id"] == workflow_id

    resumed = await engine.resume(workflow_id, {})
    assert resumed["status"] == "RESUMED"
