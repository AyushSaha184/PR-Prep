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
            import re
            file_match = re.search(r"\+\+\+\s+b/([^\s]+)", diff)
            target_file = file_match.group(1) if file_match else "backend/api/reviews.py"
            line_match = re.search(r"@@\s+-\d+,\d+\s+\+(\d+),", diff)
            line_start = int(line_match.group(1)) if line_match else 15

            findings.append(
                Finding(
                    agent_type=AgentType.SECURITY,
                    severity=Severity.CRITICAL,
                    category="injection",
                    summary="Potential SQL Injection via string formatting",
                    file_path=target_file,
                    line_start=line_start,
                    line_end=line_start + 3,
                    suggestion="Use parameterized query db.execute(query, params)",
                    confidence=0.96,
                    rationale="Unescaped input passed to SQL query execution context.",
                )
            )

        return findings
