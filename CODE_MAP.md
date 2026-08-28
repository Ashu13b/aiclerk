<!-- context-kit CODE_MAP · v0.1.0 · generated 2026-08-07 11:46 UTC · sha 9f903c3 · host vnic-trading -->

# CODE_MAP

Symbol index (skim-grade). Consult before Grep/Read.

## Composition
- Python — 6 files · 71 symbols
- TypeScript — 13 files · 50 symbols
- JavaScript — 3 files · 36 symbols
- HTML — 1 file (unindexed)
_Total: 23 files · 157 symbols across 4 languages._


## Compartments
- `auto` — dynamic (git files in play + 2-hop import neighborhood)

Run `ck compartment <name>` to load a compartment's warm symbol index.

### ./
- `mass_ingest.py` — REINGEST_DIR, files, def run_ingest
### aiclerk/
- `aiclerk/__init__.py` — __version__
- `aiclerk/cli.py` — def cli, def ingest, def review, def correct, def timeline, def list_vault, def gaps, def clean, def auto, def courses, def sync, def fill, _PROFILE_QUESTIONS, def profile, def repl
- `aiclerk/config.py` — CONFIG_DIR, KNOWN_PERSONS_FILE, RELATIONAL_MATRIX_FILE, REVIEW_QUEUE_FILE, FORM_CODES_FILE, COURSES_REGISTRY_FILE, _PACKAGE_DIR, _PROJECT_DIR, OUTPUT_DIR, INBOX_DIR, REGISTRY_FILE, ARCHIVE_DIR, VAULT_DIRS, COURSES_DIR, FILL_REPORTS_DIR, PROFILES_DIR, CONFIDENCE_THRESHOLD, VIDEO_EXTENSIONS, SEQUENTIAL_RE, USER_NAME, ANCHOR_INSTITUTIONS
- `aiclerk/core.py` — def run_ai_cmd, def file_hash, def get_safe_year, def slugify, def make_symlink, def extract_json, def normalize_text, class EnvironmentalIntelligence(get_context), class RelationalMatrix(__init__, get_person_context, update_matrix), def build_final_name, def file_document, def build_person_profile, def _course_signals, def _is_course_folder, def _move_course
- `aiclerk/data.py` — def load_json, def save_json, def load_known_persons, def save_known_persons, def load_registry, def append_registry_entry, def load_review_queue, def save_review_queue, def add_to_review_queue, def load_form_codes, def save_form_codes, def load_relational_matrix, def load_courses_registry, def save_courses_registry, def load_profile, def save_profile
### app/
- `app/App.tsx` — Screen, App, renderScreen
- `app/components/BottomNav.tsx` — Screen, Props, BottomNav
- `app/components/ProgressRing.tsx` — Props, ProgressRing
- `app/components/Tag.tsx` — Props, Tag
- `app/components/XPBar.tsx` — Props, XPBar
- `app/data.ts` — VaultType, Document, Person, Proposal, FillSource, FillField, FillReport
- `app/design/ios-frame.jsx` — IOSStatusBar, IOSGlassPill, IOSNavBar, pillIcon, IOSListRow, IOSList, IOSDevice, IOSKeyboard, key, row
- `app/design/tweaks-panel.jsx` — useTweaks, TweaksPanel, onMsg, dismiss, onDragStart, move, up, TweakSection, TweakRow, TweakSlider, TweakToggle, TweakRadio, segAt, onPointerDown, move, up, TweakSelect, TweakText, TweakNumber, clamp, onScrubStart, decimals, move, up, TweakColor, TweakButton
- `app/screens/DashboardScreen.tsx` — Props, DashboardScreen, StatCard
- `app/screens/FillScreen.tsx` — Props, FillScreen, commitEdit, startEdit, cancelEdit, StatBadge, Section, FieldRowProps, FieldRow
- `app/screens/InboxScreen.tsx` — Props, InboxScreen, approve, ProposalCard, DetailRow
- `app/screens/SearchScreen.tsx` — Props, SearchScreen, handleSearch, clickSuggestion, DetailRow
- `app/screens/SettingsScreen.tsx` — Props, SettingsScreen, triggerReindex, triggerClean, StatRow, ConfigRow, PathRow
- `app/theme.ts` — Theme, getTheme
