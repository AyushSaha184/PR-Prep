"""REST API router for PR reviews."""
from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from backend.models.enums import ReviewStatus, Severity
from backend.models.findings import Finding
from backend.models.review import ReviewState
from backend.observability.logging import setup_logger

logger = setup_logger("pr_prep.api.reviews")
router = APIRouter(prefix="/api/reviews", tags=["Reviews"])

# In-memory store for development/testing
_MOCK_REVIEWS_STORE: dict[str, ReviewState] = {}


def _init_mock_store() -> None:
    if _MOCK_REVIEWS_STORE:
        return
    rev1 = ReviewState(
        workflow_id="wf-001",
        repository="owner/repo",
        pr_number=42,
        commit_sha="a1b2c3d4",
        status=ReviewStatus.ROUTED_TO_HITL,
        findings=[
            Finding(
                agent_type="security",  # type: ignore[arg-type]
                severity=Severity.CRITICAL,
                category="injection",
                summary="SQL Injection vulnerability",
                file_path="backend/api/reviews.py",
                line_start=10,
                line_end=15,
                suggestion="Use parameterized query",
                confidence=0.96,
                rationale="Raw string concatenation detected",
            )
        ],
        overall_confidence=0.89,
        auto_post_eligible=False,
        routing_decision="ROUTED_TO_HITL (Mandatory Escalation: CRITICAL finding present)",
    )
    _MOCK_REVIEWS_STORE[str(rev1.review_id)] = rev1


@router.get("", response_model=list[ReviewState])
async def list_reviews() -> list[ReviewState]:
    _init_mock_store()
    logger.info("Listing all review states")
    return list(_MOCK_REVIEWS_STORE.values())


@router.get("/{review_id}", response_model=ReviewState)
async def get_review_by_id(review_id: UUID) -> ReviewState:
    _init_mock_store()
    str_id = str(review_id)
    if str_id not in _MOCK_REVIEWS_STORE:
        logger.warning(f"Review not found: {str_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    return _MOCK_REVIEWS_STORE[str_id]
