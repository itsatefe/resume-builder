import logging
from pathlib import Path
from graph.state import PipelineState

log = logging.getLogger(__name__)


def projects_lister(state: PipelineState) -> PipelineState:
    """List project directories under projects_root, filtered by include_projects if provided."""
    root = Path(state["projects_root"])
    include = set(state.get("include_projects", []))

    project_paths = [
        str(p) for p in root.iterdir()
        if p.is_dir() and (not include or p.name in include)
    ]

    names = [Path(p).name for p in project_paths]
    log.info("[1/5] projects_lister | found %d project(s): %s", len(names), names)
    return {**state, "project_paths": project_paths}