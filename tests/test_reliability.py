"""Unit tests for Phase 12 Resilience, CircuitBreaker, Backoff, DLQ, and Fault Injection."""
import asyncio

import pytest

from backend.job_queue.dead_letter import DeadLetterQueue
from backend.reliability.fault_injection import FaultInjectionHarness, SimulatedProviderFault
from backend.reliability.resilience import (
    CircuitBreaker,
    CircuitBreakerError,
    CircuitState,
    retry_with_backoff,
)


@pytest.mark.asyncio
async def test_retry_with_backoff_success() -> None:
    attempts = 0

    async def flaky_fn() -> str:
        nonlocal attempts
        attempts += 1
        if attempts < 2:
            raise ValueError("Transient error")
        return "success"

    res = await retry_with_backoff(flaky_fn, max_retries=3, base_delay_seconds=0.01)
    assert res == "success"
    assert attempts == 2


@pytest.mark.asyncio
async def test_circuit_breaker_state_transitions() -> None:
    cb = CircuitBreaker("test_cb", failure_threshold=2, recovery_timeout_seconds=0.1)

    async def failing_fn() -> None:
        raise RuntimeError("Service failure")

    # Fail 1
    with pytest.raises(RuntimeError):
        await cb.call(failing_fn)
    assert cb.state == CircuitState.CLOSED

    # Fail 2 -> Transitions to OPEN
    with pytest.raises(RuntimeError):
        await cb.call(failing_fn)
    assert str(cb.state) == str(CircuitState.OPEN)

    # Call while OPEN fails fast with CircuitBreakerError
    with pytest.raises(CircuitBreakerError):
        await cb.call(failing_fn)

    # Wait for recovery timeout
    await asyncio.sleep(0.15)

    # Success probe -> Transitions to CLOSED
    async def healthy_fn() -> str:
        return "ok"

    res = await cb.call(healthy_fn)
    assert res == "ok"
    assert str(cb.state) == str(CircuitState.CLOSED)


def test_dead_letter_queue() -> None:
    dlq = DeadLetterQueue()
    job = dlq.push_to_dlq(
        job_id="job-999",
        workflow_id="wf-dlq-001",
        repository="owner/repo",
        pr_number=42,
        error_message="Exhausted retries",
    )
    assert job.replayed is False

    replayed = dlq.replay_job("job-999")
    assert replayed["status"] == "replayed"


def test_fault_injection_harness() -> None:
    harness = FaultInjectionHarness()
    harness.enable_fault("llm_stall")

    with pytest.raises(SimulatedProviderFault):
        harness.check_and_inject("llm_stall")

    harness.disable_fault("llm_stall")
    harness.check_and_inject("llm_stall")  # No error raised after disable
