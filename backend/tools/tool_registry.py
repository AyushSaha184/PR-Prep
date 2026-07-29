"""Typed Tool Registry for inspecting repository code and running verification tools."""
from typing import Any

from pydantic import BaseModel

from backend.observability.logging import setup_logger
from backend.tools.capability_scope import CapabilityScope
from backend.tools.sandbox import DockerSandbox

logger = setup_logger("pr_prep.tools.tool_registry")


class ToolSpec(BaseModel):
    name: str
    description: str
    requires_sandbox: bool = False
    side_effect: bool = False


class ToolRegistry:
    """Registry managing available inspection and verification tools."""

    def __init__(self) -> None:
        self._tools: dict[str, ToolSpec] = {}
        self.sandbox = DockerSandbox()
        self._register_default_tools()

    def _register_default_tools(self) -> None:
        self.register_tool(
            ToolSpec(
                name="read_diff",
                description="Reads the raw diff for a given PR",
                requires_sandbox=False,
            )
        )
        self.register_tool(
            ToolSpec(
                name="run_pytest_sandbox",
                description="Runs pytest suite inside ephemeral rootless Docker sandbox",
                requires_sandbox=True,
            )
        )

    def register_tool(self, spec: ToolSpec) -> None:
        self._tools[spec.name] = spec
        logger.info(f"ToolRegistry registered tool '{spec.name}' (sandbox={spec.requires_sandbox})")

    async def execute_tool(
        self,
        tool_name: str,
        scope: CapabilityScope,
        args: dict[str, Any],
    ) -> Any:
        """Executes tool enforcing capability scope and sandbox rules."""
        if tool_name not in self._tools:
            logger.error(f"Attempted execution of unregistered tool '{tool_name}'")
            raise ValueError(f"Unregistered tool: '{tool_name}'")

        spec = self._tools[tool_name]
        scope.validate_tool_access(tool_name, target_path=args.get("path"))

        logger.info(f"Executing tool '{tool_name}' under scope caller='{scope.agent_name}'")

        if spec.requires_sandbox:
            cmd = args.get("command", ["pytest"])
            return await self.sandbox.run_command_in_sandbox(cmd)

        return {"status": "success", "result": f"Executed {tool_name} with args {args}"}
