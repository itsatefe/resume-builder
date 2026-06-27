# resume-builder

Scans a folder of local projects and matches them against a job description using Gemini. Outputs a ranked markdown report showing which projects satisfy which requirements.

## How it works

```
projects_lister → process_all_projects → jd_parser → matcher → report_generator
```

For each project: extracts AST signals, dependencies, README, directory structure, and git log — then calls Gemini to summarize the project. After all projects are processed, Gemini parses the JD and semantically matches requirements against summaries (e.g. "FAISS" satisfies "vector database").

Results are written to `report.md`.

## Setup

```bash
pip install -r requirements.txt
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
# Match all projects against a JD
python main.py path/to/jd.txt

# Match specific projects only
python main.py path/to/jd.txt --projects my-api rag-chatbot
```

## Caching

Project summaries are cached in `.project_cache.json` by an MD5 hash of the project's key files. Unchanged projects skip all LLM calls on subsequent runs.
