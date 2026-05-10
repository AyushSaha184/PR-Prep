"""Deduce PR intent using Gemini."""

from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from rich.console import Console

from pr_prep_agent.llm.gemini_adapter import GeminiAdapter, strip_json_fences
from pr_prep_agent.logger import get_logger
from pr_prep_agent.state import PRContextState

log = get_logger()


def intent_deduction(state: PRContextState) -> PRContextState:
    node = "intent_deduction"
    log.info("node_start", node=node)
    try:
        config = state.get("config", {})
        model = (
            config.get("flash_model")
            if state.get("route_decision") == "flash"
            else config.get("pro_model")
        )
        adapter = GeminiAdapter(
            api_key=str(config["gemini_api_key"]),
            model=str(model),
            retry_attempts=int(config.get("retry_attempts", 3)),
            retry_wait=float(config.get("retry_wait", 2.0)),
        )
        console = Console()
        if state.get("used_fallback") or state.get("diff_was_chunked"):
            pr_structure = _large_diff_path(state, config, console)
        else:
            prompt = _build_prompt(state)
            streamed = adapter.complete_streaming(prompt, console)
            pr_structure = json.loads(strip_json_fences(streamed))
        state["pr_structure"] = pr_structure
        log.info("node_complete", node=node)
        return state
    except Exception as exc:
        log.exception("node_failed", node=node, reason=str(exc))
        raise RuntimeError(f"{node}: {exc}") from exc


def _large_diff_path(
    state: PRContextState,
    config: dict[str, Any],
    console: Console,
) -> dict[str, Any]:
    flash = GeminiAdapter(
        api_key=str(config["gemini_api_key"]),
        model=str(config.get("flash_model", "gemini-1.5-flash")),
        retry_attempts=int(config.get("retry_attempts", 3)),
        retry_wait=float(config.get("retry_wait", 2.0)),
    )
    pro = GeminiAdapter(
        api_key=str(config["gemini_api_key"]),
        model=str(config.get("pro_model", "gemini-1.5-pro")),
        retry_attempts=int(config.get("retry_attempts", 3)),
        retry_wait=float(config.get("retry_wait", 2.0)),
    )

    def summarize(item: dict[str, Any]) -> str:
        prompt = (
            "Summarize this file change in 2 concise sentences for a pull request.\n"
            f"File change:\n{json.dumps(item, indent=2)}"
        )
        return flash.complete(prompt)

    with ThreadPoolExecutor(max_workers=6) as executor:
        summaries = list(executor.map(summarize, state.get("ast_results", [])))
    final_prompt = _build_prompt(state, file_summaries=summaries)
    streamed = pro.complete_streaming(final_prompt, console)
    return dict(json.loads(strip_json_fences(streamed)))


def _build_prompt(state: PRContextState, file_summaries: list[str] | None = None) -> str:
    parts = [
        "You are preparing a GitHub pull request from staged local changes.",
        f"Branch: {state.get('current_branch', '')}",
        f"Linked issues: {state.get('linked_issues', [])}",
        f"AST results: {json.dumps(state.get('ast_results', []), indent=2)}",
        f"Breaking changes: {state.get('breaking_change_details', [])}",
        f"Test coverage gaps: {state.get('test_coverage_gaps', [])}",
        f"Reviewer suggestions: {state.get('reviewer_suggestions', [])}",
    ]
    if file_summaries:
        parts.append(
            "Per-file summaries:\n" + "\n".join(f"- {summary}" for summary in file_summaries)
        )
    if not state.get("is_first_commit"):
        parts.append(f"Commit history: {json.dumps(state.get('commit_history', []), indent=2)}")
    if state.get("pr_template"):
        parts.append(f"PR template:\n{state['pr_template']}")
    if state.get("past_pr_styles"):
        parts.append(f"Tone reference from a past PR:\n{state['past_pr_styles'][0]}")
    parts.append(
        "Respond ONLY with a JSON object with exactly these keys: "
        "title (string, imperative mood, max 72 chars), summary (2-4 sentences), "
        "changes (list of strings), breaking_change_note (null or string), "
        "testing_notes (string), reviewer_suggestions (list of strings), "
        'risk_level ("low" | "medium" | "high"), linked_issues (list of strings).'
    )
    return "\n\n".join(parts)
