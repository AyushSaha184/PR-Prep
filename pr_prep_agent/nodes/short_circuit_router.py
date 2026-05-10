"""Route diffs to trivial, Flash, or Pro paths."""

from __future__ import annotations

import re
from pathlib import Path

from pr_prep_agent.logger import get_logger
from pr_prep_agent.state import PRContextState

log = get_logger()
DOC_EXTENSIONS = {".md", ".txt", ".rst"}


def short_circuit_router(state: PRContextState) -> PRContextState:
    node = "short_circuit_router"
    log.info("node_start", node=node)
    try:
        staged_files = state.get("staged_files", [])
        raw_diff = state.get("raw_diff", "")
        if staged_files and all(
            Path(item["path"]).suffix.lower() in DOC_EXTENSIONS for item in staged_files
        ):
            state["route_decision"] = "trivial"
            state["trivial_reason"] = "Documentation-only change"
        elif _is_version_bump_only(raw_diff, staged_files):
            state["route_decision"] = "trivial"
            state["trivial_reason"] = "Version bump only"
        elif _is_clean_revert(raw_diff, state):
            state["route_decision"] = "trivial"
            state["trivial_reason"] = "Clean revert"
        elif _is_flash_candidate(raw_diff, staged_files, state):
            state["route_decision"] = "flash"
            state["trivial_reason"] = None
        else:
            state["route_decision"] = "pro"
            state["trivial_reason"] = None
        if state["route_decision"] == "trivial":
            log.warning("trivial_route", reason=state.get("trivial_reason"))
        log.info("node_complete", node=node, route=state["route_decision"])
        return state
    except Exception as exc:
        log.exception("node_failed", node=node, reason=str(exc))
        raise RuntimeError(f"{node}: {exc}") from exc


def _is_version_bump_only(raw_diff: str, staged_files: list[dict[str, object]]) -> bool:
    if len(staged_files) != 1:
        return False
    path = str(staged_files[0].get("path", ""))
    if path not in {"package.json", "pyproject.toml"}:
        return False
    changed = [
        line
        for line in raw_diff.splitlines()
        if (line.startswith("+") or line.startswith("-"))
        and not line.startswith(("+++", "---"))
        and line.strip()
    ]
    if len(changed) != 2:
        return False
    patterns = [r'"version"\s*:\s*"[^"]+"', r"version\s*=\s*\"[^\"]+\""]
    return all(any(re.search(pattern, line) for pattern in patterns) for line in changed)


def _is_clean_revert(raw_diff: str, state: PRContextState) -> bool:
    plus = sum(
        1 for line in raw_diff.splitlines() if line.startswith("+") and not line.startswith("+++")
    )
    minus = sum(
        1 for line in raw_diff.splitlines() if line.startswith("-") and not line.startswith("---")
    )
    total = plus + minus
    if total == 0 or minus / total <= 0.9:
        return False
    messages = " ".join(str(item.get("message", "")) for item in state.get("commit_history", []))
    return "revert" in messages.lower()


def _is_flash_candidate(
    raw_diff: str,
    staged_files: list[dict[str, object]],
    state: PRContextState,
) -> bool:
    non_test_files = [item for item in staged_files if not bool(item.get("is_test"))]
    if staged_files and all(bool(item.get("is_test")) for item in staged_files):
        return True
    threshold_lines = int(state.get("config", {}).get("flash_threshold_lines", 200))
    threshold_files = int(state.get("config", {}).get("flash_threshold_files", 2))
    return len(raw_diff.splitlines()) < threshold_lines and len(non_test_files) <= threshold_files
