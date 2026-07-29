"""ReviewDecisionRecord linking findings to diff locations and citations."""
from datetime import UTC, datetime

from pydantic import BaseModel, Field

from backend.models.findings import Finding
from backend.observability.logging import setup_logger

logger = setup_logger("pr_prep.governance.decision_record")


class ReviewDecisionRecord(BaseModel):
    review_id: str
    repository: str
    pr_number: int
    commit_sha: str
    findings: list[Finding] = Field(default_factory=list)
    cited_chunk_ids: list[str] = Field(default_factory=list)
    overall_confidence: float = 1.0
    routing_decision: str = "POSTED_AUTOMATICALLY"
    specialist_versions: dict[str, str] = Field(default_factory=dict)
    prompt_versions: dict[str, str] = Field(default_factory=dict)
    created_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())


class GovernanceManager:
    """Manages review decision records for auditing and explainability."""

    def __init__(self) -> None:
        self._records: dict[str, ReviewDecisionRecord] = {}

    def create_decision_record(
        self,
        review_id: str,
        repository: str,
        pr_number: int,
        commit_sha: str,
        findings: list[Finding],
        cited_chunk_ids: list[str],
        overall_confidence: float,
        routing_decision: str,
    ) -> ReviewDecisionRecord:
        record = ReviewDecisionRecord(
            review_id=review_id,
            repository=repository,
            pr_number=pr_number,
            commit_sha=commit_sha,
            findings=findings,
            cited_chunk_ids=cited_chunk_ids,
            overall_confidence=overall_confidence,
            routing_decision=routing_decision,
            specialist_versions={"security": "v1.0.0", "quality": "v1.0.0"},
            prompt_versions={"security": "security_v1", "quality": "quality_v1"},
        )
        self._records[review_id] = record
        msg = f"GovernanceManager recorded decision for review_id='{review_id}'"
        logger.info(f"{msg} ({len(findings)} findings)")
        return record

    def get_decision_record(self, review_id: str) -> ReviewDecisionRecord | None:
        return self._records.get(review_id)
