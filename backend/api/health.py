"""Health and readiness endpoints for FastAPI backend."""
from typing import Any

from fastapi import APIRouter

from backend.core.config import get_settings

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check() -> dict[str, Any]:
    settings = get_settings()
    return {
        "status": "healthy",
        "service": "pr-prep-backend",
        "version": "0.1.0",
        "environment": settings.ENVIRONMENT,
    }


@router.get("/ready")
async def readiness_check() -> dict[str, Any]:
    return {
        "status": "ready",
        "database": "configured",
        "queue": "configured",
    }
