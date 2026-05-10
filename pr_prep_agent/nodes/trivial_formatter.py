"""Local PR formatter for trivial changes."""

from __future__ import annotations

import re
from pathlib import Path

from pr_prep_agent.logger import get_logger
from pr_prep_agent.state import PRContextState

log = get_logger()


def trivial_formatter(state: PRContextState) -> PRContextState:
    node = "trivial_formatter"
    log.info("node_start", node=node)
    try:
        reason = state.get("trivial_reason") or ""
        if "Version bump" in reason:
            state["pr_structure"] = _format_version_bump(state)
        elif "revert" in reason.lower():
            state["pr_structure"] = _format_revert(state)
        else:
            files = [item["path"] for item in state.get("staged_files", [])]
            state["pr_structure"] = {
                "title": f"docs: update {', '.join(Path(file).name for file in files)}",
                "summary": "Updates documentation files.",
                "changes": [f"Documentation update in `{file}`" for file in files],
                "breaking_change_note": None,
                "testing_notes": "Not run; documentation-only change.",
                "reviewer_suggestions": [],
                "risk_level": "low",
                "linked_issues": state.get("linked_issues", []),
            }
        log.info("node_complete", node=node)
        return state
    except Exception as exc:
        log.exception("node_failed", node=node, reason=str(exc))
        raise RuntimeError(f"{node}: {exc}") from exc


def _format_version_bump(state: PRContextState) -> dict[str, object]:
    raw_diff = state.get("raw_diff", "")
    old = new = "unknown"
    for line in raw_diff.splitlines():
        if line.startswith("-") and not line.startswith("---"):
            old = _extract_version(line) or old
        if line.startswith("+") and not line.startswith("+++"):
            new = _extract_version(line) or new
    file_path = state.get("staged_files", [{}])[0].get("path", "version file")
    package = Path(str(file_path)).stem
    return {
        "title": f"chore: bump version to {new}",
        "summary": f"Bumps {package} version from {old} to {new}.",
        "changes": [f"Version bump in {file_path}"],
        "breaking_change_note": None,
        "testing_notes": "Not run; version-only change.",
        "reviewer_suggestions": [],
        "risk_level": "low",
        "linked_issues": state.get("linked_issues", []),
    }


def _extract_version(line: str) -> str | None:
    match = re.search(r'"version"\s*:\s*"([^"]+)"', line)
    if match:
        return match.group(1)
    match = re.search(r"version\s*=\s*\"([^\"]+)\"", line)
    return match.group(1) if match else None


def _format_revert(state: PRContextState) -> dict[str, object]:
    message = next(
        (str(item.get("message", "")).splitlines()[0] for item in state.get("commit_history", [])),
        "recent change",
    )
    message = re.sub(r"^revert[:\s-]*", "", message, flags=re.IGNORECASE).strip() or "recent change"
    return {
        "title": f"revert: {message}"[:72],
        "summary": "Reverts changes introduced in a recent commit.",
        "changes": ["Reverted deleted lines from the staged diff."],
        "breaking_change_note": None,
        "testing_notes": "Review reverted behavior before merging.",
        "reviewer_suggestions": [],
        "risk_level": "medium",
        "linked_issues": state.get("linked_issues", []),
    }
