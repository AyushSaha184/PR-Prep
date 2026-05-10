"""Reduce parallel AST results into canonical state."""

from __future__ import annotations

from collections import Counter
from pathlib import Path

from git import Repo

from pr_prep_agent.logger import get_logger
from pr_prep_agent.state import PRContextState

log = get_logger()


def ast_reducer(state: PRContextState) -> PRContextState:
    node = "ast_reducer"
    log.info("node_start", node=node)
    try:
        results = state.get("ast_single_results", [])
        succeeded = [item for item in results if item.get("status") == "ok"]
        failed = [item for item in results if item.get("status") != "ok"]

        ast_results = list(succeeded)
        failed_files = [str(item.get("file")) for item in failed if item.get("file")]
        parsed_files = {item.get("file") for item in results}

        for file_info in state.get("staged_files", []):
            path = str(file_info["path"])
            if path in parsed_files:
                continue
            if file_info.get("is_binary"):
                ast_results.append({"file": path, "change_type": "binary", "detail": "Binary file"})
            elif file_info.get("language") is None:
                failed_files.append(path)

        breaking_details: list[str] = []
        for item in succeeded:
            for symbol in item.get("breaking_changes", []):
                breaking_details.append(f"`{item['file']}` removed `{symbol}`")

        state["ast_results"] = ast_results
        state["ast_failed_files"] = sorted(set(failed_files))
        state["breaking_change_details"] = breaking_details
        state["is_breaking_change"] = bool(breaking_details)
        state["tests_modified"] = any(
            bool(item.get("is_test")) for item in state.get("staged_files", [])
        )
        state["reviewer_suggestions"] = _reviewer_suggestions(state)
        state["used_fallback"] = bool(state["ast_failed_files"])
        log.info("node_complete", node=node)
        return state
    except Exception as exc:
        log.exception("node_failed", node=node, reason=str(exc))
        raise RuntimeError(f"{node}: {exc}") from exc


def _reviewer_suggestions(state: PRContextState) -> list[str]:
    repo_path = Path(state["repo_path"])
    try:
        repo = Repo(str(repo_path), search_parent_directories=True)
    except Exception:
        return []
    names: list[str] = []
    for file_info in state.get("staged_files", [])[:5]:
        try:
            output = repo.git.log("--follow", "--format=%an", "--", file_info["path"])
        except Exception:
            continue
        counter = Counter(line.strip() for line in output.splitlines() if line.strip())
        for name, _count in counter.most_common(3):
            if name not in names:
                names.append(name)
            if len(names) >= 5:
                return names
    return names
