"""Typed state representation for LangGraph workflow execution."""
from typing import Any, TypedDict

from backend.models.findings import Finding


class ReviewGraphState(TypedDict, total=False):
    workflow_id: str
    repository: str
    pr_number: int
    commit_sha: str
    diff_content: str
    status: str
    findings: list[Finding]
    agent_results: dict[str, list[Finding]]
    overall_confidence: float
    auto_post_eligible: bool
    routing_decision: str
    errors: list[str]
    metadata: dict[str, Any]
