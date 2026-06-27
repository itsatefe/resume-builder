# resume-builder

Scans a folder of local projects, matches them against a job description using Gemini, and generates a tailored resume `.docx`. Projects linked to a work experience are woven into that role's bullets; unaffiliated projects appear in a standalone Projects section.

## Pipeline

```
projects_lister
  └── process_all_projects (per project):
        file_scanner → signal_compressor → gemini_summarizer
  └── jd_parser
  └── matcher
  └── report_generator  →  report.md
  └── resume_generator  →  resume.docx
```

### What each stage does

| Stage | What it does |
|---|---|
| `file_scanner` | Extracts AST signals (imports, classes, functions, decorators), dependencies via LLM, directory structure, file extensions, README, and git log. Checks cache — skips LLM if unchanged. |
| `signal_compressor` | Formats raw signals into a text payload for the summarizer. |
| `gemini_summarizer` | Calls Gemini to produce a structured `ProjectSummary` (domain, tech stack, patterns, key features). |
| `jd_parser` | Calls Gemini to extract structured requirements from the JD (hard skills, domain knowledge, tools). |
| `matcher` | Semantically matches JD requirements against project summaries, including indirect matches (e.g. `mcp` → "Model Context Protocol"). Produces a ranked markdown report. |
| `report_generator` | Writes `report.md`. |
| `resume_generator` | Calls Gemini to produce a tailored resume, then writes `resume.docx`. Projects linked to a role in `profile.yaml` are merged into that role's experience bullets. |

All LLM outputs use `with_structured_output()` backed by Pydantic models — no manual JSON parsing.

## Setup

```bash
pip install -r requirements.txt
# or, much faster:
pip install uv && uv pip install -r requirements.txt
```

Create a `.env` file:

```
GOOGLE_PROJECT_ID=your-gcp-project
GOOGLE_LOCATION=us-central1        # optional, default: us-central1
GEMINI_MODEL=gemini-2.5-flash      # optional
PROJECTS_ROOT=/path/to/your/projects
```

Authenticate with Google Cloud:

```bash
gcloud auth application-default login
```

## Usage

```bash
# Match all projects against a JD and generate resume
python main.py JD/1.txt

# Match specific projects only
python main.py JD/1.txt --projects cat-ai-proc-agent rag-chatbot

# Clear the project summary cache
python main.py --clear-cache

# Show full payloads sent to Gemini (for debugging)
python main.py --debug JD/1.txt
```

## Outputs

| File | Description |
|---|---|
| `report.md` | Matched / unmatched requirements table, evidence, top projects ranking |
| `resume.docx` | Tailored resume — summary, skills, experience with project highlights embedded, standalone projects |

## Profile configuration (`profile.yaml`)

Defines personal info, background, work experience, and education. Link local projects to the role they were built during using the `projects:` field — they will be woven into that role's resume bullets instead of appearing as separate projects.

```yaml
experience:
  - title: Applied AI Engineer
    company: Mithra-AI Solutions
    period: "Mar 2026 – Present"
    projects:
      - cat-ai-proc-agent        # this project's highlights go under this role
    bullets:
      - ...
```

Projects not listed under any role appear in the standalone Projects section of the resume.

## Caching

Project summaries are cached in `.project_cache.json` by an MD5 hash of all `.py` files (recursive), README, and dependency files. Unchanged projects skip all LLM calls on subsequent runs. Run `--clear-cache` to force a full re-scan.
