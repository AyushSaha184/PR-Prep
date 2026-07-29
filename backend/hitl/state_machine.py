"""HITL State Machine with optimistic concurrency control and immutable decision events."""
from pydantic import BaseModel, Field

from backend.core.exceptions import PRPrepError
from backend.models.enums import ReviewStatus
from backend.observability.logging import setup_logger

logger = setup_logger("pr_prep.hitl.state_machine")


class ConcurrencyError(PRPrepError):
    """Raised when concurrent reviewer edits collide."""

    pass


class HITLItem(BaseModel):
    review_id: str
    repository: str
    pr_number: int
    version: int = 1
    assigned_reviewer: str | None = None
    status: ReviewStatus = ReviewStatus.ROUTED_TO_HITL
    reviewer_comments: list[str] = Field(default_factory=list)


class HITLStateMachine:
    """Manages state transitions for Human-in-the-Loop review items with optimistic locking."""

    def __init__(self) -> None:
        self._items: dict[str, HITLItem] = {}

    def register_item(self, item: HITLItem) -> None:
        self._items[item.review_id] = item

    def apply_reviewer_action(
        self,
        review_id: str,
        expected_version: int,
        action: str,
        reviewer: str,
        comment: str | None = None,
    ) -> HITLItem:
        if review_id not in self._items:
            raise KeyError(f"HITL item '{review_id}' not found")

        item = self._items[review_id]

        if item.version != expected_version:
            exp = expected_version
            cur = item.version
            msg = f"Concurrency conflict on '{review_id}': expected {exp}, found {cur}"
            logger.error(msg)
            raise ConcurrencyError(msg)

        item.version += 1
        item.assigned_reviewer = reviewer

        if comment:
            item.reviewer_comments.append(f"[{reviewer}] {comment}")

        if action == "APPROVE":
            item.status = ReviewStatus.COMPLETED
        elif action == "REJECT":
            item.status = ReviewStatus.FAILED
        elif action == "ESCALATE":
            item.status = ReviewStatus.ESCALATED

        msg = f"HITLStateMachine applied '{action}' on '{review_id}' (new version={item.version})"
        logger.info(msg)
        return item
