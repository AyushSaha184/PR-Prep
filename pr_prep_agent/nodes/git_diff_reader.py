"""Read staged git diff and derive repository context."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from git import GitCommandError

from pr_prep_agent import cache
from pr_prep_agent.logger import get_logger
from pr_prep_agent.state import PRContextState
from pr_prep_agent.tools.git_tools import (
    chunk_diff,
    extract_linked_issues,
    get_repo,
    parse_name_status,
)

log = get_logger()


def git_diff_reader(state: PRContextState) -> PRContextState:
    node = "git_diff_reader"
    log.info("node_start", node=node)
    try:
        repo_path = Path(state["repo_path"])
        repo = get_repo(repo_path)
        raw_diff = repo.git.diff("--cached", "--find-renames", "--no-color")
        name_status = repo.git.diff("--cached", "--name-status", "--find-renames", "--no-color")
        if not raw_diff.strip() and not name_status.strip():
            raise RuntimeError("No staged changes found. Run `git add` first.")

        state["diff_hash"] = hashlib.md5(raw_diff.encode("utf-8")).hexdigest()
        repo_root = str(repo.working_tree_dir or repo_path)
        state["staged_files"] = parse_name_status(name_status, repo_root)
        state["raw_diff"], state["diff_was_chunked"] = chunk_diff(
            raw_diff,
            int(state.get("config", {}).get("max_diff_lines", 800)),
            int(state.get("config", {}).get("chunk_size_lines", 200)),
        )
        state["is_detached_head"], state["current_branch"] = _branch_info(repo)
        state["commit_history"], state["is_first_commit"] = _commit_history(
            repo,
            int(state.get("config", {}).get("max_commit_history", 20)),
        )
        issue_texts = [
            raw_diff,
            *[str(item.get("message", "")) for item in state["commit_history"]],
        ]
        state["linked_issues"] = extract_linked_issues(*issue_texts)

        cached = cache.load(state["diff_hash"], repo_root)
        if cached is not None:
            state["pr_structure"] = cached
            state["route_decision"] = "cached"

        log.info("node_complete", node=node)
        return state
    except RuntimeError:
        raise
    except Exception as exc:
        log.exception("node_failed", node=node, reason=str(exc))
        raise RuntimeError(f"{node}: {exc}") from exc


def _branch_info(repo: Any) -> tuple[bool, str]:
    try:
        return False, str(repo.active_branch)
    except TypeError:
        sha = repo.head.commit.hexsha[:8]
        log.warning("detached_head", sha=sha)
        return True, sha


def _commit_history(repo: Any, limit: int) -> tuple[list[dict[str, Any]], bool]:
    try:
        commits = list(repo.iter_commits(max_count=limit))
    except (ValueError, GitCommandError):
        log.warning("empty_history")
        return [], True
    if not commits:
        log.warning("empty_history")
        return [], True
    history = [
        {
            "hash": commit.hexsha[:8],
            "message": commit.message.strip(),
            "author": getattr(commit.author, "name", ""),
            "date": commit.committed_datetime.isoformat(),
        }
        for commit in commits
    ]
    return history, False
