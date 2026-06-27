import json
from pathlib import Path

MAX_FILE_SIZE = 50_000  # 50KB — dependency files are always small

BINARY_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".pdf",
    ".zip", ".tar", ".gz", ".exe", ".dll", ".so", ".dylib",
    ".woff", ".woff2", ".ttf", ".eot", ".bin", ".pyc",
}


def _list_depth_one_files(project_path: Path) -> list[Path]:
    """
    List readable files at project root depth only.
    Excludes:
      - Hidden files and .env files (anything starting with '.')
      - Files ending with .env (e.g. production.env)
      - Binary file types
      - Files larger than MAX_FILE_SIZE
    """
    files = []
    for p in project_path.iterdir():
        if not p.is_file():
            continue
        if p.name.startswith("."):       # covers .env, .env.local, .gitignore, etc.
            continue
        if p.suffix == ".env":           # covers production.env, local.env, etc.
            continue
        if p.suffix in BINARY_EXTENSIONS:
            continue
        if p.stat().st_size > MAX_FILE_SIZE:
            continue
        files.append(p)
    return sorted(files)


def extract_deps(project_path: Path) -> list[str]:
    """
    Dynamically identify dependency files at project root using LLM,
    then extract package names from their content.
    Handles any ecosystem: Python, Node, Go, Rust, Java, PHP, Ruby, etc.
    """
    from langchain_google_vertexai import ChatVertexAI
    from config import GOOGLE_PROJECT_ID, GOOGLE_LOCATION, GEMINI_MODEL

    files = _list_depth_one_files(project_path)
    if not files:
        return []

    file_names = [f.name for f in files]
    llm = ChatVertexAI(model=GEMINI_MODEL, project=GOOGLE_PROJECT_ID, location=GOOGLE_LOCATION)

    # Step 1: ask LLM which files contain dependency information
    identify_prompt = f"""These files exist at the root of a software project:
{chr(10).join(f'- {n}' for n in file_names)}

Which of these files likely contain package or dependency information?
Examples of dependency files: requirements.txt, package.json, Pipfile, pyproject.toml,
go.mod, Cargo.toml, pom.xml, build.gradle, composer.json, Gemfile, mix.exs, etc.

Return JSON only:
{{"dependency_files": [str]}}
Only include filenames from the list above. Return empty list if none qualify."""

    r1 = llm.invoke(identify_prompt)
    raw1 = r1.content.strip().removeprefix("```json").removesuffix("```").strip()
    dep_names = json.loads(raw1).get("dependency_files", [])

    if not dep_names:
        return []

    # Step 2: read identified files and extract package names
    blocks = []
    for name in dep_names:
        p = project_path / name
        if p.exists() and p.is_file():
            try:
                content = p.read_text(encoding="utf-8", errors="ignore")
                blocks.append(f"=== {name} ===\n{content}")
            except Exception:
                pass

    if not blocks:
        return []

    extract_prompt = f"""Extract all package and dependency names from these files.
Strip version specifiers, extras, URLs, and comments.

{chr(10).join(blocks)}

Return JSON only:
{{"packages": [str]}}
Return lowercase package names only. No versions, no duplicates."""

    r2 = llm.invoke(extract_prompt)
    raw2 = r2.content.strip().removeprefix("```json").removesuffix("```").strip()
    packages = json.loads(raw2).get("packages", [])

    return sorted({p.lower().strip() for p in packages if p.strip()})
