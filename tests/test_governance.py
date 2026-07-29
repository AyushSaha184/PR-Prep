"""Unit tests for Phase 15 DecisionRecord, GovernanceManager, ExportManager, and Governance API."""
from fastapi.testclient import TestClient

from backend.governance.decision_record import GovernanceManager
from backend.governance.export import GovernanceExportManager
from backend.main import app

client = TestClient(app)


def test_governance_manager_record_creation() -> None:
    gov = GovernanceManager()
    rec = gov.create_decision_record(
        review_id="rev-gov-100",
        repository="owner/repo",
        pr_number=5,
        commit_sha="commit555",
        findings=[],
        cited_chunk_ids=["chunk-01"],
        overall_confidence=0.91,
        routing_decision="POSTED_AUTOMATICALLY",
    )

    assert rec.review_id == "rev-gov-100"
    assert rec.overall_confidence == 0.91

    fetched = gov.get_decision_record("rev-gov-100")
    assert fetched is not None
    assert fetched.repository == "owner/repo"


def test_governance_export_bundle() -> None:
    exporter = GovernanceExportManager()
    bundle = exporter.export_review_audit_bundle("rev-gov-100", {"status": "POSTED_AUTOMATICALLY"})
    assert bundle["review_id"] == "rev-gov-100"
    assert "export_timestamp" in bundle


def test_governance_api_explain_endpoint() -> None:
    res = client.get("/api/governance/explain/rev-gov-100")
    assert res.status_code == 200
    data = res.json()
    assert "review_id" in data
    assert "routing_decision" in data
