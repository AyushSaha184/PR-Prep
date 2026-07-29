"""BudgetGuard enforcing preflight cost caps and hard-blocking overspend."""
from backend.core.config import get_settings
from backend.core.exceptions import BudgetExceededError
from backend.observability.logging import setup_logger

logger = setup_logger("pr_prep.economics.budget_guard")


class BudgetGuard:
    """Preflight budget guard hard-blocking LLM/embedding calls when spend cap is exceeded."""

    def __init__(self, daily_budget_usd: float | None = None) -> None:
        settings = get_settings()
        self.daily_budget_usd = (
            daily_budget_usd if daily_budget_usd is not None else settings.DAILY_BUDGET_CAP_USD
        )
        self._current_spend_usd = 0.0

    def check_and_reserve_budget(self, estimated_cost_usd: float) -> bool:
        """Preflight budget check. Returns True if authorized, raises BudgetExceededError."""
        cap = self.daily_budget_usd
        cur = self._current_spend_usd
        logger.info(f"BudgetGuard check: cost=${estimated_cost_usd} cur=${cur} cap=${cap}")

        if cap <= 0.0 or (cur + estimated_cost_usd > cap):
            total = cur + estimated_cost_usd
            msg = f"BudgetGuard hard-block: spend ${total:.4f} exceeds cap ${cap}"
            logger.error(msg)
            raise BudgetExceededError(msg)

        self._current_spend_usd += estimated_cost_usd
        logger.info(f"BudgetGuard authorized cost. New daily total=${self._current_spend_usd:.4f}")
        return True
