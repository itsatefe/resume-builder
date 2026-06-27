import ast
from pathlib import Path

STDLIB = {
    "os", "sys", "re", "json", "time", "math", "io", "abc", "copy", "enum",
    "typing", "types", "pathlib", "datetime", "logging", "functools",
    "itertools", "collections", "contextlib", "dataclasses", "threading",
    "asyncio", "hashlib", "base64", "string", "struct", "random", "uuid",
    "warnings", "traceback", "inspect", "importlib", "unittest", "subprocess",
}

SKIP_DIRS = {"migrations", "venv", ".venv", "__pycache__", ".git", "node_modules"}


def _collect_py_files(root: Path, depth: int) -> list[Path]:
    files = []
    for p in root.iterdir():
        if p.name in SKIP_DIRS or p.name.startswith("."):
            continue
        if p.is_file() and p.suffix == ".py":
            files.append(p)
        elif p.is_dir() and depth > 1:
            files.extend(_collect_py_files(p, depth - 1))
    return files


def extract_ast_signals(project_path: Path, depth: int = 2) -> dict:
    """
    Walk Python files up to `depth` and return:
    imports_used, classes, functions, decorators.
    """
    imports: set[str] = set()
    classes: list[str] = []
    functions: list[str] = []
    decorators: set[str] = set()

    for py_file in _collect_py_files(project_path, depth):
        try:
            tree = ast.parse(py_file.read_text(encoding="utf-8", errors="ignore"))
        except SyntaxError:
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    top = alias.name.split(".")[0]
                    if top not in STDLIB:
                        imports.add(top)

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    top = node.module.split(".")[0]
                    if top not in STDLIB:
                        imports.add(top)

            elif isinstance(node, ast.ClassDef):
                classes.append(node.name)
                for dec in node.decorator_list:
                    _extract_decorator(dec, decorators)

            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if not node.name.startswith("_") and not node.name.startswith("test_"):
                    functions.append(node.name)
                for dec in node.decorator_list:
                    _extract_decorator(dec, decorators)

    return {
        "imports_used": sorted(imports),
        "classes": classes,
        "functions": functions,
        "decorators": sorted(decorators),
    }


def _extract_decorator(node: ast.expr, decorators: set[str]) -> None:
    if isinstance(node, ast.Name):
        decorators.add(node.id)
    elif isinstance(node, ast.Attribute):
        decorators.add(f"{_attr_chain(node)}")
    elif isinstance(node, ast.Call):
        _extract_decorator(node.func, decorators)


def _attr_chain(node: ast.expr) -> str:
    if isinstance(node, ast.Attribute):
        return f"{_attr_chain(node.value)}.{node.attr}"
    elif isinstance(node, ast.Name):
        return node.id
    return ""