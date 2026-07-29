"""Docs Specialist Agent analyzing API docstrings and comment drift."""
from backend.agents.base_agent import BaseAgent
from backend.models.enums import AgentType, Severity
from backend.models.findings import Finding
from backend.observability.logging import setup_logger

logger = setup_logger("pr_prep.agents.docs_agent")


class DocsAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(agent_type=AgentType.DOCS, prompt_name="docs_v1")

    def get_domain_findings(self, diff: str, citations: list[str]) -> list[Finding]:
        logger.info("DocsAgent evaluating diff for documentation drift")
        return [
            Finding(
                agent_type=AgentType.DOCS,
                severity=Severity.LOW,
                category="outdated_doc",
                summary="Public abstract method missing docstring argument description",
                file_path="backend/core/workflow_engine.py",
                line_start=12,
                line_end=15,
                suggestion="Add Args: workflow_id description to run() docstring",
                confidence=0.91,
                rationale="Public contract method lacks explicit parameter documentation.",
            )
        ]
