"""Abstract WorkflowEngine interface and in-memory test implementation.

Modular-monolith rule: core depends on nothing; outer orchestrators (LangGraph/Temporal)
implement this interface.
"""
from abc import ABC, abstractmethod
from typing import Any


class WorkflowEngine(ABC):
    """Abstract orchestration engine interface (ADR-001 seam)."""

    @abstractmethod
    async def run(self, workflow_id: str, input_data: dict[str, Any]) -> dict[str, Any]:
        """Starts or executes a workflow run."""
        pass

    @abstractmethod
    async def resume(self, workflow_id: str, checkpoint_state: dict[str, Any]) -> dict[str, Any]:
        """Resumes workflow execution from a checkpoint."""
        pass

    @abstractmethod
    async def get_state(self, workflow_id: str) -> dict[str, Any] | None:
        """Retrieves current workflow state."""
        pass


class InMemoryWorkflowEngine(WorkflowEngine):
    """Simple in-memory workflow engine for unit tests and local execution before LangGraph."""

    def __init__(self) -> None:
        self._states: dict[str, dict[str, Any]] = {}

    async def run(self, workflow_id: str, input_data: dict[str, Any]) -> dict[str, Any]:
        state = {
            "workflow_id": workflow_id,
            "status": "COMPLETED",
            "input": input_data,
            "findings": input_data.get("mock_findings", []),
            "overall_confidence": input_data.get("mock_confidence", 0.9),
        }
        self._states[workflow_id] = state
        return state

    async def resume(self, workflow_id: str, checkpoint_state: dict[str, Any]) -> dict[str, Any]:
        state = self._states.get(workflow_id, checkpoint_state)
        state["status"] = "RESUMED"
        self._states[workflow_id] = state
        return state

    async def get_state(self, workflow_id: str) -> dict[str, Any] | None:
        return self._states.get(workflow_id)
