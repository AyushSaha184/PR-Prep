"""Fault injection harness for chaos and resilience testing."""
from backend.core.exceptions import PRPrepError
from backend.observability.logging import setup_logger

logger = setup_logger("pr_prep.reliability.fault_injection")


class SimulatedProviderFault(PRPrepError):
    """Simulated provider stall or outage error."""
    pass


class FaultInjectionHarness:
    """Injects synthetic failure modes to verify system resilience and HITL escalation."""

    def __init__(self, enable_faults: bool = False) -> None:
        self.enable_faults = enable_faults
        self._active_faults: set[str] = set()

    def enable_fault(self, fault_type: str) -> None:
        self.enable_faults = True
        self._active_faults.add(fault_type)
        logger.warning(f"FaultInjectionHarness activated fault: '{fault_type}'")

    def disable_fault(self, fault_type: str) -> None:
        self._active_faults.discard(fault_type)
        if not self._active_faults:
            self.enable_faults = False
        logger.info(f"FaultInjectionHarness deactivated fault: '{fault_type}'")

    def check_and_inject(self, fault_type: str) -> None:
        """Injects simulated fault if active."""
        if self.enable_faults and fault_type in self._active_faults:
            logger.error(f"FaultInjectionHarness injecting fault '{fault_type}'!")
            raise SimulatedProviderFault(f"Simulated fault: {fault_type}")
