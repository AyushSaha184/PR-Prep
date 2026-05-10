"""Assess whether changed source files appear to have corresponding tests."""

from __future__ import annotations

from pr_prep_agent.logger import get_logger
from pr_prep_agent.state import PRContextState
from pr_prep_agent.tools.file_tools import find_corresponding_tests

log = get_logger()


def test_coverage_assessor(state: PRContextState) -> PRContextState:
    node = "test_coverage_assessor"
    log.info("node_start", node=node)
    try:
        gaps: list[str] = []
        for file_info in state.get("staged_files", []):
            if file_info.get("is_binary") or file_info.get("is_test"):
                continue
            path = str(file_info["path"])
            if not find_corresponding_tests(state["repo_path"], path):
                gaps.append(f"`{path}` has no corresponding test file found")
        state["test_coverage_gaps"] = gaps
        log.info("node_complete", node=node)
        return state
    except Exception as exc:
        log.exception("node_failed", node=node, reason=str(exc))
        raise RuntimeError(f"{node}: {exc}") from exc
