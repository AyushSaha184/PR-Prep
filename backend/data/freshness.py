"""Freshness tracker for repository file indexing."""
from typing import Any

from backend.observability.logging import setup_logger

logger = setup_logger("pr_prep.data.freshness")


class FreshnessTracker:
    """Tracks file SHA freshness to determine incremental re-embedding requirements."""

    def __init__(self) -> None:
        self._file_index: dict[str, dict[str, Any]] = {}

    def is_file_stale(self, repo: str, file_path: str, current_sha: str) -> bool:
        key = f"{repo}:{file_path}"
        entry = self._file_index.get(key)
        if not entry:
            logger.info(f"FreshnessTracker: {key} not found; marked STALE for initial embedding.")
            return True

        if entry.get("file_sha") != current_sha:
            old_sha = entry.get("file_sha", "")[:7]
            logger.info(f"FreshnessTracker: {key} SHA changed ({old_sha} -> {current_sha[:7]}).")
            return True

        logger.info(f"FreshnessTracker: {key} is FRESH (SHA matches {current_sha[:7]}).")
        return False

    def update_file_index(
        self, repo: str, file_path: str, file_sha: str, commit_sha: str, chunk_count: int
    ) -> None:
        key = f"{repo}:{file_path}"
        self._file_index[key] = {
            "file_sha": file_sha,
            "commit_sha": commit_sha,
            "chunk_count": chunk_count,
        }
        logger.info(f"FreshnessTracker updated index for {key} with {chunk_count} chunks.")
