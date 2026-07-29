"""REST API router for developer review disputes and feedback capture."""
from typing import Any

from fastapi import APIRouter, status
from pydantic import BaseModel

from backend.observability.logging import setup_logger

logger = setup_logger("pr_prep.api.disputes")
router = APIRouter(prefix="/api/disputes", tags=["Disputes & Feedback"])


class DeveloperDisputeRequest(BaseModel):
    review_id: str
    finding_index: int
    developer_id: str
    reason: str
    evidence_notes: str | None = None


_DISPUTES_STORE: list[dict[str, Any]] = []


@router.post("", status_code=status.HTTP_201_CREATED)
async def submit_developer_dispute(req: DeveloperDisputeRequest) -> dict[str, Any]:
    """Submits a developer dispute against a posted review finding."""
    logger.info(
        f"DeveloperDispute: review_id='{req.review_id}', index={req.finding_index} "
        f"submitted by '{req.developer_id}'"
    )

    record = {
        "dispute_id": f"disp-{len(_DISPUTES_STORE) + 1:04d}",
        "review_id": req.review_id,
        "finding_index": req.finding_index,
        "developer_id": req.developer_id,
        "reason": req.reason,
        "status": "OPEN",
    }
    _DISPUTES_STORE.append(record)

    return {"status": "submitted", "dispute_id": record["dispute_id"], "review_id": req.review_id}
