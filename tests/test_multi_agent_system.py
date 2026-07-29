"""Unit tests for Phase 8 Grounded Specialist Agents and FindingAggregator."""
import pytest

from backend.agents.base_agent import FindingAggregator
from backend.agents.contracts import AgentRequest, AgentResponse
from backend.agents.quality_agent import QualityAgent
from backend.agents.security_agent import SecurityAgent
from backend.models.enums import AgentType, Severity
from backend.models.findings import Finding


@pytest.mark.asyncio
async def test_specialist_agents_execution() -> None:
    req = AgentRequest(
        workflow_id="wf-agents-001",
        repository="owner/repo",
        pr_number=10,
        commit_sha="commit123",
        diff_content="+ SELECT * FROM reviews WHERE id = '%s'",
        agent_type=AgentType.SECURITY,
    )

    sec_agent = SecurityAgent()
    sec_res = await sec_agent.execute(req)
    assert sec_res.agent_type == AgentType.SECURITY
    assert len(sec_res.findings) >= 1
    assert sec_res.findings[0].severity == Severity.CRITICAL

    qual_agent = QualityAgent()
    qual_res = await qual_agent.execute(req)
    assert len(qual_res.findings) >= 1


def test_finding_aggregator_deduplication_and_hitl_gate() -> None:
    finding1 = Finding(
        agent_type=AgentType.SECURITY,
        severity=Severity.CRITICAL,
        category="injection",
        summary="SQL Injection",
        file_path="backend/api/reviews.py",
        line_start=15,
        line_end=18,
        confidence=0.95,
        rationale="Raw SQL injection",
    )
    # Duplicate finding on same file & line
    finding2 = Finding(
        agent_type=AgentType.QUALITY,
        severity=Severity.HIGH,
        category="injection",
        summary="SQL Injection duplicate",
        file_path="backend/api/reviews.py",
        line_start=15,
        line_end=18,
        confidence=0.90,
        rationale="Raw SQL injection duplicate",
    )

    res1 = AgentResponse(agent_type=AgentType.SECURITY, findings=[finding1])
    res2 = AgentResponse(agent_type=AgentType.QUALITY, findings=[finding2])

    aggregator = FindingAggregator()
    output = aggregator.merge_and_deduplicate([res1, res2])

    assert len(output["findings"]) == 1  # Deduplicated from 2 to 1
    assert output["auto_post_eligible"] is False  # CRITICAL finding present -> HITL mandatory
    assert output["status"] == "ROUTED_TO_HITL"
    assert "CRITICAL finding present" in output["routing_decision"]
