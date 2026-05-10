"""Git helper functions."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from git import Repo

from pr_prep_agent.tools.file_tools import detect_language, is_binary_file, is_test_file

ISSUE_RE = re.compile(r"\b(?:fixes|closes|resolves|refs?)\s+#(\d+)", re.IGNORECASE)


def get_repo(repo_path: str | Path) -> Repo:
    return Repo(str(repo_path), search_parent_directories=True)


def parse_name_status(name_status: str, repo_path: str | Path) -> list[dict[str, Any]]:
    files: list[dict[str, Any]] = []
    root = Path(repo_path)
    for line in name_status.splitlines():
        parts = line.split("\t")
        if not parts:
            continue
        status = parts[0]
        path = parts[-1]
        absolute = root / path
        files.append(
            {
                "path": path,
                "status": status[0],
                "language": detect_language(path),
                "is_binary": is_binary_file(absolute),
                "is_test": is_test_file(path),
            }
        )
    return files


def chunk_diff(raw_diff: str, max_lines: int, chunk_size: int) -> tuple[str, bool]:
    lines = raw_diff.splitlines()
    if len(lines) <= max_lines:
        return raw_diff, False

    sections: list[list[str]] = []
    current: list[str] = []
    for line in lines:
        if line.startswith("diff --git ") and current:
            sections.append(current)
            current = [line]
        else:
            current.append(line)
    if current:
        sections.append(current)

    output: list[str] = []
    for section in sections:
        kept = section[:chunk_size]
        output.extend(kept)
        truncated = max(0, len(section) - len(kept))
        if truncated:
            output.append(f"[{truncated} lines truncated]")
    return "\n".join(output), True


def extract_linked_issues(*texts: str) -> list[str]:
    found: list[str] = []
    for text in texts:
        for match in ISSUE_RE.finditer(text or ""):
            issue = f"#{match.group(1)}"
            if issue not in found:
                found.append(issue)
    return found
