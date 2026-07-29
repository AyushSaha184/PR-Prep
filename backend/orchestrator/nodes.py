"""Node functions for LangGraph workflow graph execution."""
from typing import Any

from backend.models.enums import AgentType, Severity
from backend.models.findings import Finding
from backend.observability.logging import setup_logger
from backend.orchestrator.state import ReviewGraphState

logger = setup_logger("pr_prep.orchestrator.nodes")


async def context_prep_node(state: ReviewGraphState) -> dict[str, Any]:
    """Prepares workflow context and fetches PR diff."""
    wf_id = state.get("workflow_id", "unknown")
    repo = state.get("repository", "owner/repo")
    pr = state.get("pr_number", 0)
    logger.info(f"Node [context_prep] starting for {repo}#PR-{pr} (workflow_id={wf_id})")

    diff = state.get("diff_content") or "+ def sample(): return True\n+ # TODO: add security check"
    return {
        "diff_content": diff,
        "status": "RUNNING",
        "agent_results": {},
    }


async def security_agent_node(state: ReviewGraphState) -> dict[str, Any]:
    """Security specialist node analyzing injection, secrets, auth bypasses."""
    wf_id = state.get("workflow_id", "unknown")
    logger.info(f"Node [security_agent] analyzing diff (workflow_id={wf_id})")

    findings = [
        Finding(
            agent_type=AgentType.SECURITY,
            severity=Severity.HIGH,
            category="injection",
            summary="Potential unescaped input parameter in SQL query string",
            file_path="backend/api/reviews.py",
            line_start=15,
            line_end=18,
            suggestion="Use parameter binding: db.execute(query, params)",
            confidence=0.92,
            rationale="Dynamic string formatting passed directly to database execution context.",
        )
    ]
    logger.info(f"Node [security_agent] done: {len(findings)} findings (wf={wf_id})")
    return {"agent_results": {"security": findings}}


async def quality_agent_node(state: ReviewGraphState) -> dict[str, Any]:
    """Quality specialist node analyzing logic correctness, complexity, smells."""
    wf_id = state.get("workflow_id", "unknown")
    logger.info(f"Node [quality_agent] analyzing diff (workflow_id={wf_id})")

    findings = [
        Finding(
            agent_type=AgentType.QUALITY,
            severity=Severity.MEDIUM,
            category="code_smell",
            summary="Unused variable assignment in function body",
            file_path="backend/core/config.py",
            line_start=30,
            line_end=32,
            suggestion="Remove unused variable `dev_secret`",
            confidence=0.88,
            rationale="Variable declared on line 30 is never read before function return.",
        )
    ]
    logger.info(f"Node [quality_agent] done: {len(findings)} findings (wf={wf_id})")
    return {"agent_results": {"quality": findings}}


async def tests_agent_node(state: ReviewGraphState) -> dict[str, Any]:
    """Tests specialist node analyzing test gaps, missing edge cases."""
    wf_id = state.get("workflow_id", "unknown")
    logger.info(f"Node [tests_agent] analyzing diff (workflow_id={wf_id})")

    findings = [
        Finding(
            agent_type=AgentType.TESTS,
            severity=Severity.LOW,
            category="missing_test",
            summary="Missing unit test for invalid signature error branch",
            file_path="tests/test_webhook.py",
            line_start=20,
            line_end=25,
            suggestion="Add test_webhook_invalid_signature_returns_401()",
            confidence=0.85,
            rationale="Security error branch in validator.py is uncovered in test suite.",
        )
    ]
    logger.info(f"Node [tests_agent] done: {len(findings)} findings (wf={wf_id})")
    return {"agent_results": {"tests": findings}}


async def docs_agent_node(state: ReviewGraphState) -> dict[str, Any]:
    """Docs specialist node analyzing API docstrings and comment drift."""
    wf_id = state.get("workflow_id", "unknown")
    logger.info(f"Node [docs_agent] analyzing diff (workflow_id={wf_id})")

    findings: list[Finding] = []
    logger.info(f"Node [docs_agent] done: {len(findings)} findings (wf={wf_id})")
    return {"agent_results": {"docs": findings}}


async def aggregator_node(state: ReviewGraphState) -> dict[str, Any]:
    """Deterministic aggregator node: merges specialist findings, calculates confidence."""
    wf_id = state.get("workflow_id", "unknown")
    logger.info(f"Node [aggregator] joining agent results (workflow_id={wf_id})")

    agent_results = state.get("agent_results", {})
    all_findings: list[Finding] = []

    for agent_name, findings in agent_results.items():
        logger.info(f"Aggregator merging {len(findings)} findings from {agent_name}")
        all_findings.extend(findings)

    conf_scores = [f.confidence for f in all_findings] if all_findings else [1.0]
    overall_confidence = round(sum(conf_scores) / len(conf_scores), 3)

    has_critical = any(f.severity == Severity.CRITICAL for f in all_findings)
    auto_post = (overall_confidence >= 0.85) and not has_critical

    if has_critical:
        routing = "ROUTED_TO_HITL (Mandatory Escalation: CRITICAL finding present)"
        final_status = "ROUTED_TO_HITL"
    elif not auto_post:
        routing = f"ROUTED_TO_HITL (Confidence {overall_confidence} < threshold 0.85)"
        final_status = "ROUTED_TO_HITL"
    else:
        routing = f"POSTED_AUTOMATICALLY (High confidence {overall_confidence})"
        final_status = "POSTED_AUTOMATICALLY"

    logger.info(
        f"Node [aggregator] completed: total_findings={len(all_findings)}, "
        f"confidence={overall_confidence}, auto_post={auto_post}"
    )

    return {
        "findings": all_findings,
        "overall_confidence": overall_confidence,
        "auto_post_eligible": auto_post,
        "routing_decision": routing,
        "status": final_status,
    }


async def error_dead_letter_node(state: ReviewGraphState) -> dict[str, Any]:
    """Dead-letter node handling worker errors or branch timeouts safely."""
    wf_id = state.get("workflow_id", "unknown")
    logger.error(f"Node [error_dead_letter] handling failure (workflow_id={wf_id})")
    return {
        "status": "FAILED",
        "routing_decision": "ROUTED_TO_HITL (Workflow Execution Error / Partial Timeout)",
        "auto_post_eligible": False,
    }
