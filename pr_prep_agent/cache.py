"""MD5 keyed local cache for generated PR structures."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pr_prep_agent.logger import get_logger

log = get_logger()


def _cache_path(repo_path: str | Path) -> Path:
    return Path(repo_path) / ".prprep" / "cache.json"


def _ensure_gitignore(repo_path: str | Path) -> None:
    try:
        path = Path(repo_path) / ".gitignore"
        existing = path.read_text(encoding="utf-8") if path.exists() else ""
        if ".prprep/" not in existing.splitlines():
            suffix = "" if existing.endswith("\n") or not existing else "\n"
            path.write_text(f"{existing}{suffix}.prprep/\n", encoding="utf-8")
    except Exception as exc:  # pragma: no cover - intentionally best effort
        log.warning("cache_gitignore_skip", reason=str(exc))


def load(diff_hash: str, repo_path: str | Path) -> dict[str, Any] | None:
    """Return a cached PR structure for a diff hash, or None."""
    try:
        _ensure_gitignore(repo_path)
        path = _cache_path(repo_path)
        if not path.exists():
            log.warning("cache_miss", diff_hash=diff_hash)
            return None
        data = json.loads(path.read_text(encoding="utf-8"))
        entry = data.get(diff_hash)
        if not entry:
            log.warning("cache_miss", diff_hash=diff_hash)
            return None
        log.warning("cache_hit", diff_hash=diff_hash)
        pr_structure = entry.get("pr_structure")
        return pr_structure if isinstance(pr_structure, dict) else None
    except Exception as exc:
        log.warning("cache_load_skip", reason=str(exc))
        return None


def save(
    diff_hash: str,
    repo_path: str | Path,
    pr_structure: dict[str, Any],
    branch: str = "",
) -> None:
    """Write or update the cache entry. Cache failures never fail the run."""
    try:
        _ensure_gitignore(repo_path)
        path = _cache_path(repo_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        data: dict[str, Any] = {}
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
        data[diff_hash] = {
            "pr_structure": pr_structure,
            "created_at": datetime.now(UTC).isoformat(),
            "branch": branch,
        }
        path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
    except Exception as exc:
        log.warning("cache_save_skip", reason=str(exc))


def clear(repo_path: str | Path) -> None:
    """Delete the local cache file if present."""
    try:
        path = _cache_path(repo_path)
        if path.exists():
            path.unlink()
    except Exception as exc:
        log.warning("cache_clear_skip", reason=str(exc))
