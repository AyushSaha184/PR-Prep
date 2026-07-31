"""REST API router for Human-in-the-Loop approval queue."""
from typing import Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from backend.hitl.state_machine import ConcurrencyError, HITLItem, HITLStateMachine
from backend.models.enums import ReviewStatus
from backend.models.review import ReviewState
from backend.observability.logging import setup_logger

logger = setup_logger("pr_prep.api.hitl")
router = APIRouter(prefix="/api/hitl", tags=["Human-in-the-Loop"])
hitl_state_machine = HITLStateMachine()


class HITLActionRequest(BaseModel):
    review_id: str
    action: str  # APPROVE, EDIT, REJECT, ESCALATE
    expected_version: int = 1
    reviewer: str = "human_reviewer"
    comment: str | None = None
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

    # Register item in state machine if missing
    if req.review_id not in hitl_state_machine._items:
        hitl_state_machine.register_item(
            HITLItem(
                review_id=req.review_id,
                repository=rev.repository,
                pr_number=rev.pr_number,
                version=1,
                status=rev.status,
            )
        )

    try:
        updated_item = hitl_state_machine.apply_reviewer_action(
            review_id=req.review_id,
            expected_version=req.expected_version,
            action=req.action,
            reviewer=req.reviewer,
            comment=req.comment or req.feedback,
        )
        rev.status = updated_item.status
        rev.routing_decision = f"{req.action} applied by {req.reviewer}"
    except ConcurrencyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(e)
        ) from e

    return {
        "status": "success",
        "review_id": req.review_id,
        "action": req.action,
        "new_status": rev.status,
        "new_version": updated_item.version,
    }
