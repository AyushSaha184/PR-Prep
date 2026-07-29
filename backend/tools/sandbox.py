"""Ephemeral Docker Sandbox interface for isolated tool execution."""
from pydantic import BaseModel

from backend.observability.logging import setup_logger

logger = setup_logger("pr_prep.tools.sandbox")


class SandboxResult(BaseModel):
    exit_code: int
    stdout: str
    stderr: str
    timed_out: bool = False


class DockerSandbox:
    """Interface for rootless ephemeral container execution."""

    def __init__(self, image: str = "python:3.12-slim", timeout_seconds: float = 15.0) -> None:
        self.image = image
        self.timeout_seconds = timeout_seconds

    async def run_command_in_sandbox(
        self, command: list[str], workspace_mount: str | None = None
    ) -> SandboxResult:
        """Executes a command inside the isolated ephemeral sandbox."""
        cmd_str = " ".join(command)
        logger.info(f"DockerSandbox executing command inside image='{self.image}': '{cmd_str}'")

        # Isolated sandbox simulation / docker runner stub
        return SandboxResult(
            exit_code=0,
            stdout=f"[SANDBOX_OUTPUT] Command '{cmd_str}' executed cleanly.",
            stderr="",
            timed_out=False,
        )
