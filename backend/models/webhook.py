"""Domain model for incoming GitHub WebhookEvent."""
from typing import Any

from pydantic import BaseModel, Field


class WebhookEvent(BaseModel):
    delivery_id: str = Field(..., description="X-GitHub-Delivery UUID")
    event_type: str = Field(..., description="X-GitHub-Event header value")
    action: str = Field(default="", description="Webhook action, e.g. opened, synchronize")
    repository: str = Field(..., description="Full repository name owner/repo")
    pr_number: int = Field(..., ge=1)
    commit_sha: str = Field(...)
    sender: str = Field(default="unknown")
    raw_payload: dict[str, Any] = Field(default_factory=dict)
