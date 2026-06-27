from pathlib import Path


def extract_readme(project_path: Path) -> str:
    """Read README.md or README.rst and return full content."""
    for name in ("README.md", "README.rst", "readme.md", "readme.rst"):
        candidate = project_path / name
        if candidate.exists():
            return candidate.read_text(encoding="utf-8", errors="ignore")
    return ""