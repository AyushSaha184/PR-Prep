"""Feedback Curation Workflow converting reviewer edits/disputes into golden candidates."""
from typing import Any

from backend.evals.dataset import EvalFixture
from backend.observability.logging import setup_logger

logger = setup_logger("pr_prep.learning.feedback_curation")


class FeedbackCurationPipeline:
    """Curates human edits and developer disputes into candidate evaluation fixtures."""

    def curate_feedback_item(self, dispute_data: dict[str, Any]) -> EvalFixture:
        """Converts raw dispute feedback into a structured evaluation fixture candidate."""
        rev_id = dispute_data.get("review_id", "001")
        logger.info(f"FeedbackCurationPipeline curating item from review '{rev_id}'")
        return EvalFixture(
            fixture_id=f"curated-{rev_id}",
            category="curated_dispute",
            diff_content="+ # Curated feedback sample",
            expected_findings_count=1,
            expected_routing="ROUTED_TO_HITL",
            has_critical=False,
        )
