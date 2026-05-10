"""Tree-sitter based symbol extraction with regex fallbacks."""

from __future__ import annotations

import re
from importlib import import_module
from pathlib import Path
from typing import Any

SYMBOL_NODE_TYPES = {
    "function_definition",
    "function_declaration",
    "method_definition",
    "class_definition",
    "class_declaration",
    "function_item",
    "impl_item",
}

SUPPORTED_LANGUAGES = {"python", "javascript", "typescript", "java", "go", "rust", "cpp"}


def extract_symbols(content: str, language: str) -> list[str]:
    """Extract top-level symbol names from source text.

    Tree-sitter package APIs have changed across releases, so this function attempts
    tree-sitter first and uses conservative regex extraction as a stable fallback.
    """
    if language not in SUPPORTED_LANGUAGES:
        raise ValueError(f"Unsupported language: {language}")
    try:
        symbols = _extract_with_tree_sitter(content, language)
        if symbols:
            return sorted(set(symbols))
    except Exception:
        pass
    return sorted(set(_extract_with_regex(content, language)))


def _extract_with_tree_sitter(content: str, language: str) -> list[str]:
    from tree_sitter import Language, Parser

    module = _language_module(language)
    language_obj: Any = (
        Language(module.language()) if hasattr(module, "language") else module.language()
    )

    parser = Parser()
    if hasattr(parser, "set_language"):
        parser.set_language(language_obj)
    else:
        parser.language = language_obj
    tree = parser.parse(content.encode("utf-8"))
    symbols: list[str] = []
    _walk_tree(tree.root_node, content.encode("utf-8"), symbols)
    return symbols


def _language_module(language: str) -> Any:
    module_names = {
        "python": "tree_sitter_python",
        "javascript": "tree_sitter_javascript",
        "typescript": "tree_sitter_typescript",
        "java": "tree_sitter_java",
        "go": "tree_sitter_go",
        "rust": "tree_sitter_rust",
        "cpp": "tree_sitter_cpp",
    }
    module_name = module_names.get(language)
    if module_name is None:
        raise ValueError(f"Unsupported language: {language}")
    return import_module(module_name)


def _walk_tree(node: Any, source: bytes, symbols: list[str]) -> None:
    if node.type in SYMBOL_NODE_TYPES:
        name_node = node.child_by_field_name("name")
        if name_node is not None:
            symbols.append(source[name_node.start_byte : name_node.end_byte].decode("utf-8"))
    for child in node.children:
        _walk_tree(child, source, symbols)


def _extract_with_regex(content: str, language: str) -> list[str]:
    patterns = {
        "python": [
            r"^\s*def\s+([A-Za-z_][\w]*)\s*\(",
            r"^\s*class\s+([A-Za-z_][\w]*)\b",
        ],
        "javascript": [
            r"^\s*(?:export\s+)?function\s+([A-Za-z_$][\w$]*)\s*\(",
            r"^\s*(?:export\s+)?class\s+([A-Za-z_$][\w$]*)\b",
            r"^\s*(?:export\s+)?(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?\(",
        ],
        "typescript": [
            r"^\s*(?:export\s+)?function\s+([A-Za-z_$][\w$]*)\s*\(",
            r"^\s*(?:export\s+)?class\s+([A-Za-z_$][\w$]*)\b",
            r"^\s*(?:export\s+)?(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?\(",
        ],
        "java": [
            r"^\s*(?:public|private|protected)?\s*(?:static\s+)?class\s+([A-Za-z_][\w]*)\b",
            r"^\s*(?:public|private|protected)?\s*(?:static\s+)?[\w<>\[\]]+\s+([A-Za-z_][\w]*)\s*\(",
        ],
        "go": [
            r"^\s*func\s+(?:\([^)]*\)\s*)?([A-Za-z_][\w]*)\s*\(",
            r"^\s*type\s+([A-Za-z_][\w]*)\s+struct\b",
        ],
        "rust": [
            r"^\s*(?:pub\s+)?fn\s+([A-Za-z_][\w]*)\s*\(",
            r"^\s*(?:pub\s+)?(?:struct|enum|trait|impl)\s+([A-Za-z_][\w]*)\b",
        ],
        "cpp": [
            r"^\s*class\s+([A-Za-z_][\w]*)\b",
            r"^\s*[\w:<>~*&\s]+\s+([A-Za-z_][\w]*)\s*\([^;]*\)\s*\{",
        ],
    }
    matches: list[str] = []
    for pattern in patterns.get(language, []):
        matches.extend(re.findall(pattern, content, flags=re.MULTILINE))
    return matches


def file_size_kb(path: str | Path) -> float:
    return Path(path).stat().st_size / 1024
