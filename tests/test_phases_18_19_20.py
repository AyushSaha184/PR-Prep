"""Unit tests for Phase 18 Canary, Phase 19 HITL StateMachine & Disputes, and Phase 20 Drift."""
import pytest
from fastapi.testclient import TestClient

from backend.ci.canary import CanaryEvaluator, CanaryMetrics
from backend.hitl.state_machine import ConcurrencyError, HITLItem, HITLStateMachine
from backend.learning.drift_monitor import QualityDriftMonitor
from backend.learning.feedback_curation import FeedbackCurationPipeline
from backend.main import app
from backend.models.enums import ReviewStatus

client = TestClient(app)


def test_canary_evaluator_promote_and_rollback() -> None:
    evaluator = CanaryEvaluator()
    healthy = CanaryMetrics(rejection_rate=0.02, error_rate=0.001, p95_latency_ms=800)
    res1 = evaluator.evaluate_canary(healthy)
    assert res1["should_promote"] is True

    regressed = CanaryMetrics(rejection_rate=0.25, error_rate=0.05, p95_latency_ms=3000)
    res2 = evaluator.evaluate_canary(regressed)
    assert res2["should_promote"] is False
    assert res2["action"] == "ROLLBACK"


def test_hitl_state_machine_optimistic_concurrency() -> None:
    sm = HITLStateMachine()
    item = HITLItem(review_id="rev-sm-100", repository="owner/repo", pr_number=1, version=1)
    sm.register_item(item)

    updated = sm.apply_reviewer_action(
        "rev-sm-100", expected_version=1, action="APPROVE", reviewer="alice"
    )
    assert updated.version == 2
    assert updated.status == ReviewStatus.COMPLETED

    with pytest.raises(ConcurrencyError):
        sm.apply_reviewer_action("rev-sm-100", expected_version=1, action="REJECT", reviewer="bob")


def test_disputes_api_endpoint() -> None:
    res = client.post(
        "/api/disputes",
        json={
            "review_id": "rev-sm-100",
            "finding_index": 0,
            "developer_id": "dev_bob",
            "reason": "False positive SQL injection report",
        },
    )
    assert res.status_code == 201
    assert res.json()["status"] == "submitted"


def test_quality_drift_monitor_and_feedback_curation() -> None:
    monitor = QualityDriftMonitor()
    report = monitor.evaluate_drift(total_reviews=100, rejected_count=20, disputed_count=15)
    assert report.is_drift_detected is True

    curator = FeedbackCurationPipeline()
    fixture = curator.curate_feedback_item({"review_id": "rev-sm-100"})
    assert fixture.category == "curated_dispute"
