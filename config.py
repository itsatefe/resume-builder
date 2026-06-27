from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

GOOGLE_PROJECT_ID: str = os.getenv("GOOGLE_PROJECT_ID", "")
GOOGLE_LOCATION: str = os.getenv("GOOGLE_LOCATION", "us-central1")
GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
PROJECTS_ROOT: Path = Path(os.getenv("PROJECTS_ROOT", Path(__file__).parent.parent))
THIS_PROJECT: str = Path(__file__).parent.name
CACHE_FILE: Path = Path(__file__).parent / ".project_cache.json"
SCAN_DEPTH: int = 2
MAX_README_CHARS: int = 500
MAX_COMMITS: int = 20
