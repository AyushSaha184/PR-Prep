"""Unit tests for Phase 9 Evaluation Dataset, Scorer, and RegressionGate."""
from typing import Any

import pytest

from backend.evals.dataset import load_eval_dataset
from backend.evals.regression_gate import RegressionError, RegressionGate
from backend.evals.scorers import score_fixture_execution


def test_load_eval_dataset() -> None:
    fixtures = load_eval_dataset()
    assert len(fixtures) >= 4
    categories = {f.category for f in fixtures}
    assert "security" in categories
    assert "clean" in categories


def test_scorer_fixture_execution() -> None:
    fixtures = load_eval_dataset()
    sec_fixture = fixtures[0]
    result = score_fixture_execution(sec_fixture, {"status": "ROUTED_TO_HITL", "findings": [{}]})
    assert result.routing_correct is True
    assert result.overall_score >= 0.8


def test_regression_gate_passes_baseline() -> None:
    gate = RegressionGate(baseline_threshold=0.70)
    mock_results: dict[str, dict[str, Any]] = {
        "eval-sec-001": {"status": "ROUTED_TO_HITL", "findings": [{}]},
        "eval-qual-002": {"status": "POSTED_AUTOMATICALLY", "findings": [{}]},
        "eval-clean-003": {"status": "POSTED_AUTOMATICALLY", "findings": []},
        "eval-inj-004": {"status": "POSTED_AUTOMATICALLY", "findings": []},
    }
    summary = gate.evaluate_suite(mock_results)
    assert summary.passed_gate is True
    assert summary.routing_accuracy == 1.0


def test_regression_gate_fails_on_score_drop() -> None:
    gate = RegressionGate(baseline_threshold=0.90)
    mock_results: dict[str, dict[str, Any]] = {
        "eval-sec-001": {"status": "POSTED_AUTOMATICALLY_WRONG", "findings": []},
        "eval-qual-002": {"status": "FAILED", "findings": []},
    }
    with pytest.raises(RegressionError):
        gate.evaluate_suite(mock_results)
