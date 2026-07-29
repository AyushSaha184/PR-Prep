"""AST-based import boundary tests enforcing modular monolith dependency rules."""
import ast
from pathlib import Path

BACKEND_DIR = Path(__file__).parent.parent / "backend"


def test_core_module_has_zero_external_backend_dependencies() -> None:
    """Core module must not import any other backend module."""
    core_dir = BACKEND_DIR / "core"
    for py_file in core_dir.glob("*.py"):
        tree = ast.parse(py_file.read_text(), filename=str(py_file))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    is_core = alias.name.startswith("backend.core")
                    is_backend = alias.name.startswith("backend.")
                    assert not is_backend or is_core, (
                        f"Core violation in {py_file.name}: imports {alias.name}"
                    )
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    is_core_mod = node.module.startswith("backend.core")
                    is_backend_mod = node.module.startswith("backend.")
                    assert not is_backend_mod or is_core_mod, (
                        f"Core violation in {py_file.name}: imports from {node.module}"
                    )


def test_models_module_has_no_outer_backend_dependencies() -> None:
    """Models module must only import core or models, not outer modules."""
    allowed_prefixes = ("backend.core", "backend.models")
    models_dir = BACKEND_DIR / "models"
    for py_file in models_dir.glob("*.py"):
        tree = ast.parse(py_file.read_text(), filename=str(py_file))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.startswith("backend."):
                        assert any(alias.name.startswith(p) for p in allowed_prefixes), (
                            f"Models violation in {py_file.name}: imports {alias.name}"
                        )
            elif isinstance(node, ast.ImportFrom):
                if node.module and node.module.startswith("backend."):
                    assert any(node.module.startswith(p) for p in allowed_prefixes), (
                        f"Models violation in {py_file.name}: imports from {node.module}"
                    )
