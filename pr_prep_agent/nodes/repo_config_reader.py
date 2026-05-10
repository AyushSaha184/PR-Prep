"""Read repository-level PR metadata."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from pr_prep_agent.logger import get_logger
from pr_prep_agent.state import PRContextState

log = get_logger()


def repo_config_reader(state: PRContextState) -> PRContextState:
    node = "repo_config_reader"
    log.info("node_start", node=node)
    try:
        repo_path = Path(state["repo_path"])
        state["pr_template"] = _first_existing(
            repo_path,
            [
                ".github/pull_request_template.md",
                ".github/PULL_REQUEST_TEMPLATE.md",
                "pull_request_template.md",
            ],
        )
        state["codeowners"] = _first_existing(repo_path, [".github/CODEOWNERS", "CODEOWNERS"])
        state["past_pr_styles"] = _past_pr_styles(
            repo_path, state.get("config", {}).get("max_past_prs", 5)
        )
        log.info("node_complete", node=node)
        return state
    except Exception as exc:
        log.exception("node_failed", node=node, reason=str(exc))
        raise RuntimeError(f"{node}: {exc}") from exc


def _first_existing(repo_path: Path, candidates: list[str]) -> str | None:
    for candidate in candidates:
        path = repo_path / candidate
        if path.exists():
            return path.read_text(encoding="utf-8")
    return None


def _past_pr_styles(repo_path: Path, limit: int) -> list[str]:
    try:
        result = subprocess.run(
            [
                "gh",
                "pr",
                "list",
                "--state",
                "merged",
                "--limit",
                str(limit),
                "--json",
                "title,body",
            ],
            cwd=repo_path,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=True,
        )
        data: Any = json.loads(result.stdout)
        if not isinstance(data, list):
            return []
        return [
            f"{item.get('title', '')}\n\n{item.get('body', '')}".strip() for item in data[:limit]
        ]
    except Exception:
        log.warning("missing_gh_or_pr_styles")
        return []
