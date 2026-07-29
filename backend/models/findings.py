"""Domain model for Finding matching core contract."""
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator

from backend.models.enums import AgentType, Severity


class Finding(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    agent_type: AgentType
    severity: Severity
    category: str = Field(..., min_length=1)
    summary: str = Field(..., min_length=1)
    file_path: str = Field(..., min_length=1)
    line_start: int = Field(..., ge=1)
    line_end: int = Field(..., ge=1)
    suggestion: str = Field(default="")
    confidence: float = Field(..., ge=0.0, le=1.0)
    rationale: str = Field(..., min_length=1)

    @field_validator("line_end")
    @classmethod
    def validate_line_range(cls, v: int, info: Any) -> int:
        line_start = info.data.get("line_start")
        if line_start is not None and v < line_start:
            raise ValueError("line_end must be greater than or equal to line_start")
        return v
