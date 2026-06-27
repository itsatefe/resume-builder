import logging
from pathlib import Path
from graph.state import PipelineState

log = logging.getLogger(__name__)


def report_generator(state: PipelineState) -> PipelineState:
    """Write report_md to report.md and print it to terminal."""
    log.info("[5/5] report_generator | writing report.md ...")
    report_md = state["report_md"]
    output_path = Path(__file__).parents[2] / "report.md"
    output_path.write_text(report_md, encoding="utf-8")
    log.info("              ↳ saved to %s", output_path)
    log.info("=" * 60)
    print(report_md)
    return state