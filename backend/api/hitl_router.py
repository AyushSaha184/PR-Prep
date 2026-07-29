"""REST API router for Human-in-the-Loop approval queue."""
from typing import Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from backend.models.enums import ReviewStatus
from backend.models.review import ReviewState
from backend.observability.logging import setup_logger

logger = setup_logger("pr_prep.api.hitl")
router = APIRouter(prefix="/api/hitl", tags=["Human-in-the-Loop"])


class HITLActionRequest(BaseModel):
    review_id: str
    action: str  # APPROVE, EDIT, REJECT, ESCALATE
    reviewer: str = "human_reviewer"
    feedback: str | None = None


@router.get("/queue", response_model=list[ReviewState])
async def get_hitl_queue() -> list[ReviewState]:
    from backend.api.reviews import _MOCK_REVIEWS_STORE, _init_mock_store

    _init_mock_store()
    queue_items = [
        r for r in _MOCK_REVIEWS_STORE.values() if r.status == ReviewStatus.ROUTED_TO_HITL
    ]
    logger.info(f"Retrieved HITL queue items: count={len(queue_items)}")
    return queue_items


@router.post("/action")
async def apply_hitl_action(req: HITLActionRequest) -> dict[str, Any]:
    from backend.api.reviews import _MOCK_REVIEWS_STORE, _init_mock_store

    _init_mock_store()
    if req.review_id not in _MOCK_REVIEWS_STORE:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")

    rev = _MOCK_REVIEWS_STORE[req.review_id]
    logger.info(f"HITL action '{req.action}' applied to review {req.review_id} by {req.reviewer}")

    if req.action == "APPROVE":
        rev.status = ReviewStatus.COMPLETED
        rev.routing_decision = f"APPROVED by {req.reviewer}"
    elif req.action == "REJECT":
        rev.status = ReviewStatus.FAILED
        rev.routing_decision = f"REJECTED by {req.reviewer}"
    elif req.action == "ESCALATE":
        rev.status = ReviewStatus.ESCALATED
        rev.routing_decision = f"ESCALATED to security lead by {req.reviewer}"

    return {
        "status": "success",
        "review_id": req.review_id,
        "action": req.action,
        "new_status": rev.status,
    }
