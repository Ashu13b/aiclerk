import re
from pathlib import Path

CONFIG_DIR = Path.home() / ".aiclerk"
KNOWN_PERSONS_FILE = CONFIG_DIR / "known_persons.json"
RELATIONAL_MATRIX_FILE = CONFIG_DIR / "relational_matrix.json"
REVIEW_QUEUE_FILE = CONFIG_DIR / "review_queue.json"
FORM_CODES_FILE = CONFIG_DIR / "form_codes.json"
COURSES_REGISTRY_FILE = CONFIG_DIR / "courses_registry.json"

_PACKAGE_DIR = Path(__file__).parent   # aiclerk/aiclerk/
_PROJECT_DIR = _PACKAGE_DIR.parent    # aiclerk/ (umbrella)

OUTPUT_DIR = _PROJECT_DIR / "output"
INBOX_DIR = _PROJECT_DIR / "inbox"
REGISTRY_FILE = OUTPUT_DIR / "v2_metadata_results.json"
ARCHIVE_DIR = OUTPUT_DIR / "archive"
VAULT_DIRS = {
    "ServiceRecord":      OUTPUT_DIR / "service_records",
    "ProfessionalOutput": OUTPUT_DIR / "professional_output",
    "KnowledgeBase":      OUTPUT_DIR / "insights",
}
COURSES_DIR = OUTPUT_DIR / "courses"
FILL_REPORTS_DIR = OUTPUT_DIR / "fill_reports"
PROFILES_DIR = CONFIG_DIR / "profiles"

CONFIDENCE_THRESHOLD = 0.70
VIDEO_EXTENSIONS = {".mp4", ".mkv", ".mov", ".avi", ".webm", ".m4v", ".wmv", ".flv"}
SEQUENTIAL_RE = re.compile(
    r"^(\d{1,3}[\s\-_.]+|"
    r"(lecture|chapter|module|session|week|lesson|part|unit|class)[\s\-_]?\d)",
    re.IGNORECASE,
)
USER_NAME = "Ashu"
ANCHOR_INSTITUTIONS = ["GMC Nagaur", "RajMES", "SDH Rajgarh", "RUHS", "JLN Hospital Nagaur"]
