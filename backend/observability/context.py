"""ContextVar correlation context manager propagating trace ID, span ID, and repository context."""
import uuid
from contextvars import ContextVar
from typing import Any

from backend.observability.logging import setup_logger

logger = setup_logger("pr_prep.observability.context")

# ContextVars for async task trace propagation
_TRACE_ID: ContextVar[str] = ContextVar("trace_id", default="trace_root")
_SPAN_ID: ContextVar[str] = ContextVar("span_id", default="span_root")
_PARENT_SPAN_ID: ContextVar[str | None] = ContextVar("parent_span_id", default=None)
_REPOSITORY: ContextVar[str] = ContextVar("repository", default="owner/repo")


class WorkflowContext:
    """Manages ContextVar lifecycle for span and trace correlation."""

    @staticmethod
    def get_current_context() -> dict[str, Any]:
        return {
            "trace_id": _TRACE_ID.get(),
            "span_id": _SPAN_ID.get(),
            "parent_span_id": _PARENT_SPAN_ID.get(),
            "repository": _REPOSITORY.get(),
        }

    @staticmethod
    def set_context(trace_id: str, repository: str, span_id: str | None = None) -> None:
        new_span = span_id or f"span-{uuid.uuid4().hex[:8]}"
        _PARENT_SPAN_ID.set(_SPAN_ID.get())
        _TRACE_ID.set(trace_id)
        _SPAN_ID.set(new_span)
        _REPOSITORY.set(repository)
        logger.info(f"WorkflowContext updated: trace_id='{trace_id}', span_id='{new_span}'")
