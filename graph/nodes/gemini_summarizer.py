import logging
from langchain_google_vertexai import ChatVertexAI
from cache.project_cache import load_cache, save_cache, set_cached_summary
from config import CACHE_FILE, GOOGLE_PROJECT_ID, GOOGLE_LOCATION, GEMINI_MODEL
from graph.state import ProjectState
from models.schemas import ProjectSummary

log = logging.getLogger(__name__)


def gemini_summarizer(state: ProjectState) -> ProjectState:
    """
    Send compressed_payload to Gemini Flash and parse response into ProjectSummary.
    Skips the LLM call if file_scanner already found a cache hit.
    Writes the new summary to cache after a successful call.
    """
    if state["cache_hit"]:
        return state

    log.info("[4/5] gemini_summarizer | %-30s calling Gemini ...", state["project_name"])
    llm = ChatVertexAI(model=GEMINI_MODEL, project=GOOGLE_PROJECT_ID, location=GOOGLE_LOCATION)
    llm_structured = llm.with_structured_output(ProjectSummary)

    prompt = f"""You are extracting project capabilities for resume matching.
Project: {state["project_name"]}
---
{state["compressed_payload"]}
---
domain: one short phrase describing what this project does (e.g. "RAG pipeline", "admin dashboard").
tech_stack: languages, frameworks, libraries actually used.
patterns: architectural or design patterns observed (e.g. "REST API", "event-driven", "agent tool use").
key_features: concrete capabilities built (e.g. "document ingestion", "semantic search", "streaming chat")."""

    summary: ProjectSummary = llm_structured.invoke(prompt)
    summary = summary.model_copy(update={"name": state["project_name"]})

    cache = load_cache(CACHE_FILE)
    set_cached_summary(cache, state["project_name"], state["content_hash"], summary)
    save_cache(CACHE_FILE, cache)

    log.info("              ↳ done | domain=%s  tech_stack=%s", summary.domain, summary.tech_stack)
    return {**state, "summary": summary}
