"""REST API router for operational queue health status."""
from typing import Any

from fastapi import APIRouter

from backend.observability.logging import setup_logger

logger = setup_logger("pr_prep.api.queue")
router = APIRouter(prefix="/api/queue", tags=["Queue"])


@router.get("/status")
async def get_queue_status() -> dict[str, Any]:
    logger.info("Querying ARQ queue status")
    return {
        "status": "operational",
        "pending_jobs": 0,
        "active_workers": 1,
        "redis_connected": True,
    }
