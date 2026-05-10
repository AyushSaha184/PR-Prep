"""GitHub CLI integration."""

from __future__ import annotations

import shutil
import subprocess
from typing import Any

from rich.console import Console


def gh_cli_execution(
    title: str,
    pr_markdown: str,
    base_branch: str,
    reviewer_suggestions: list[str],
    console: Console | None = None,
) -> str | None:
    """Create a GitHub PR using gh, degrading gracefully on failure."""
    console = console or Console()
    if shutil.which("gh") is None:
        console.print("[yellow]gh CLI is unavailable. Paste the PR body manually.[/yellow]")
        console.print(pr_markdown)
        return None
    command: list[str] = [
        "gh",
        "pr",
        "create",
        "--title",
        title,
        "--body",
        pr_markdown,
        "--base",
        base_branch,
    ]
    for reviewer in reviewer_suggestions:
        command.extend(["--reviewer", reviewer])
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
    except (OSError, subprocess.CalledProcessError) as exc:
        detail = getattr(exc, "stderr", "") or str(exc)
        console.print(f"[yellow]gh pr create failed: {detail}[/yellow]")
        console.print(pr_markdown)
        return None
    url = result.stdout.strip()
    console.print(f"[green]Pull request created:[/green] {url}")
    return url


def command_exists(name: str) -> bool:
    return shutil.which(name) is not None


def run_json_command(command: list[str]) -> Any:
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    return result.stdout
