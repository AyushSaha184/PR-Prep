"""Routing advisor for cost and model optimization."""
from typing import Any

from backend.observability.logging import setup_logger

logger = setup_logger("pr_prep.economics.routing_advisor")


def recommend_model_route(diff_size_lines: int, priority: str = "normal") -> dict[str, Any]:
    """Provides cost-optimized model routing recommendations based on diff size and priority."""
    if diff_size_lines > 500:
        recommended = "gpt-4o"
        rationale = "Large diff complexity requires high reasoning capacity"
    elif priority == "high":
        recommended = "gpt-4o"
        rationale = "High priority review requires top precision model"
    else:
        recommended = "gpt-4o-mini"
        rationale = "Routine small diff optimized for latency and cost"

    msg = f"RoutingAdvisor recommended model='{recommended}' for diff_lines={diff_size_lines}"
    logger.info(msg)
    return {
        "recommended_model": recommended,
        "rationale": rationale,
        "estimated_cost_usd": 0.015 if recommended == "gpt-4o" else 0.002,
    }
