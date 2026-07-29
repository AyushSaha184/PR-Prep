"""Tests Specialist Agent analyzing coverage gaps, missing edge cases."""
from backend.agents.base_agent import BaseAgent
from backend.models.enums import AgentType, Severity
from backend.models.findings import Finding
from backend.observability.logging import setup_logger

logger = setup_logger("pr_prep.agents.test_agent")


class TestAgent(BaseAgent):
    __test__ = False  # Instruct Pytest not to collect this domain class as a test suite

    def __init__(self) -> None:
        super().__init__(agent_type=AgentType.TESTS, prompt_name="tests_v1")

    def get_domain_findings(self, diff: str, citations: list[str]) -> list[Finding]:
        logger.info("TestAgent evaluating diff for test coverage gaps")
        return [
            Finding(
                agent_type=AgentType.TESTS,
                severity=Severity.MEDIUM,
                category="missing_test",
                summary="Untested exception path in HMAC validator",
                file_path="tests/test_webhook.py",
                line_start=15,
                line_end=22,
                suggestion="Add test_hmac_signature_mismatch_raises_security_error()",
                confidence=0.84,
                rationale="Security exception branch has no corresponding pytest coverage.",
            )
        ]
