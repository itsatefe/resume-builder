from pathlib import Path
from collections import Counter

SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", ".idea", "dist", "build"}
SKIP_EXTENSIONS = {".pyc", ".pyo", ".lock", ".log", ".map"}


def extract_dir_structure(project_path: Path, depth: int = 2) -> list[str]:
    """Return folder/file names up to `depth`, excluding hidden and generated dirs."""
    entries = []
    _walk(project_path, depth, entries, prefix="")
    return entries


def _walk(path: Path, depth: int, entries: list[str], prefix: str) -> None:
    if depth == 0:
        return
    for p in sorted(path.iterdir()):
        if p.name in SKIP_DIRS or p.name.startswith("."):
            continue
        entries.append(prefix + p.name + ("/" if p.is_dir() else ""))
        if p.is_dir():
            _walk(p, depth - 1, entries, prefix + "  ")


def extract_file_extensions(project_path: Path) -> dict[str, int]:
    """Count files per extension across the project."""
    counter: Counter = Counter()
    for p in project_path.rglob("*"):
        if p.is_file() and p.suffix and p.suffix not in SKIP_EXTENSIONS:
            parts = set(p.parts)
            if not parts.intersection(SKIP_DIRS) and not p.name.startswith("."):
                counter[p.suffix.lstrip(".")] += 1
    return dict(counter.most_common())