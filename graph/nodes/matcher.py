import json
import logging
from graph.state import PipelineState
from models.schemas import MatchReport, MatchResult

log = logging.getLogger(__name__)


def matcher(state: PipelineState) -> PipelineState:
    """
    Gemini-powered semantic matching between jd_requirements and project summaries.
    Returns both structured MatchReport and a ready-to-save markdown report in one call.
    """
    from langchain_google_vertexai import ChatVertexAI
    from config import GOOGLE_PROJECT_ID, GOOGLE_LOCATION, GEMINI_MODEL

    log.info("[4/5] matcher | matching %d requirement(s) against %d project(s) ...",
             len(state["jd_requirements"].hard_skills) +
             len(state["jd_requirements"].domain_knowledge) +
             len(state["jd_requirements"].tools_and_frameworks),
             len(state["summaries"]))
    llm = ChatVertexAI(model=GEMINI_MODEL, project=GOOGLE_PROJECT_ID, location=GOOGLE_LOCATION)

    jd_req = state["jd_requirements"]
    summaries = state["summaries"]

    all_requirements = jd_req.hard_skills + jd_req.domain_knowledge + jd_req.tools_and_frameworks

    projects_block = "\n\n".join(
        f"Project: {s.name}\n"
        f"Domain: {s.domain}\n"
        f"Tech stack: {', '.join(s.tech_stack)}\n"
        f"Patterns: {', '.join(s.patterns)}\n"
        f"Key features: {', '.join(s.key_features)}"
        for s in summaries
    )

    prompt = f"""You are matching job description requirements against a candidate's local projects.

JD Requirements:
{chr(10).join(f'- {r}' for r in all_requirements)}

Candidate Projects:
{projects_block}

For each requirement, identify which projects provide evidence — including semantic matches
(e.g. "FAISS" satisfies "vector database", "Celery" satisfies "async task queue").

Return JSON only with this exact structure:
{{
  "matched": [
    {{"requirement": str, "matched_projects": [str], "evidence": str}},
    ...
  ],
  "unmatched": [str],
  "top_projects": [str],
  "report_md": str
}}

top_projects: ranked by how many requirements they satisfy.
report_md: a clean markdown report with a summary section, a matched requirements table
(columns: Requirement | Projects | Evidence), an unmatched requirements list,
and a top projects ranking."""

    response = llm.invoke(prompt)
    raw = response.content.strip().removeprefix("```json").removesuffix("```").strip()
    data = json.loads(raw)

    report = MatchReport(
        matched=[MatchResult(**m) for m in data["matched"]],
        unmatched=data["unmatched"],
        top_projects=data["top_projects"],
    )

    log.info("              ↳ done | matched=%d  unmatched=%d  top=%s",
             len(report.matched), len(report.unmatched), report.top_projects[:3])
    return {**state, "report": report, "report_md": data["report_md"]}