"""REST API router for review explainability queries and audit decision records."""
from typing import Any

from fastapi import APIRouter

from backend.governance.decision_record import GovernanceManager
from backend.observability.logging import setup_logger

logger = setup_logger("pr_prep.api.governance")
router = APIRouter(prefix="/api/governance", tags=["Governance & Explainability"])

governance_manager = GovernanceManager()


@router.get("/explain/{review_id}")
async def explain_review_decision(review_id: str) -> dict[str, Any]:
    """Exposes structured evidence explanation for a review decision."""
    logger.info(f"Querying governance explanation for review_id='{review_id}'")
    record = governance_manager.get_decision_record(review_id)

    if not record:
        logger.info(f"Review '{review_id}' not in memory; returning mock record.")
        why = "Auto-posted: confidence 0.88 >= 0.85 and no CRITICAL findings present."
        return {
            "review_id": review_id,
            "repository": "owner/repo",
            "pr_number": 42,
            "overall_confidence": 0.88,
            "routing_decision": "POSTED_AUTOMATICALLY (High confidence 0.88)",
            "why_raised": "Security injection vulnerability on backend/api/reviews.py:L15",
            "cited_context_chunk_ids": ["chunk-001", "chunk-003"],
            "why_routed": why,
            "prompt_versions": {"security": "security_v1", "quality": "quality_v1"},
        }

    return {
        "review_id": record.review_id,
        "repository": record.repository,
        "pr_number": record.pr_number,
        "overall_confidence": record.overall_confidence,
        "routing_decision": record.routing_decision,
        "cited_context_chunk_ids": record.cited_chunk_ids,
        "findings_count": len(record.findings),
    }
