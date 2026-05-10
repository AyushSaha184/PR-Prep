"""Structlog configuration."""

from __future__ import annotations

import logging
import sys
from typing import cast

import structlog


def setup_logger(debug: bool = False) -> None:
    """Configure process-wide logging."""
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(format="%(message)s", stream=sys.stderr, level=level)
    renderer: structlog.types.Processor = (
        structlog.dev.ConsoleRenderer() if debug else structlog.processors.JSONRenderer()
    )
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            renderer,
        ],
        wrapper_class=structlog.make_filtering_bound_logger(level),
        logger_factory=structlog.PrintLoggerFactory(file=sys.stderr),
        cache_logger_on_first_use=True,
    )


def get_logger() -> structlog.stdlib.BoundLogger:
    return cast(structlog.stdlib.BoundLogger, structlog.get_logger("pr_prep"))
