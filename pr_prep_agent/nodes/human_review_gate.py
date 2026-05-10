"""Human-in-the-loop review gate."""

from __future__ import annotations

import os
import subprocess
import tempfile
from contextlib import suppress
from pathlib import Path

import pyperclip
from rich.console import Console
from rich.panel import Panel

from pr_prep_agent.logger import get_logger
from pr_prep_agent.state import PRContextState

log = get_logger()


def human_review_gate(state: PRContextState) -> PRContextState:
    node = "human_review_gate"
    log.info("node_start", node=node)
    try:
        if state.get("user_action") in {"submit", "abort"}:
            log.info("node_complete", node=node, action=state.get("user_action"))
            return state
        console = Console()
        while True:
            console.print(Panel(state.get("pr_markdown") or "", title="Review Pull Request"))
            choice = console.input(
                "[bold][S][/bold]ubmit   [bold][E][/bold]dit   [bold][A][/bold]bort > "
            )
            normalized = choice.strip().lower()[:1]
            if normalized == "e":
                state["pr_markdown"] = _edit_markdown(state.get("pr_markdown") or "")
                continue
            if normalized == "s":
                state["user_action"] = "submit"
                if not state.get("no_clipboard"):
                    try:
                        pyperclip.copy(state.get("pr_markdown") or "")
                        console.print("Copied to clipboard.")
                    except Exception as exc:
                        console.print(f"[yellow]Clipboard copy failed: {exc}[/yellow]")
                log.info("node_complete", node=node, action="submit")
                return state
            if normalized == "a":
                state["user_action"] = "abort"
                console.print("Aborted.")
                log.info("node_complete", node=node, action="abort")
                return state
    except Exception as exc:
        log.exception("node_failed", node=node, reason=str(exc))
        raise RuntimeError(f"{node}: {exc}") from exc


def _edit_markdown(markdown: str) -> str:
    editor = os.environ.get("EDITOR") or "nano"
    with tempfile.NamedTemporaryFile("w+", suffix=".md", delete=False, encoding="utf-8") as handle:
        path = Path(handle.name)
        handle.write(markdown)
    try:
        subprocess.run([editor, str(path)], check=False)
        return path.read_text(encoding="utf-8")
    finally:
        with suppress(OSError):
            path.unlink()
