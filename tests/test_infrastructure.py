"""Unit tests for Phase 13 Infrastructure, Docker, Health/Readiness probes."""
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_health_probe() -> None:
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"


def test_readiness_probe() -> None:
    res = client.get("/ready")
    assert res.status_code == 200
    assert res.json()["status"] == "ready"
