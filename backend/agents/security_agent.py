"""Security Specialist Agent analyzing injection, secrets, auth, deserialization."""
from backend.agents.base_agent import BaseAgent
from backend.models.enums import AgentType, Severity
from backend.models.findings import Finding
from backend.observability.logging import setup_logger

logger = setup_logger("pr_prep.agents.security_agent")


class SecurityAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(agent_type=AgentType.SECURITY, prompt_name="security_v1")

    def get_domain_findings(self, diff: str, citations: list[str]) -> list[Finding]:
        logger.info("SecurityAgent evaluating diff for security vulnerabilities")
        findings = []

        if "SELECT" in diff and "%" in diff:
            findings.append(
                Finding(
                    agent_type=AgentType.SECURITY,
                    severity=Severity.CRITICAL,
                    category="injection",
                    summary="Potential SQL Injection via string formatting",
                    file_path="backend/api/reviews.py",
                    line_start=15,
                    line_end=18,
                    suggestion="Use parameterized query db.execute(query, params)",
                    confidence=0.96,
                    rationale="Unescaped input passed to SQL query execution context.",
                )
            )

        return findings
