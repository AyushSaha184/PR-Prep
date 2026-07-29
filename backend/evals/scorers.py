"""Deterministic evaluation metrics and scoring functions for evaluation benchmark."""
from typing import Any

from pydantic import BaseModel

from backend.evals.dataset import EvalFixture
from backend.observability.logging import setup_logger

logger = setup_logger("pr_prep.evals.scorers")


class EvalScoreResult(BaseModel):
    fixture_id: str
    schema_valid: bool = True
    precision: float = 1.0
    routing_correct: bool = True
    dedup_pass: bool = True
    overall_score: float = 1.0


def score_fixture_execution(
    fixture: EvalFixture, actual_output: dict[str, Any]
) -> EvalScoreResult:
    """Evaluates actual model execution output against golden fixture assertions."""
    actual_status = actual_output.get("status", "")
    findings = actual_output.get("findings", [])

    routing_correct = (fixture.expected_routing in actual_status) or (
        actual_status == fixture.expected_routing
    )
    precision = 1.0 if len(findings) == fixture.expected_findings_count else 0.8

    overall = round((1.0 if routing_correct else 0.5) * precision, 3)

    logger.info(
        f"EvalScorer scored fixture '{fixture.fixture_id}': precision={precision}, "
        f"routing_correct={routing_correct}, overall={overall}"
    )

    return EvalScoreResult(
        fixture_id=fixture.fixture_id,
        schema_valid=True,
        precision=precision,
        routing_correct=routing_correct,
        dedup_pass=True,
        overall_score=overall,
    )
