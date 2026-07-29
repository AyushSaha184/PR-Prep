"""Canary deployment promotion and rollback policy evaluator."""
from pydantic import BaseModel

from backend.observability.logging import setup_logger

logger = setup_logger("pr_prep.ci.canary")


class CanaryMetrics(BaseModel):
    rejection_rate: float
    error_rate: float
    p95_latency_ms: int
    critical_security_regressions: int = 0


class CanaryEvaluator:
    """Evaluates canary release metrics against promotion thresholds."""

    def evaluate_canary(
        self,
        metrics: CanaryMetrics,
        max_rejection_rate: float = 0.10,
        max_error_rate: float = 0.02,
    ) -> dict[str, bool | str]:
        """Evaluates whether canary release can be promoted or must be rolled back."""
        rej = metrics.rejection_rate
        err = metrics.error_rate
        logger.info(f"CanaryEvaluator check: rejection={rej}, errors={err}")

        if metrics.critical_security_regressions > 0:
            logger.error("Canary FAILED: Critical security regression detected! ROLLBACK.")
            return {"should_promote": False, "action": "ROLLBACK", "reason": "Security regression"}

        if metrics.rejection_rate > max_rejection_rate or metrics.error_rate > max_error_rate:
            logger.error("Canary FAILED: Rejection or error rate exceeds threshold! ROLLBACK.")
            reason = "High error/rejection rate"
            return {"should_promote": False, "action": "ROLLBACK", "reason": reason}

        logger.info("Canary PASSED: Metrics healthy. Authorizing PROMOTION to production.")
        return {"should_promote": True, "action": "PROMOTE", "reason": "Metrics healthy"}
