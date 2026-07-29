"""Domain model for ReviewState and PRReviewRecord."""
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from backend.models.enums import ReviewStatus
from backend.models.findings import Finding


class ReviewState(BaseModel):
    review_id: UUID = Field(default_factory=uuid4)
    workflow_id: str
    repository: str
    pr_number: int
    commit_sha: str
    status: ReviewStatus = ReviewStatus.PENDING
    findings: list[Finding] = Field(default_factory=list)
    overall_confidence: float = 0.0
    auto_post_eligible: bool = False
    routing_decision: str = "PENDING"
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    metadata: dict[str, Any] = Field(default_factory=dict)
