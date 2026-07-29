"""Node functions for LangGraph workflow graph execution with grounded specialist agents."""
from typing import Any

from backend.agents.base_agent import FindingAggregator
from backend.agents.contracts import AgentRequest
from backend.agents.docs_agent import DocsAgent
from backend.agents.quality_agent import QualityAgent
from backend.agents.security_agent import SecurityAgent
from backend.agents.test_agent import TestAgent
from backend.observability.logging import setup_logger
from backend.orchestrator.state import ReviewGraphState

logger = setup_logger("pr_prep.orchestrator.nodes")


async def context_prep_node(state: ReviewGraphState) -> dict[str, Any]:
    """Prepares workflow context and fetches PR diff."""
    wf_id = state.get("workflow_id", "unknown")
    repo = state.get("repository", "owner/repo")
    pr = state.get("pr_number", 0)
    logger.info(f"Node [context_prep] starting for {repo}#PR-{pr} (workflow_id={wf_id})")

    diff = state.get("diff_content") or "+ SELECT * FROM reviews WHERE id = '%' + input"
    return {
        "diff_content": diff,
        "status": "RUNNING",
        "agent_results": {},
    }


async def security_agent_node(state: ReviewGraphState) -> dict[str, Any]:
    """Security specialist node analyzing injection, secrets, auth bypasses."""
    wf_id = state.get("workflow_id", "unknown")
    logger.info(f"Node [security_agent] analyzing diff (workflow_id={wf_id})")

    req = AgentRequest(
        workflow_id=wf_id,
        repository=state.get("repository", "owner/repo"),
        pr_number=state.get("pr_number", 1),
        commit_sha=state.get("commit_sha", "sha123"),
        diff_content=state.get("diff_content", ""),
        agent_type="security",  # type: ignore[arg-type]
    )

    agent = SecurityAgent()
    res = await agent.execute(req)
    return {"agent_results": {"security": res.findings}}


async def quality_agent_node(state: ReviewGraphState) -> dict[str, Any]:
    """Quality specialist node analyzing logic correctness, complexity, smells."""
    wf_id = state.get("workflow_id", "unknown")
    logger.info(f"Node [quality_agent] analyzing diff (workflow_id={wf_id})")

    req = AgentRequest(
        workflow_id=wf_id,
        repository=state.get("repository", "owner/repo"),
        pr_number=state.get("pr_number", 1),
        commit_sha=state.get("commit_sha", "sha123"),
        diff_content=state.get("diff_content", ""),
        agent_type="quality",  # type: ignore[arg-type]
    )

    agent = QualityAgent()
    res = await agent.execute(req)
    return {"agent_results": {"quality": res.findings}}


async def tests_agent_node(state: ReviewGraphState) -> dict[str, Any]:
    """Tests specialist node analyzing test gaps, missing edge cases."""
    wf_id = state.get("workflow_id", "unknown")
    logger.info(f"Node [tests_agent] analyzing diff (workflow_id={wf_id})")

    req = AgentRequest(
        workflow_id=wf_id,
        repository=state.get("repository", "owner/repo"),
        pr_number=state.get("pr_number", 1),
        commit_sha=state.get("commit_sha", "sha123"),
        diff_content=state.get("diff_content", ""),
        agent_type="tests",  # type: ignore[arg-type]
    )

    agent = TestAgent()
    res = await agent.execute(req)
    return {"agent_results": {"tests": res.findings}}


async def docs_agent_node(state: ReviewGraphState) -> dict[str, Any]:
    """Docs specialist node analyzing API docstrings and comment drift."""
    wf_id = state.get("workflow_id", "unknown")
    logger.info(f"Node [docs_agent] analyzing diff (workflow_id={wf_id})")

    req = AgentRequest(
        workflow_id=wf_id,
        repository=state.get("repository", "owner/repo"),
        pr_number=state.get("pr_number", 1),
        commit_sha=state.get("commit_sha", "sha123"),
        diff_content=state.get("diff_content", ""),
        agent_type="docs",  # type: ignore[arg-type]
    )

    agent = DocsAgent()
    res = await agent.execute(req)
    return {"agent_results": {"docs": res.findings}}


async def aggregator_node(state: ReviewGraphState) -> dict[str, Any]:
    """Deterministic aggregator node using FindingAggregator."""
    wf_id = state.get("workflow_id", "unknown")
    logger.info(f"Node [aggregator] joining agent results (workflow_id={wf_id})")

    agent_results = state.get("agent_results", {})
    responses = []

    from backend.agents.contracts import AgentResponse

    for agent_name, findings in agent_results.items():
        responses.append(
            AgentResponse(
                agent_type=agent_name,  # type: ignore[arg-type]
                findings=findings,
                confidence=0.90,
            )
        )

    aggregator = FindingAggregator()
    result = aggregator.merge_and_deduplicate(responses)
    return result


async def error_dead_letter_node(state: ReviewGraphState) -> dict[str, Any]:
    """Dead-letter node handling worker errors or branch timeouts safely."""
    wf_id = state.get("workflow_id", "unknown")
    logger.error(f"Node [error_dead_letter] handling failure (workflow_id={wf_id})")
    return {
        "status": "FAILED",
        "routing_decision": "ROUTED_TO_HITL (Workflow Execution Error / Partial Timeout)",
        "auto_post_eligible": False,
    }
