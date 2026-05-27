import json
from pathlib import Path

from .config import (
    COURSES_REGISTRY_FILE,
    FORM_CODES_FILE,
    KNOWN_PERSONS_FILE,
    PROFILES_DIR,
    REGISTRY_FILE,
    RELATIONAL_MATRIX_FILE,
    REVIEW_QUEUE_FILE,
)


def load_json(path: Path, default):
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(default, f, indent=2)
        return default
    with open(path) as f:
        return json.load(f)


def save_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_known_persons() -> dict:
    initial = {
        "ASHISH_YADAV":     {"prefix": "ash",  "tier": 1, "name": "Dr. Ashish Yadav"},
        "SANJEEV_KALER":    {"prefix": "sanj", "tier": 4, "name": "Sanjeev Kaler"},
        "JITENDRA_PATAWAT": {"prefix": "jit",  "tier": 4, "name": "Jitendra Patawat"},
    }
    data = load_json(KNOWN_PERSONS_FILE, initial)
    dirty = False
    for key, pdata in data.items():
        if not pdata.get("name"):
            pdata["name"] = key.replace("_", " ").title()
            dirty = True
    if dirty:
        save_json(KNOWN_PERSONS_FILE, data)
    return data


def save_known_persons(data: dict):
    save_json(KNOWN_PERSONS_FILE, data)


def load_registry() -> list:
    return load_json(REGISTRY_FILE, [])


def append_registry_entry(entry: dict):
    registry = [r for r in load_registry() if r.get("filed_as") != entry["filed_as"]]
    registry.append(entry)
    save_json(REGISTRY_FILE, registry)


def load_review_queue() -> list:
    return load_json(REVIEW_QUEUE_FILE, [])


def save_review_queue(queue: list):
    save_json(REVIEW_QUEUE_FILE, queue)


def add_to_review_queue(entry: dict):
    queue = load_review_queue()
    queue.append(entry)
    save_review_queue(queue)


def load_form_codes() -> dict:
    return load_json(FORM_CODES_FILE, {})


def save_form_codes(data: dict):
    save_json(FORM_CODES_FILE, data)


def load_relational_matrix() -> dict:
    return load_json(RELATIONAL_MATRIX_FILE, {})


def load_courses_registry() -> list:
    return load_json(COURSES_REGISTRY_FILE, [])


def save_courses_registry(data: list):
    save_json(COURSES_REGISTRY_FILE, data)


def load_profile(person_key: str) -> dict:
    path = PROFILES_DIR / f"{person_key}.json"
    return load_json(path, {})


def save_profile(person_key: str, data: dict):
    PROFILES_DIR.mkdir(parents=True, exist_ok=True)
    save_json(PROFILES_DIR / f"{person_key}.json", data)
