"""LangGraph wiring for PR Prep Agent."""

from __future__ import annotations

from typing import Any, Literal, cast

from langgraph.graph import END, StateGraph

from pr_prep_agent.nodes.ast_file_router import ast_file_router, ast_file_router_node
from pr_prep_agent.nodes.ast_reducer import ast_reducer
from pr_prep_agent.nodes.ast_single_file import ast_single_file
from pr_prep_agent.nodes.git_diff_reader import git_diff_reader
from pr_prep_agent.nodes.human_review_gate import human_review_gate
from pr_prep_agent.nodes.intent_deduction import intent_deduction
from pr_prep_agent.nodes.pr_formatter import pr_formatter
from pr_prep_agent.nodes.raw_diff_fallback import raw_diff_fallback
from pr_prep_agent.nodes.repo_config_reader import repo_config_reader
from pr_prep_agent.nodes.short_circuit_router import short_circuit_router
from pr_prep_agent.nodes.test_coverage_assessor import test_coverage_assessor
from pr_prep_agent.nodes.trivial_formatter import trivial_formatter
from pr_prep_agent.state import PRContextState


def build_graph(interrupt_before: list[str] | None = None) -> Any:
    graph = StateGraph(PRContextState)
    graph.add_node("repo_config_reader", repo_config_reader)
    graph.add_node("git_diff_reader", git_diff_reader)
    graph.add_node("short_circuit_router", short_circuit_router)
    graph.add_node("trivial_formatter", trivial_formatter)
    graph.add_node("ast_file_router", ast_file_router_node)
    graph.add_node("ast_single_file", cast(Any, ast_single_file))
    graph.add_node("ast_reducer", ast_reducer)
    graph.add_node("raw_diff_fallback", raw_diff_fallback)
    graph.add_node("test_coverage_assessor", test_coverage_assessor)
    graph.add_node("intent_deduction", intent_deduction)
    graph.add_node("pr_formatter", pr_formatter)
    graph.add_node("human_review_gate", human_review_gate)

    graph.set_entry_point("repo_config_reader")
    graph.add_edge("repo_config_reader", "git_diff_reader")
    graph.add_conditional_edges(
        "git_diff_reader",
        _after_git_diff,
        {"cached": "pr_formatter", "continue": "short_circuit_router"},
    )
    graph.add_conditional_edges(
        "short_circuit_router",
        _after_short_circuit,
        {"trivial": "trivial_formatter", "llm": "ast_file_router"},
    )
    graph.add_edge("trivial_formatter", "pr_formatter")
    graph.add_conditional_edges(
        "ast_file_router",
        ast_file_router,
        {
            "fan_out": "ast_single_file",
            "single": "ast_reducer",
        },
    )
    graph.add_edge("ast_single_file", "ast_reducer")
    graph.add_conditional_edges(
        "ast_reducer",
        _after_ast_reducer,
        {
            "fallback": "raw_diff_fallback",
            "test_coverage": "test_coverage_assessor",
            "intent": "intent_deduction",
        },
    )
    graph.add_conditional_edges(
        "raw_diff_fallback",
        _after_test_gate,
        {"test_coverage": "test_coverage_assessor", "intent": "intent_deduction"},
    )
    graph.add_edge("test_coverage_assessor", "intent_deduction")
    graph.add_edge("intent_deduction", "pr_formatter")
    graph.add_edge("pr_formatter", "human_review_gate")
    graph.add_edge("human_review_gate", END)
    return graph.compile(interrupt_before=interrupt_before or [])


def _after_git_diff(state: PRContextState) -> Literal["cached", "continue"]:
    return "cached" if state.get("route_decision") == "cached" else "continue"


def _after_short_circuit(state: PRContextState) -> Literal["trivial", "llm"]:
    return "trivial" if state.get("route_decision") == "trivial" else "llm"


def _after_ast_reducer(state: PRContextState) -> Literal["fallback", "test_coverage", "intent"]:
    if state.get("ast_failed_files"):
        return "fallback"
    return _after_test_gate(state)


def _after_test_gate(state: PRContextState) -> Literal["test_coverage", "intent"]:
    return "test_coverage" if state.get("tests_modified") else "intent"
