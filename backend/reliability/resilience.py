"""Reliability module implementing bounded exponential backoff with jitter and CircuitBreaker."""
import asyncio
import inspect
import random
import time
from collections.abc import Callable
from enum import StrEnum
from typing import Any, TypeVar

from backend.core.exceptions import PRPrepError
from backend.observability.logging import setup_logger

logger = setup_logger("pr_prep.reliability.resilience")

T = TypeVar("T")


class CircuitState(StrEnum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


class CircuitBreakerError(PRPrepError):
    """Raised when a circuit breaker is in OPEN state."""

    pass


class CircuitBreaker:
    """Circuit breaker enforcing failure thresholds, recovery timeout, and half-open probes."""

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout_seconds: float = 30.0,
    ) -> None:
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout_seconds = recovery_timeout_seconds
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_state_change = time.perf_counter()

    async def call(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        now = time.perf_counter()

        if self.state == CircuitState.OPEN:
            if now - self.last_state_change > self.recovery_timeout_seconds:
                logger.info(f"CircuitBreaker '{self.name}' transitioning -> HALF_OPEN")
                self.state = CircuitState.HALF_OPEN
                self.last_state_change = now
            else:
                logger.warning(f"CircuitBreaker '{self.name}' is OPEN; fast-failing call.")
                raise CircuitBreakerError(f"CircuitBreaker '{self.name}' is OPEN")

        try:
            res = (
                await func(*args, **kwargs)
                if inspect.iscoroutinefunction(func)
                else func(*args, **kwargs)
            )
            if self.state == CircuitState.HALF_OPEN:
                logger.info(f"CircuitBreaker '{self.name}' probe succeeded; -> CLOSED")
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.last_state_change = now
            return res
        except Exception as e:
            self.failure_count += 1
            cur = self.failure_count
            thresh = self.failure_threshold
            logger.error(f"CircuitBreaker '{self.name}' error ({cur}/{thresh}): {e}")
            if self.failure_count >= self.failure_threshold:
                logger.error(f"CircuitBreaker '{self.name}' threshold reached; -> OPEN")
                self.state = CircuitState.OPEN
                self.last_state_change = now
            raise e


async def retry_with_backoff(
    func: Callable[..., Any],
    max_retries: int = 3,
    base_delay_seconds: float = 0.5,
    max_delay_seconds: float = 5.0,
) -> Any:
    """Executes async function with bounded exponential backoff and randomized jitter."""
    for attempt in range(1, max_retries + 1):
        try:
            return await func() if inspect.iscoroutinefunction(func) else func()
        except Exception as e:
            if attempt == max_retries:
                logger.error(f"Backoff retries exhausted ({attempt}/{max_retries}); error: {e}")
                raise e

            delay = min(max_delay_seconds, base_delay_seconds * (2 ** (attempt - 1)))
            jittered_delay = delay + random.uniform(0.0, 0.2 * delay)
            msg = f"Retry attempt {attempt}/{max_retries} error '{e}'. Delay {jittered_delay:.2f}s"
            logger.info(msg)
            await asyncio.sleep(jittered_delay)
