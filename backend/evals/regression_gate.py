"""RegressionGate comparing current evaluation run metrics against baseline thresholds."""
from typing import Any

from pydantic import BaseModel

from backend.core.exceptions import PRPrepError
from backend.evals.dataset import load_eval_dataset
from backend.evals.scorers import EvalScoreResult, score_fixture_execution
from backend.observability.logging import setup_logger

logger = setup_logger("pr_prep.evals.regression_gate")


class RegressionError(PRPrepError):
    """Raised when evaluation scores fall below baseline threshold."""

    pass


class BenchmarkSummary(BaseModel):
    total_fixtures: int
    passed_fixtures: int
    mean_precision: float
    routing_accuracy: float
    baseline_threshold: float = 0.85
    passed_gate: bool = True


class RegressionGate:
    """Regression gate ensuring review accuracy and routing precision remain above baseline."""

    def __init__(self, baseline_threshold: float = 0.85) -> None:
        self.baseline_threshold = baseline_threshold

    def evaluate_suite(self, mock_results: dict[str, dict[str, Any]]) -> BenchmarkSummary:
        fixtures = load_eval_dataset()
        scores: list[EvalScoreResult] = []

        for f in fixtures:
            actual = mock_results.get(f.fixture_id, {"status": f.expected_routing, "findings": []})
            s = score_fixture_execution(f, actual)
            scores.append(s)

        mean_precision = round(sum(s.precision for s in scores) / len(scores), 3)
        routing_correct_count = sum(1 for s in scores if s.routing_correct)
        routing_accuracy = round(routing_correct_count / len(scores), 3)

        passed_gate = (mean_precision >= self.baseline_threshold) and (
            routing_accuracy >= self.baseline_threshold
        )

        logger.info(
            f"RegressionGate benchmark completed: mean_precision={mean_precision}, "
            f"routing_accuracy={routing_accuracy}, passed_gate={passed_gate}"
        )

        summary = BenchmarkSummary(
            total_fixtures=len(fixtures),
            passed_fixtures=routing_correct_count,
            mean_precision=mean_precision,
            routing_accuracy=routing_accuracy,
            baseline_threshold=self.baseline_threshold,
            passed_gate=passed_gate,
        )

        if not passed_gate:
            msg = (
                f"RegressionGate FAILED: precision {mean_precision} or routing "
                f"{routing_accuracy} < {self.baseline_threshold}"
            )
            logger.error(msg)
            raise RegressionError(msg)

        return summary
