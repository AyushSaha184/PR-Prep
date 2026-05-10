"""CLI entry point for pr-prep."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Any, cast

import typer
from rich.console import Console
from rich.panel import Panel

try:
    import langgraph.types as langgraph_types
except ImportError:  # pragma: no cover
    langgraph_types = None  # type: ignore[assignment]

from pr_prep_agent import cache
from pr_prep_agent.config import load_config
from pr_prep_agent.graph import build_graph
from pr_prep_agent.logger import setup_logger
from pr_prep_agent.state import PRContextState
from pr_prep_agent.tools.gh_tools import gh_cli_execution
from pr_prep_agent.tools.git_tools import get_repo

app = typer.Typer(help="Prepare GitHub pull requests from staged changes.")
console = Console()


@app.command(default=True)
def run(
    repo: Annotated[Path, typer.Option("--repo", help="Git repo path.")] = Path("."),
    debug: Annotated[bool, typer.Option("--debug", help="Verbose logging.")] = False,
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Skip gh pr create.")] = False,
    no_clipboard: Annotated[
        bool, typer.Option("--no-clipboard", help="Skip clipboard copy.")
    ] = False,
    clear_cache: Annotated[
        bool, typer.Option("--clear-cache", help="Delete .prprep/cache.json and exit.")
    ] = False,
) -> None:
    setup_logger(debug)
    repo_path = Path(repo).resolve()
    git_repo = get_repo(repo_path)
    root = Path(git_repo.working_tree_dir or repo_path).resolve()
    config = load_config(root)

    if clear_cache:
        cache.clear(root)
        console.print("[green]Cache cleared.[/green]")
        raise typer.Exit(0)

    if not config.gemini_api_key:
        console.print(
            Panel(
                "GEMINI_API_KEY is required. Set it in the environment, ~/.prprep.toml, "
                "or .prprep.toml.",
                title="Configuration Error",
                style="red",
            )
        )
        raise typer.Exit(1)

    state: PRContextState = {
        "repo_path": str(root),
        "staged_files": [],
        "raw_diff": "",
        "diff_hash": "",
        "diff_was_chunked": False,
        "commit_history": [],
        "linked_issues": [],
        "is_first_commit": False,
        "is_detached_head": False,
        "current_branch": "",
        "pr_template": None,
        "codeowners": None,
        "past_pr_styles": [],
        "config": config.to_dict(),
        "dry_run": dry_run,
        "no_clipboard": no_clipboard,
        "route_decision": "",
        "trivial_reason": None,
        "ast_results": [],
        "ast_single_results": [],
        "ast_failed_files": [],
        "used_fallback": False,
        "is_breaking_change": False,
        "breaking_change_details": [],
        "tests_modified": False,
        "test_coverage_gaps": [],
        "reviewer_suggestions": [],
        "pr_structure": None,
        "pr_markdown": None,
        "user_action": None,
    }

    graph = build_graph(interrupt_before=["human_review_gate"])
    final_state = _run_graph_until_review(graph, state)

    final_state = _resume_after_review(graph, final_state)

    if final_state.get("user_action") == "submit":
        if dry_run:
            console.print("[yellow]Dry run: skipped gh pr create.[/yellow]")
            return
        pr_structure = final_state.get("pr_structure") or {}
        gh_cli_execution(
            str(pr_structure.get("title", "Pull request")),
            final_state.get("pr_markdown") or "",
            config.base_branch,
            list(pr_structure.get("reviewer_suggestions", [])),
            console,
        )


def _merge_state(target: PRContextState, source: dict) -> PRContextState:
    """Merge source dict into target, extending lists instead of overwriting."""
    for key, value in source.items():
        if key in target and isinstance(target[key], list) and isinstance(value, list):
            target[key].extend(value)  # type: ignore[arg-type]
        else:
            target[key] = value  # type: ignore[literal-required]
    return target


def _run_graph_until_review(graph: Any, state: PRContextState) -> PRContextState:
    latest: PRContextState = state
    for event in graph.stream(state):
        if isinstance(event, dict):
            for value in event.values():
                if isinstance(value, dict):
                    _merge_state(latest, cast(PRContextState, value))
    return latest


def _resume_after_review(graph: Any, state: PRContextState) -> PRContextState:
    command_cls = getattr(langgraph_types, "Command", None)
    if command_cls is None:
        return state
    latest: PRContextState = state
    try:
        for event in graph.stream(command_cls(resume=state)):
            if isinstance(event, dict):
                for value in event.values():
                    if isinstance(value, dict):
                        _merge_state(latest, cast(PRContextState, value))
    except Exception:
        return state
    return latest


if __name__ == "__main__":
    app()
