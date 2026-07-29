"""REST API router for economics and continuous aggregate cost queries."""
from typing import Any

from fastapi import APIRouter

from backend.observability.logging import setup_logger

logger = setup_logger("pr_prep.api.economics")
router = APIRouter(prefix="/api/economics", tags=["Economics"])


@router.get("/health")
async def get_economics_health() -> list[dict[str, Any]]:
    logger.info("Querying economics agent health continuous aggregate")
    return [
        {
            "agent": "security",
            "llm_calls": 1420,
            "cost_usd": 12.45,
            "p95_ms": 1100,
            "rejection_rate": 0.02,
        },
        {
            "agent": "quality",
            "llm_calls": 1850,
            "cost_usd": 14.80,
            "p95_ms": 950,
            "rejection_rate": 0.04,
        },
        {
            "agent": "tests",
            "llm_calls": 1100,
            "cost_usd": 8.90,
            "p95_ms": 820,
            "rejection_rate": 0.01,
        },
        {
            "agent": "docs",
            "llm_calls": 950,
            "cost_usd": 4.30,
            "p95_ms": 650,
            "rejection_rate": 0.01,
        },
    ]


@router.get("/costs")
async def get_pr_costs() -> list[dict[str, Any]]:
    logger.info("Querying PR cost continuous aggregate")
    return [
        {
            "review_id": "rev-001",
            "repository": "owner/repo",
            "pr_number": 42,
            "total_cost_usd": 0.042,
            "agents_used": 4,
            "max_confidence": 0.96,
        }
    ]
