import hashlib
import json
import re
import shutil
import subprocess
import unicodedata
from datetime import datetime
from pathlib import Path

from .config import (
    ANCHOR_INSTITUTIONS,
    ARCHIVE_DIR,
    COURSES_DIR,
    OUTPUT_DIR,
    RELATIONAL_MATRIX_FILE,
    SEQUENTIAL_RE,
    VAULT_DIRS,
    VIDEO_EXTENSIONS,
)
from .data import (
    load_courses_registry,
    load_json,
    load_known_persons,
    load_profile,
    load_registry,
    save_json,
    save_courses_registry,
)


# --- UTILITIES ---

def run_ai_cmd(command_str: str) -> str:
    result = subprocess.run(command_str, shell=True, capture_output=True, text=True)
    return result.stdout.strip()


def file_hash(path: Path) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def get_safe_year(date_str: str) -> str:
    if not date_str or date_str in ("0000-00-00", "N/A"):
        return ""
    s = str(date_str)
    for pattern in [r"(\d{4})-\d{2}-\d{2}", r"\d{1,2}[\.\-/]\d{1,2}[\.\-/](\d{4})", r"(\d{4})"]:
        m = re.search(pattern, s)
        if m:
            return m.group(1)
    return ""


def slugify(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"dr\.?\s+", "", text.lower()).strip()
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def make_symlink(target: Path, link: Path):
    link.parent.mkdir(parents=True, exist_ok=True)
    if link.exists() or link.is_symlink():
        link.unlink()
    link.symlink_to(target.resolve())


def extract_json(text: str) -> dict | None:
    try:
        m = re.search(r"(\{.*\})", text, re.DOTALL)
        return json.loads(m.group(1)) if m else json.loads(text)
    except Exception:
        return None


def normalize_text(text: str) -> str:
    if not text:
        return ""
    return unicodedata.normalize("NFC", text)


# --- INTELLIGENCE MODULES ---

class EnvironmentalIntelligence:
    @staticmethod
    def get_context(file_path: Path) -> dict:
        parents = [p.name for p in file_path.parents if p.name not in (".", "..", "inbox", "samples")]
        filename_words = re.findall(r"[a-zA-Z]{3,}", file_path.stem)
        return {"source_folders": parents, "filename_hints": filename_words}


class RelationalMatrix:
    def __init__(self):
        self.matrix = load_json(RELATIONAL_MATRIX_FILE, {})

    def get_person_context(self, person_key: str) -> dict:
        return self.matrix.get(person_key, {
            "institutions": [], "domains": [], "keywords": [], "aliases": [], "assets": []
        })

    def update_matrix(self, person_key: str, institutions: list, domains: list,
                      keywords: list, alias=None, assets=None):
        if person_key not in self.matrix:
            self.matrix[person_key] = {
                "institutions": [], "domains": [], "keywords": [], "aliases": [], "assets": []
            }
        p = self.matrix[person_key]
        p["institutions"] = list(set(p.get("institutions", []) + [i for i in institutions if i]))
        p["domains"]      = list(set(p.get("domains", []) + domains))
        p["keywords"]     = list(set(p.get("keywords", []) + [k for k in keywords if k]))
        if alias and alias not in p.get("aliases", []):
            p.setdefault("aliases", []).append(alias)
        if assets:
            p["assets"] = list(set(p.get("assets", []) + assets))
        save_json(RELATIONAL_MATRIX_FILE, self.matrix)


# --- FILING ENGINE ---

def build_final_name(data: dict, prefix: str, file_path: Path, vehicle_no: str = "") -> str:
    raw_date = data.get("date") or (data.get("metadata") or {}).get("date") or ""
    year = get_safe_year(raw_date)

    raw_tag = slugify(data.get("naming_tag") or data.get("action_type") or "document")
    seen: set = set()
    name_tag = "-".join(x for x in raw_tag.split("-") if not (x in seen or seen.add(x)))  # type: ignore

    sig_entity = ""
    if data.get("include_location"):
        inst = slugify(data.get("location") or "")
        if inst in {slugify(a) for a in ANCHOR_INSTITUTIONS}:
            sig_entity = inst

    main_parts = [name_tag, year, sig_entity]
    if "list_details" in data:
        ld = data["list_details"]
        main_parts.append(f"p{ld['page']}-s{ld['sno']}")
    if vehicle_no:
        main_parts.append(vehicle_no)

    content_str = "-".join(p for p in main_parts if p)
    return f"{prefix}_{content_str}{file_path.suffix}"


def file_document(data: dict, file_path: Path, final_name: str,
                  person_key: str, subject_display: str) -> str | None:
    """Copy to archive and create vault + index symlinks. Returns final name, or None if exact duplicate."""
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    dest = ARCHIVE_DIR / final_name

    if dest.exists():
        if file_hash(file_path) == file_hash(dest):
            return None
        ts = datetime.now().strftime("%Y%m%d%H%M%S")
        stem, ext = final_name.rsplit(".", 1)
        final_name = f"{stem}_{ts}.{ext}"
        dest = ARCHIVE_DIR / final_name

    shutil.copy2(file_path, dest)

    vault_type = data.get("vault_type") or "KnowledgeBase"
    vault_base = VAULT_DIRS.get(vault_type, VAULT_DIRS["KnowledgeBase"])
    if vault_type == "KnowledgeBase":
        doc_type = slugify(data.get("action_type") or "general")
        vault_dir = vault_base / doc_type
    else:
        vault_dir = vault_base / person_key
    make_symlink(dest, vault_dir / final_name)

    year = get_safe_year(data.get("date") or (data.get("metadata") or {}).get("date") or "")
    idx = OUTPUT_DIR / "indices"
    make_symlink(dest, idx / "by_person" / person_key / final_name)
    make_symlink(dest, idx / "by_vault"  / vault_type  / final_name)
    if year:
        make_symlink(dest, idx / "by_timeline" / year / final_name)

    return final_name


# --- PERSON PROFILE ---

def build_person_profile(person_key: str) -> dict:
    """Aggregate all known data for a person for use in form filling."""
    known = load_known_persons()
    matrix = RelationalMatrix()
    registry = load_registry()
    stored_profile = load_profile(person_key)

    person = known.get(person_key, {})
    context = matrix.get_person_context(person_key)

    # Pull structured facts from registry entries
    locations: list[str] = []
    action_types: set[str] = set()
    dates: list[str] = []
    excerpts: list[str] = []
    for entry in registry:
        if entry.get("person_key") != person_key:
            continue
        if entry.get("location"):
            locations.append(entry["location"])
        if entry.get("action_type"):
            action_types.add(entry["action_type"])
        if entry.get("date"):
            dates.append(entry["date"])
        if entry.get("ocr_excerpt"):
            tag = entry.get("naming_tag", "doc")
            excerpts.append(f"[{tag} {entry.get('date','')}]: {entry['ocr_excerpt'][:250]}")

    # Extract likely employee ID (RJCR… pattern) and vehicle from keywords
    employee_id = next(
        (k for k in context.get("keywords", []) if re.match(r"RJCR\d{12}", k)), ""
    )
    vehicle_no = next(
        (a for a in context.get("assets", []) if re.match(r"[A-Z]{2}\d{2}", a)), ""
    )

    return {
        "key": person_key,
        "name": person.get("name", person_key.replace("_", " ").title()),
        "prefix": person.get("prefix", ""),
        "institutions": [i for i in context.get("institutions", []) if i],
        "assets": context.get("assets", []),
        "keywords": context.get("keywords", []),
        "employee_id": employee_id,
        "vehicle_no": vehicle_no,
        "known_locations": list(dict.fromkeys(locations)),   # deduplicated, order preserved
        "known_action_types": sorted(action_types),
        "known_dates": sorted(set(dates)),
        "profile": stored_profile,
        "document_excerpts": excerpts[:10],
    }


# --- COURSE DETECTION ---

def _course_signals(path: Path) -> dict:
    videos = pdfs = sequential = total = 0
    for f in path.iterdir():
        if not f.is_file():
            continue
        total += 1
        ext = f.suffix.lower()
        if ext in VIDEO_EXTENSIONS:
            videos += 1
        elif ext == ".pdf":
            pdfs += 1
        if SEQUENTIAL_RE.match(f.stem):
            sequential += 1
    return {"videos": videos, "pdfs": pdfs, "sequential": sequential, "total": total}


def _is_course_folder(path: Path) -> tuple[bool, str, dict]:
    sig = _course_signals(path)
    if sig["total"] < 5:
        return False, "", sig
    has_video = sig["videos"] >= 3
    has_seq = sig["sequential"] >= 5 and sig["sequential"] / sig["total"] >= 0.40
    if not has_video and not has_seq:
        return False, "", sig
    if has_video and sig["pdfs"] > 0:
        kind = "mixed"
    elif has_video:
        kind = "video-only"
    else:
        kind = "pdf-only"
    return True, kind, sig


def _move_course(folder: Path, kind: str) -> Path:
    COURSES_DIR.mkdir(parents=True, exist_ok=True)
    dest = COURSES_DIR / folder.name
    if dest.exists():
        ts = datetime.now().strftime("%Y%m%d%H%M%S")
        dest = COURSES_DIR / f"{folder.name}_{ts}"
    shutil.move(str(folder), dest)
    registry = load_courses_registry()
    registry.append({
        "folder":   folder.name,
        "kind":     kind,
        "moved_to": str(dest),
        "moved_at": datetime.now().isoformat(),
    })
    save_courses_registry(registry)
    return dest
