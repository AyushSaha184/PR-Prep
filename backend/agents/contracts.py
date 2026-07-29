"""Data contracts for specialist agent inputs and structured outputs."""
from pydantic import BaseModel, Field

from backend.models.enums import AgentType
from backend.models.findings import Finding


class AgentRequest(BaseModel):
    workflow_id: str
    repository: str
    pr_number: int
    commit_sha: str
    diff_content: str
    agent_type: AgentType
    priority: str = "normal"


class AgentResponse(BaseModel):
    agent_type: AgentType
    findings: list[Finding] = Field(default_factory=list)
    confidence: float = 1.0
    citations: list[str] = Field(default_factory=list)
    model_used: str = "gpt-4o"
    tokens_in: int = 0
    tokens_out: int = 0
    cost_usd: float = 0.0
    latency_ms: int = 0
    error: str | None = None
