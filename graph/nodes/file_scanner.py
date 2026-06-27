import logging
import subprocess
from pathlib import Path

from extractors.ast_extractor import extract_ast_signals
from extractors.deps import extract_deps
from extractors.readme import extract_readme
from extractors.structure import extract_dir_structure, extract_file_extensions
from cache.project_cache import compute_project_hash, get_cached_summary, load_cache
from config import CACHE_FILE, MAX_COMMITS
from graph.state import ProjectState
from models.schemas import ProjectSignals

log = logging.getLogger(__name__)


def file_scanner(state: ProjectState) -> ProjectState:
    """
    Stage 1: pure Python extraction.
    Calls all extractors, checks cache, and populates state['raw_signals'] + state['content_hash'].
    Sets state['cache_hit'] = True and state['summary'] if a valid cache entry exists.
    """
    project_path = Path(state["project_path"])
    project_name = project_path.name

    content_hash = compute_project_hash(project_path)

    cache = load_cache(CACHE_FILE)
    cached = get_cached_summary(cache, project_name, content_hash)
    if cached:
        log.info("[2/5] file_scanner | %-30s CACHE HIT — skipping extraction", project_name)
        return {
            **state,
            "project_name": project_name,
            "content_hash": content_hash,
            "cache_hit": True,
            "summary": cached,
            "raw_signals": None,
            "compressed_payload": "",
        }

    log.info("[2/5] file_scanner | %-30s extracting signals ...", project_name)

    log.info("              ↳ extracting AST signals")
    ast_signals = extract_ast_signals(project_path)

    log.info("              ↳ extracting dependencies (LLM-assisted)")
    log.info("              ↳ extracting dir structure & file extensions")
    log.info("              ↳ extracting README")
    log.info("              ↳ reading git log")

    signals = ProjectSignals(
        name=project_name,
        deps=extract_deps(project_path),
        imports_used=ast_signals["imports_used"],
        classes=ast_signals["classes"],
        functions=ast_signals["functions"],
        decorators=ast_signals["decorators"],
        dir_structure=extract_dir_structure(project_path),
        file_extensions=extract_file_extensions(project_path),
        readme_excerpt=extract_readme(project_path),
        recent_commits=_get_recent_commits(project_path),
    )
    log.info("              ↳ done | deps=%d  imports=%d  classes=%d  commits=%d",
             len(signals.deps), len(signals.imports_used), len(signals.classes), len(signals.recent_commits))
    log.debug("              ↳ deps:    %s", signals.deps)
    log.debug("              ↳ imports: %s", signals.imports_used)

    return {
        **state,
        "project_name": project_name,
        "content_hash": content_hash,
        "cache_hit": False,
        "raw_signals": signals,
        "summary": None,
        "compressed_payload": "",
    }


def _get_recent_commits(project_path: Path) -> list[str]:
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", f"-{MAX_COMMITS}"],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return [line.split(" ", 1)[-1] for line in result.stdout.strip().splitlines() if line]
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return []
