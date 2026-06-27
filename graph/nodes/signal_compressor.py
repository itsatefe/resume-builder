import logging
from graph.state import ProjectState

log = logging.getLogger(__name__)


def signal_compressor(state: ProjectState) -> ProjectState:
    """
    Format raw_signals into a readable string payload for the Gemini prompt.
    Drops empty fields only. Populates state['compressed_payload'].
    """
    signals = state["raw_signals"]
    lines = []

    if signals.deps:
        lines.append(f"Dependencies: {', '.join(signals.deps)}")
    if signals.imports_used:
        lines.append(f"Imports: {', '.join(signals.imports_used)}")
    if signals.classes:
        lines.append(f"Classes: {', '.join(signals.classes)}")
    if signals.functions:
        lines.append(f"Functions: {', '.join(signals.functions)}")
    if signals.decorators:
        lines.append(f"Decorators: {', '.join(signals.decorators)}")
    if signals.dir_structure:
        lines.append(f"Structure: {', '.join(signals.dir_structure)}")
    if signals.file_extensions:
        ext_str = ", ".join(f"{k}:{v}" for k, v in signals.file_extensions.items())
        lines.append(f"File types: {ext_str}")
    if signals.readme_excerpt:
        lines.append(f"README: {signals.readme_excerpt}")
    if signals.recent_commits:
        lines.append(f"Recent commits: {', '.join(signals.recent_commits)}")

    payload = "\n".join(lines)
    log.info("[3/5] signal_compressor | %-30s payload ready (%d chars)", state["project_name"], len(payload))
    log.debug("[3/5] signal_compressor | %-30s full payload:\n%s", state["project_name"], payload)
    return {**state, "compressed_payload": payload}