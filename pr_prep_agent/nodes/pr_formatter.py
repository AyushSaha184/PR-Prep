"""Format PR JSON into markdown and cache it."""

from __future__ import annotations

from typing import Any

from rich.console import Console
from rich.panel import Panel

from pr_prep_agent import cache
from pr_prep_agent.logger import get_logger
from pr_prep_agent.state import PRContextState

log = get_logger()


def pr_formatter(state: PRContextState) -> PRContextState:
    node = "pr_formatter"
    log.info("node_start", node=node)
    try:
        pr_structure = state.get("pr_structure") or {}
        markdown = format_pr_markdown(pr_structure, state)
        state["pr_markdown"] = markdown
        if state.get("route_decision") == "cached":
            Console().print("[cyan]Loaded PR draft from cache.[/cyan]")
        if state.get("route_decision") not in {"trivial", "cached"} and state.get("diff_hash"):
            cache.save(
                state["diff_hash"],
                state["repo_path"],
                dict(pr_structure),
                state.get("current_branch", ""),
            )
        Console().print(Panel(markdown, title=str(pr_structure.get("title", "Pull Request"))))
        log.info("node_complete", node=node)
        return state
    except Exception as exc:
        log.exception("node_failed", node=node, reason=str(exc))
        raise RuntimeError(f"{node}: {exc}") from exc


def format_pr_markdown(pr_structure: dict[str, Any], state: PRContextState) -> str:
    if state.get("pr_template"):
        body = _inject_template(str(state["pr_template"]), pr_structure)
    else:
        body = _default_markdown(pr_structure)
    if state.get("is_breaking_change"):
        details = "\n".join(f"- {item}" for item in state.get("breaking_change_details", []))
        body = f"## ⚠️ BREAKING CHANGE\n{details}\n\n{body}"
    return body.strip() + "\n"


def _default_markdown(pr: dict[str, Any]) -> str:
    changes = "\n".join(f"- {item}" for item in pr.get("changes", [])) or "- None"
    reviewers = "\n".join(f"- {item}" for item in pr.get("reviewer_suggestions", [])) or "- None"
    linked = "\n".join(f"- {item}" for item in pr.get("linked_issues", [])) or "- None"
    breaking = pr.get("breaking_change_note") or "None"
    return (
        f"## Summary\n{pr.get('summary', '')}\n\n"
        f"## Changes\n{changes}\n\n"
        f"## Breaking Changes\n{breaking}\n\n"
        f"## Testing\n{pr.get('testing_notes', '')}\n\n"
        f"## Risk\n{pr.get('risk_level', 'medium')}\n\n"
        f"## Reviewers\n{reviewers}\n\n"
        f"## Related Issues\n{linked}"
    )


def _inject_template(template: str, pr: dict[str, Any]) -> str:
    replacements = {
        "<!-- What does this PR do? -->": str(pr.get("summary", "")),
        "<!-- Bullet list of specific changes -->": "\n".join(
            f"- {item}" for item in pr.get("changes", [])
        ),
        '<!-- If none, write "None" -->': str(pr.get("breaking_change_note") or "None"),
        "<!-- How was this tested? -->": str(pr.get("testing_notes", "")),
        "<!-- e.g. Closes #123 -->": "\n".join(str(item) for item in pr.get("linked_issues", []))
        or "None",
    }
    output = template
    for marker, value in replacements.items():
        output = output.replace(marker, value)
    return output
