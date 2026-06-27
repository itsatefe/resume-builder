import json
import logging
from langchain_google_vertexai import ChatVertexAI
from config import GOOGLE_PROJECT_ID, GOOGLE_LOCATION, GEMINI_MODEL
from graph.state import PipelineState
from models.schemas import JDRequirements

log = logging.getLogger(__name__)


def jd_parser(state: PipelineState) -> PipelineState:
    """
    Send jd_text to Gemini Flash and extract structured JDRequirements.
    Populates state['jd_requirements'].
    """
    log.info("[3/5] jd_parser | parsing job description (%d chars) ...", len(state["jd_text"]))
    llm = ChatVertexAI(model=GEMINI_MODEL, project=GOOGLE_PROJECT_ID, location=GOOGLE_LOCATION)

    prompt = f"""Extract the technical requirements from this job description.

Job Description:
{state["jd_text"]}

Return JSON only:
{{
  "hard_skills": [str],
  "domain_knowledge": [str],
  "tools_and_frameworks": [str]
}}

hard_skills: programming languages, core engineering skills (e.g. "Python", "REST API design", "SQL").
domain_knowledge: subject areas and concepts required (e.g. "RAG", "LLM fine-tuning", "data pipelines").
tools_and_frameworks: specific libraries, platforms, or tools named (e.g. "FastAPI", "LangChain", "Kafka", "Docker").

Be specific and concise. Do not include soft skills or non-technical requirements."""

    response = llm.invoke(prompt)
    raw = response.content.strip().removeprefix("```json").removesuffix("```").strip()
    data = json.loads(raw)

    reqs = JDRequirements(**data)
    log.info("              ↳ done | hard_skills=%d  domain=%d  tools=%d",
             len(reqs.hard_skills), len(reqs.domain_knowledge), len(reqs.tools_and_frameworks))
    return {**state, "jd_requirements": reqs}
