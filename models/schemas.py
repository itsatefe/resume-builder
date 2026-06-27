from pydantic import BaseModel


class ProjectSignals(BaseModel):
    """Raw signals extracted from a project by Stage 1 (pure Python, no LLM)."""
    name: str
    deps: list[str]
    imports_used: list[str]
    classes: list[str]
    functions: list[str]
    decorators: list[str]
    dir_structure: list[str]
    file_extensions: dict[str, int]
    readme_excerpt: str
    recent_commits: list[str]


class ProjectSummary(BaseModel):
    """Interpreted summary produced by Gemini from ProjectSignals."""
    name: str
    domain: str
    tech_stack: list[str]
    patterns: list[str]
    key_features: list[str]


class JDRequirements(BaseModel):
    """Structured requirements extracted from a job description."""
    hard_skills: list[str]
    domain_knowledge: list[str]
    tools_and_frameworks: list[str]


class MatchResult(BaseModel):
    """Single matched requirement with supporting evidence."""
    requirement: str
    matched_projects: list[str]
    evidence: str


class MatchReport(BaseModel):
    """Final cross-check report."""
    matched: list[MatchResult]
    unmatched: list[str]
    top_projects: list[str]


class ResumeProject(BaseModel):
    """LLM-generated project entry for the resume."""
    name: str
    bullets: list[str]


class ResumeExperience(BaseModel):
    """LLM-refined experience entry for the resume."""
    title: str
    company: str
    period: str
    bullets: list[str]


class ResumeContent(BaseModel):
    """LLM-generated resume body, tailored to the JD."""
    summary: str
    skills: dict[str, list[str]]
    projects: list[ResumeProject]
    experience: list[ResumeExperience]