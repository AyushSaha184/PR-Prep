"""Model router for selecting approved models per agent concern and task."""
from backend.core.config import get_settings
from backend.observability.logging import setup_logger

logger = setup_logger("pr_prep.tools.model_router")

# Specialist model policy mapping
SPECIALIST_MODEL_MAP = {
    "security": "gpt-4o",
    "quality": "gpt-4o",
    "tests": "gpt-4o-mini",
    "docs": "gpt-4o-mini",
    "aggregator": "gpt-4o",
}


def select_model_for_agent(agent_type: str) -> str:
    """Selects approved reasoning model for a specialist agent concern."""
    settings = get_settings()
    model = SPECIALIST_MODEL_MAP.get(agent_type, settings.DEFAULT_REASONING_MODEL)
    logger.info(f"ModelRouter selected model='{model}' for agent_type='{agent_type}'")
    return model
