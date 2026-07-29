"""Capability Scope enforcing least-privilege tool execution rules."""
from pydantic import BaseModel, Field

from backend.core.exceptions import SecurityError
from backend.observability.logging import setup_logger

logger = setup_logger("pr_prep.tools.capability_scope")


class CapabilityScope(BaseModel):
    """Binds tool execution to a caller agent, repository, commit SHA, and allowed paths."""

    agent_name: str
    repository: str
    commit_sha: str
    allowed_paths: list[str] = Field(default_factory=list)
    allow_write: bool = False
    allow_network: bool = False

    def validate_tool_access(self, tool_name: str, target_path: str | None = None) -> bool:
        """Validates tool invocation against allowed capability bounds."""
        msg = f"CapabilityScope checking access: agent='{self.agent_name}', tool='{tool_name}'"
        logger.info(msg)

        forbidden_tools = {"github_post_review", "system_shell_exec", "delete_file"}
        if tool_name in forbidden_tools:
            err = f"Agent '{self.agent_name}' attempted unauthorized tool execution: '{tool_name}'"
            logger.warning(f"CapabilityScope violation: {err}")
            raise SecurityError(err)

        if target_path and self.allowed_paths:
            if not any(target_path.startswith(p) for p in self.allowed_paths):
                err = f"Path escape attempt: '{target_path}' outside paths {self.allowed_paths}"
                logger.warning(f"CapabilityScope violation: {err}")
                raise SecurityError(err)

        logger.info(f"CapabilityScope granted access for tool='{tool_name}'")
        return True
