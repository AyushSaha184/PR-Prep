"""Fallback summary for files that could not be parsed with AST."""

from __future__ import annotations

import re

from pr_prep_agent.logger import get_logger
from pr_prep_agent.state import PRContextState

log = get_logger()


def raw_diff_fallback(state: PRContextState) -> PRContextState:
    node = "raw_diff_fallback"
    log.info("node_start", node=node)
    try:
        existing = {item.get("file") for item in state.get("ast_results", [])}
        for failed_file in state.get("ast_failed_files", []):
            if failed_file in existing:
                continue
            section = _diff_section(state.get("raw_diff", ""), failed_file)
            plus = sum(
                1
                for line in section.splitlines()
                if line.startswith("+") and not line.startswith("+++")
            )
            minus = sum(
                1
                for line in section.splitlines()
                if line.startswith("-") and not line.startswith("---")
            )
            state.setdefault("ast_results", []).append(
                {
                    "file": failed_file,
                    "change_type": "modified",
                    "detail": f"Raw diff: +{plus} lines, -{minus} lines (AST unsupported)",
                }
            )
        log.info("node_complete", node=node)
        return state
    except Exception as exc:
        log.exception("node_failed", node=node, reason=str(exc))
        raise RuntimeError(f"{node}: {exc}") from exc


def _diff_section(raw_diff: str, file_path: str) -> str:
    pattern = re.compile(r"^diff --git .*? b/" + re.escape(file_path) + r"$", re.MULTILINE)
    match = pattern.search(raw_diff)
    if not match:
        return ""
    next_match = re.search(r"^diff --git ", raw_diff[match.end() :], flags=re.MULTILINE)
    end = match.end() + next_match.start() if next_match else len(raw_diff)
    return raw_diff[match.start() : end]
