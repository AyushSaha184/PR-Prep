"""Unit tests for Phase 16 CostRepository, BudgetGuard, and Economics API."""
import pytest
from fastapi.testclient import TestClient

from backend.core.exceptions import BudgetExceededError
from backend.economics.budget_guard import BudgetGuard
from backend.economics.cost_repository import CostRepository
from backend.main import app

client = TestClient(app)


def test_cost_repository_attribution() -> None:
    repo = CostRepository()
    summary = repo.get_repository_cost_summary("owner/repo")
    assert summary.repository == "owner/repo"
    assert summary.total_cost_usd > 0.0
    assert "security" in summary.agent_spend


def test_budget_guard_authorization_and_exceeded_error() -> None:
    guard = BudgetGuard(daily_budget_usd=0.05)

    # Authorized under budget cap
    assert guard.check_and_reserve_budget(0.02) is True

    # Exceeding budget cap raises BudgetExceededError
    with pytest.raises(BudgetExceededError):
        guard.check_and_reserve_budget(0.04)


def test_economics_api_summary_endpoint() -> None:
    res = client.get("/api/economics/summary/owner-repo")
    assert res.status_code == 200
    data = res.json()
    assert "repository" in data
    assert "total_cost_usd" in data
