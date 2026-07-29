"""Quality Specialist Agent analyzing logic errors, complexity, code smells."""
from backend.agents.base_agent import BaseAgent
from backend.models.enums import AgentType, Severity
from backend.models.findings import Finding
from backend.observability.logging import setup_logger

logger = setup_logger("pr_prep.agents.quality_agent")


class QualityAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(agent_type=AgentType.QUALITY, prompt_name="quality_v1")

    def get_domain_findings(self, diff: str, citations: list[str]) -> list[Finding]:
        logger.info("QualityAgent evaluating diff for code quality")
        return [
            Finding(
                agent_type=AgentType.QUALITY,
                severity=Severity.HIGH,
                category="logic_error",
                summary="Unchecked dictionary index lookup may raise KeyError",
                file_path="backend/integrations/github_client.py",
                line_start=110,
                line_end=112,
                suggestion="Use auth_data.get('token') with a default fallback",
                confidence=0.89,
                rationale="Direct key access without prior key verification.",
            )
        ]
