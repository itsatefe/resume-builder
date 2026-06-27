from typing import TypedDict
from models.schemas import ProjectSignals, ProjectSummary, JDRequirements, MatchReport


class ProjectState(TypedDict):
    """State for the per-project subgraph."""
    project_name: str
    project_path: str
    content_hash: str
    cache_hit: bool
    raw_signals: ProjectSignals | None
    compressed_payload: str
    summary: ProjectSummary | None


class PipelineState(TypedDict):
    """Top-level state for the full pipeline graph."""
    projects_root: str
    jd_text: str
    include_projects: list[str]   # if non-empty, only these project names are scanned
    project_paths: list[str]
    summaries: list[ProjectSummary]
    jd_requirements: JDRequirements | None
    report: MatchReport | None
    report_md: str