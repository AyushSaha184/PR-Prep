"""LangGraph Send API router for per-file AST work."""

from __future__ import annotations

from typing import Any

try:
    from langgraph.constants import Send
except ImportError:  # pragma: no cover - compatibility with newer LangGraph
    from langgraph.types import Send

from pr_prep_agent.logger import get_logger
from pr_prep_agent.state import PRContextState

log = get_logger()


def ast_file_router_node(state: PRContextState) -> PRContextState:
    log.info("node_start", node="ast_file_router")
    log.info("node_complete", node="ast_file_router")
    return state


def ast_file_router(state: PRContextState) -> list[Any] | str:
    sends = [
        Send(
            "ast_single_file",
            {
                "file_path": file_info["path"],
                "language": file_info["language"],
                "repo_path": state["repo_path"],
                "status": file_info["status"],
                "ast_max_file_size_kb": state.get("config", {}).get("ast_max_file_size_kb", 500),
            },
        )
        for file_info in state.get("staged_files", [])
        if not file_info.get("is_binary") and file_info.get("language") is not None
    ]
    return sends if sends else "single"
