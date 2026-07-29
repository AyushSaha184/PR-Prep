"""Drift monitor tracking rejection rates, confidence calibration, and model quality drift."""
from pydantic import BaseModel

from backend.observability.logging import setup_logger

logger = setup_logger("pr_prep.learning.drift_monitor")


class QualityDriftReport(BaseModel):
    rejection_rate: float
    dispute_rate: float
    confidence_calibration_score: float
    is_drift_detected: bool = False
    recommendation: str = "System healthy"


class QualityDriftMonitor:
    """Monitors feedback signals for quality drift and prompts recalibration alerts."""

    def evaluate_drift(
        self, total_reviews: int, rejected_count: int, disputed_count: int
    ) -> QualityDriftReport:
        if total_reviews == 0:
            return QualityDriftReport(
                rejection_rate=0.0,
                dispute_rate=0.0,
                confidence_calibration_score=1.0,
                is_drift_detected=False,
            )

        rejection_rate = round(rejected_count / total_reviews, 3)
        dispute_rate = round(disputed_count / total_reviews, 3)
        is_drift = rejection_rate > 0.15 or dispute_rate > 0.10

        rec = (
            "ALERT: Quality drift detected! Audit prompts and run golden benchmark."
            if is_drift
            else "System quality healthy."
        )

        msg = f"DriftMonitor: {total_reviews} reviews, rej={rejection_rate}, disp={dispute_rate}"
        logger.info(msg)

        return QualityDriftReport(
            rejection_rate=rejection_rate,
            dispute_rate=dispute_rate,
            confidence_calibration_score=round(1.0 - rejection_rate, 2),
            is_drift_detected=is_drift,
            recommendation=rec,
        )
