import hashlib
import json
from pathlib import Path
from models.schemas import ProjectSummary

WATCHED_FILES = (
    "README.md", "README.rst", "readme.md",
    "requirements.txt", "package.json", "pyproject.toml", "go.mod",
)


SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", "migrations"}


def compute_project_hash(project_path: Path) -> str:
    """Hash mtimes of README, dependency files, and all .py files (recursive)."""
    h = hashlib.md5()

    for name in WATCHED_FILES:
        f = project_path / name
        if f.exists():
            h.update(f"{name}:{f.stat().st_mtime}".encode())

    for f in sorted(project_path.rglob("*.py")):
        if not any(part in SKIP_DIRS for part in f.parts):
            h.update(f"{f.relative_to(project_path)}:{f.stat().st_mtime}".encode())

    return h.hexdigest()


def load_cache(cache_file: Path) -> dict:
    """Load cache from JSON file. Returns empty dict if file does not exist."""
    if not cache_file.exists():
        return {}
    try:
        return json.loads(cache_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def save_cache(cache_file: Path, cache: dict) -> None:
    """Persist cache dict to JSON file."""
    cache_file.write_text(json.dumps(cache, indent=2), encoding="utf-8")


def get_cached_summary(cache: dict, project_name: str, content_hash: str) -> ProjectSummary | None:
    """Return cached ProjectSummary if hash matches, else None."""
    entry = cache.get(project_name)
    if entry and entry.get("hash") == content_hash:
        return ProjectSummary(**entry["summary"])
    return None


def set_cached_summary(cache: dict, project_name: str, content_hash: str, summary: ProjectSummary) -> None:
    """Store a ProjectSummary in the cache dict (in-memory; call save_cache to persist)."""
    cache[project_name] = {
        "hash": content_hash,
        "summary": summary.model_dump(),
    }
