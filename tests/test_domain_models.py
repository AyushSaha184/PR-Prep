"""Unit tests for domain models."""
import pytest
from pydantic import ValidationError

from backend.models.enums import AgentType, Severity
from backend.models.findings import Finding
from backend.models.review import ReviewState
from backend.models.webhook import WebhookEvent


def test_finding_valid_creation() -> None:
    finding = Finding(
        agent_type=AgentType.SECURITY,
        severity=Severity.CRITICAL,
        category="injection",
        summary="SQL Injection in user search query",
        file_path="backend/api/search.py",
        line_start=45,
        line_end=50,
        suggestion="Use parameterized queries instead of string formatting.",
        confidence=0.95,
        rationale="Unsanitized string concatenation observed on line 47.",
    )
    assert finding.agent_type == AgentType.SECURITY
    assert finding.severity == Severity.CRITICAL
    assert finding.confidence == 0.95


def test_finding_invalid_line_range() -> None:
    with pytest.raises(ValidationError):
        Finding(
            agent_type=AgentType.QUALITY,
            severity=Severity.HIGH,
            category="logic_error",
            summary="Invalid line range",
            file_path="backend/main.py",
            line_start=50,
            line_end=40,  # Invalid: line_end < line_start
            confidence=0.8,
            rationale="Line end cannot precede line start.",
        )


def test_review_state_defaults() -> None:
    review = ReviewState(
        workflow_id="wf-12345",
        repository="owner/repo",
        pr_number=42,
        commit_sha="abc12345",
    )
    assert review.pr_number == 42
    assert review.findings == []
    assert review.overall_confidence == 0.0
    assert review.auto_post_eligible is False


def test_webhook_event_creation() -> None:
    event = WebhookEvent(
        delivery_id="deliv-789",
        event_type="pull_request",
        action="opened",
        repository="owner/repo",
        pr_number=10,
        commit_sha="sha123",
    )
    assert event.delivery_id == "deliv-789"
    assert event.action == "opened"
