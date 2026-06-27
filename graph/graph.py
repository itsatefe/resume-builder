import logging
from pathlib import Path
from langgraph.graph import StateGraph, END
from graph.state import PipelineState, ProjectState
from graph.nodes.projects_lister import projects_lister
from graph.nodes.file_scanner import file_scanner
from graph.nodes.signal_compressor import signal_compressor
from graph.nodes.gemini_summarizer import gemini_summarizer
from graph.nodes.jd_parser import jd_parser
from graph.nodes.matcher import matcher
from graph.nodes.report_generator import report_generator

log = logging.getLogger(__name__)


def process_all_projects(state: PipelineState) -> PipelineState:
    """Iterate over all project paths and run the per-project pipeline for each."""
    summaries = []

    total = len(state["project_paths"])
    for idx, project_path in enumerate(state["project_paths"], 1):
        log.info("--- project %d/%d: %s ---", idx, total, Path(project_path).name)
        project_state: ProjectState = {
            "project_name": "",
            "project_path": project_path,
            "content_hash": "",
            "cache_hit": False,
            "raw_signals": None,
            "compressed_payload": "",
            "summary": None,
        }

        project_state = file_scanner(project_state)

        if not project_state["cache_hit"]:
            project_state = signal_compressor(project_state)
            project_state = gemini_summarizer(project_state)

        if project_state["summary"]:
            summaries.append(project_state["summary"])

    return {**state, "summaries": summaries}


def build_pipeline_graph():
    """
    Assemble the top-level LangGraph pipeline:
      projects_lister → process_all_projects → jd_parser → matcher → report_generator
    """
    graph = StateGraph(PipelineState)

    graph.add_node("projects_lister", projects_lister)
    graph.add_node("process_all_projects", process_all_projects)
    graph.add_node("jd_parser", jd_parser)
    graph.add_node("matcher", matcher)
    graph.add_node("report_generator", report_generator)

    graph.set_entry_point("projects_lister")
    graph.add_edge("projects_lister", "process_all_projects")
    graph.add_edge("process_all_projects", "jd_parser")
    graph.add_edge("jd_parser", "matcher")
    graph.add_edge("matcher", "report_generator")
    graph.add_edge("report_generator", END)

    return graph.compile()
