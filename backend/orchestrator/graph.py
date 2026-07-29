"""LangGraph StateGraph constructor and parallel fan-out join definition."""
import asyncio
from typing import Any

from backend.observability.logging import setup_logger
from backend.orchestrator.nodes import (
    aggregator_node,
    context_prep_node,
    docs_agent_node,
    quality_agent_node,
    security_agent_node,
    tests_agent_node,
)
from backend.orchestrator.state import ReviewGraphState

logger = setup_logger("pr_prep.orchestrator.graph")


class ReviewWorkflowGraph:
    """Simulated LangGraph StateGraph runner executing parallel fan-out and join."""

    async def execute(self, initial_state: ReviewGraphState) -> ReviewGraphState:
        wf_id = initial_state.get("workflow_id", "wf_unknown")
        logger.info(f"ReviewWorkflowGraph starting workflow_id={wf_id}")

        current_state: ReviewGraphState = dict(initial_state)  # type: ignore[assignment]

        # Step 1: Context Prep
        state_update = await context_prep_node(current_state)
        current_state.update(state_update)  # type: ignore[typeddict-item]

        # Step 2: Parallel Fan-Out to 4 Specialists
        logger.info(f"ReviewWorkflowGraph fanning out to 4 specialists (wf={wf_id})")
        sec_res, qual_res, test_res, doc_res = await self._run_parallel_specialists(current_state)

        # Merge agent results
        agent_results = {
            **sec_res.get("agent_results", {}),
            **qual_res.get("agent_results", {}),
            **test_res.get("agent_results", {}),
            **doc_res.get("agent_results", {}),
        }
        current_state["agent_results"] = agent_results

        # Step 3: Aggregator Join Node
        logger.info(f"ReviewWorkflowGraph fanning in to aggregator join node (wf={wf_id})")
        agg_res = await aggregator_node(current_state)
        current_state.update(agg_res)  # type: ignore[typeddict-item]

        logger.info(f"ReviewWorkflowGraph completed successfully for workflow_id={wf_id}")
        return current_state

    async def _run_parallel_specialists(
        self, state: ReviewGraphState
    ) -> tuple[dict[str, Any], ...]:
        """Runs the four specialist nodes asynchronously in parallel."""
        return await asyncio.gather(
            security_agent_node(state),
            quality_agent_node(state),
            tests_agent_node(state),
            docs_agent_node(state),
            return_exceptions=False,
        )
