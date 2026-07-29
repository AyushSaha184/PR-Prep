"""LangGraph implementation of abstract core.workflow_engine.WorkflowEngine interface."""
from typing import Any

from backend.core.workflow_engine import WorkflowEngine
from backend.observability.logging import setup_logger
from backend.orchestrator.graph import ReviewWorkflowGraph
from backend.orchestrator.state import ReviewGraphState

logger = setup_logger("pr_prep.orchestrator.langgraph_engine")


class LangGraphEngine(WorkflowEngine):
    """LangGraph execution engine implementing core.workflow_engine.WorkflowEngine."""

    def __init__(self) -> None:
        self._checkpoints: dict[str, ReviewGraphState] = {}
        self.graph = ReviewWorkflowGraph()

    async def run(self, workflow_id: str, input_data: dict[str, Any]) -> dict[str, Any]:
        logger.info(f"LangGraphEngine.run() initiated for workflow_id={workflow_id}")

        initial_state: ReviewGraphState = {
            "workflow_id": workflow_id,
            "repository": input_data.get("repository", "owner/repo"),
            "pr_number": input_data.get("pr_number", 1),
            "commit_sha": input_data.get("commit_sha", "sha_placeholder"),
            "status": "PENDING",
            "errors": [],
            "metadata": input_data,
        }

        # Save initial checkpoint
        self._checkpoints[workflow_id] = initial_state

        try:
            final_state = await self.graph.execute(initial_state)
            self._checkpoints[workflow_id] = final_state
            logger.info(f"LangGraphEngine.run() completed for workflow_id={workflow_id}")
            return dict(final_state)
        except Exception as e:
            logger.error(f"LangGraphEngine.run() error for workflow_id={workflow_id}: {e}")
            error_state: ReviewGraphState = {
                **initial_state,
                "status": "FAILED",
                "routing_decision": f"ROUTED_TO_HITL (Workflow Execution Error: {e})",
                "errors": [str(e)],
            }
            self._checkpoints[workflow_id] = error_state
            return dict(error_state)

    async def resume(self, workflow_id: str, checkpoint_state: dict[str, Any]) -> dict[str, Any]:
        logger.info(f"LangGraphEngine.resume() called for workflow_id={workflow_id}")
        state = self._checkpoints.get(workflow_id) or checkpoint_state
        state["status"] = "RESUMED"
        self._checkpoints[workflow_id] = state  # type: ignore[assignment]
        return dict(state)

    async def get_state(self, workflow_id: str) -> dict[str, Any] | None:
        state = self._checkpoints.get(workflow_id)
        return dict(state) if state else None
