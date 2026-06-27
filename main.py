import argparse
import logging
from pathlib import Path
from logger import setup_logging
from graph.graph import build_pipeline_graph
from config import PROJECTS_ROOT, CACHE_FILE

log = logging.getLogger(__name__)


def main():
    setup_logging()
    parser = argparse.ArgumentParser(description="Match local projects against a job description.")
    parser.add_argument("jd", type=Path, nargs="?", help="Path to job description text file")
    parser.add_argument(
        "--projects", "-p",
        nargs="+",
        metavar="NAME",
        help="Only scan these project names (e.g. --projects resume cat-ai-proc-agent)",
    )
    parser.add_argument(
        "--clear-cache",
        action="store_true",
        help="Delete the project summary cache and exit.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Set log level to DEBUG to show full payloads sent to Gemini.",
    )
    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    if args.clear_cache:
        if CACHE_FILE.exists():
            CACHE_FILE.unlink()
            log.info("Cache cleared: %s", CACHE_FILE)
        else:
            log.info("No cache file found at %s", CACHE_FILE)
        return

    if not args.jd:
        parser.error("the following arguments are required: jd")

    jd_text = args.jd.read_text(encoding="utf-8")
    log.info("Starting pipeline | JD: %s | Projects filter: %s", args.jd, args.projects or "all")

    graph = build_pipeline_graph()
    graph.invoke({
        "projects_root": str(PROJECTS_ROOT),
        "jd_text": jd_text,
        "include_projects": args.projects or [],
        "project_paths": [],
        "summaries": [],
        "jd_requirements": None,
        "report": None,
        "report_md": "",
        "resume_content": None,
        "resume_path": "",
    })


if __name__ == "__main__":
    main()