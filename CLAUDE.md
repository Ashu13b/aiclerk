# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

AiClerk is a pip-installable intelligent document clerk. The Python package is at `aiclerk/aiclerk/`; install it once and the `aiclerk` command becomes available globally.

## Install

```bash
pip install -e . --break-system-packages
```

## Running aiclerk

```bash
aiclerk ingest path/to/doc.pdf          # interactive single-file ingest
aiclerk ingest path/to/doc.pdf --no-interactive  # queue low-confidence items, no prompts
aiclerk sync inbox/                      # reconcile inbox dir; only new files processed
aiclerk sync inbox/ --interval 60        # continuous watch loop (60s interval)
aiclerk auto inbox/                      # batch non-interactive; skips already-filed files
aiclerk review                           # interactive loop for low-confidence queue
aiclerk correct <filed_name>             # fix a registry entry's classification in-place
aiclerk fill <form.pdf> [--person ash]   # pre-fill a blank form from the person's profile
aiclerk profile [--person ash] [--reset] # interview to build a person's profile for filling
aiclerk timeline ash                     # chronological markdown service book for a person
aiclerk list [prefix]                    # vault status overview or per-person drill-down
aiclerk gaps ash                         # surface missing document types / year gaps
aiclerk clean                            # prune registry entries whose archive file is gone
aiclerk courses <dir> [--move]           # detect course folders; --move to relocate them
aiclerk /                                # enter interactive slash-command REPL
```

Dependencies: `click`, `pdftoppm` (poppler), `ai ocr` and `ai chat` from `aistack` (`../aistack/`).

## Package Layout

```
aiclerk/              # umbrella folder
  aiclerk/            # Python package (pip-installable)
    __init__.py       # version: 0.9.0
    config.py         # all constants, paths (Path(__file__)-based for portability)
    data.py           # JSON persistence layer
    core.py           # business logic: filing, naming, course detection, matrix
    cli.py            # Click CLI — thin orchestration layer
  app/                # Expo app (Android/iOS/Web)
  output/             # organized_docs equivalent (archive/, vault dirs, indices/)
  inbox/              # incoming documents
  pyproject.toml      # entry point: aiclerk = "aiclerk.cli:cli"
```

## Ingest Pipeline (inside `cli.py` `ingest` command)

1. **Glance OCR** — `pdftoppm` splits page 1 header/footer into temp JPEGs; `ai ocr` extracts text. Non-PDF images are OCR'd directly.
2. **Pre-inference priors** — Three signals override the AI before it runs: asset match (vehicle plate in OCR/filename → known owner), folder path name (parent folder matches a known person), filename match. Priors elevate confidence and inject definitive hints into the prompt.
3. **Deep Inference** — `ai chat` receives a structured prompt (priors + relational matrix context + OCR text). Returns JSON with all fields from `SCHEMA.json`.
4. **Person Discovery** — If a new person appears at scope ≤ 3, the clerk pauses and asks whether to track them. New entries go into `~/.docclerk/known_persons.json`.
5. **Relevance Intent** — For scope 1–2 documents, asks "why are you saving this?" and stores the answer in the registry entry.
6. **List Intelligence** — If `is_list: true`, OCRs page 1 at full resolution for preamble context; optionally asks for page/serial number to verify a specific person's entry.
7. **Filing** — Copies to `organized_docs/archive/`, creates vault symlink and index symlinks. Duplicate detection via MD5; timestamp suffix on same-name collision.
8. **Registry write-back** — Appends/replaces entry in `v2_metadata_results.json`.
9. **Relational Matrix update** — Adds institutions, domains, assets to `~/.docclerk/relational_matrix.json`.

## State Files

All mutable state lives in `~/.aiclerk/` (not in the repo).
- `known_persons.json` — dict keyed by `CANONICAL_KEY`, each entry: `{prefix, tier, name}`. Bootstrapped with Ashish/Sanjeev/Jitendra on first run.
- `relational_matrix.json` — per-person `{institutions, domains, keywords, aliases, assets}` for identity resolution.
- `review_queue.json` — list of low-confidence ingest items pending human review.
- `form_codes.json` — registry of learned government form designations (e.g. `"GA 55A"` → `{naming_tag, description}`).
- `courses_registry.json` — log of course folders that were relocated.
- `profiles/<CANONICAL_KEY>.json` — structured personal data collected by `aiclerk profile` for form auto-filling.

The canonical document registry is `output/v2_metadata_results.json` (list of objects).

## Output Layout

```
output/
  archive/                        # canonical store — physical files live here
  service_records/PERSON_KEY/     # symlinks: employment, benefits, career
  professional_output/PERSON_KEY/ # symlinks: work authored/signed by person
  insights/DOC_TYPE_SLUG/         # symlinks: KnowledgeBase (precedents, guidelines)
  courses/                        # relocated course folders (video/PDF sequences)
  fill_reports/                   # JSON reports from aiclerk fill; latest.json always updated
  indices/
    by_person/PERSON_KEY/
    by_vault/VAULT_TYPE/
    by_timeline/YEAR/
```

`indices/` and vault dirs contain only symlinks; physical files live once in `archive/`.

## Metadata Schema

Defined in `SCHEMA.json`. Key fields:

- `vault_type`: `"ServiceRecord"` | `"ProfessionalOutput"` | `"KnowledgeBase"`
- `scope`: 1=Self, 2=Family/Assets, 3=AnchorOrg, 4=General, 5=Unrelated
- `primary_subject`: full person name in English
- `naming_tag`: human-readable purpose slug (e.g. `paternity-leave`, `selection-list`) — never a form code
- `form_code`: official government form designation only (e.g. `"GA 55A"`, `"Form 16"`) — learned into `form_codes.json`
- `is_list`: `true` for multi-person tables → triggers interactive page/row verification
- `assets`: vehicle plates or other IDs found verbatim in the document (not echoed from relational matrix)
- `confidence`: 0.0–1.0; items below `CONFIDENCE_THRESHOLD = 0.70` go to review queue
- `relevance_intent`: user-stated reason for saving (scope 1–2 only)

## Naming Convention

`{prefix}_{naming_tag}-{year}-{location_slug}{list_suffix}.{ext}`

Person prefixes: `ash` = Ashish Yadav, `jit` = Jitendra Patawat, `sanj` = Sanjeev Kaler.

`slugify()` strips `dr.`, lowercases, and replaces non-alphanumeric with `-`.

## Satisficed Reading Strategy

For PDFs, only the page-1 header strip and footer are OCR'd for classification. Full-page OCR is triggered only for `is_list` preamble verification and page-specific list indexing. Do not change this without a strong reason — it is a deliberate token/latency constraint.

## LLM Integration

`cli.py` calls `ai chat` and `ai ocr` via subprocess (from `aistack`). No direct API calls. The prompt for deep inference is assembled in the `ingest` command in `cli.py` and is the single most logic-dense part of the codebase — changes there affect all classification downstream.

## Legacy Scripts

`batch_ocr.py`, `process_v2_metadata.py`, `assemble_results.py`, `organize_person_centric.py`, `multi_axis_index.py`, and the `organize_*.py` variants are earlier pipeline iterations. `multi_axis_index.py` is still used for bulk re-indexing from an existing `v2_metadata_results.json`. `mass_ingest.py` is a one-off automation script for scripted interactive prompts; not a general tool.

## Deployment-specific Config (`config.py`)

`USER_NAME = "Ashu"` and `ANCHOR_INSTITUTIONS` are hardcoded in `config.py`. Change these when deploying for a different user. All paths are computed relative to `Path(__file__)`, so the package is portable — no hardcoded absolute paths.

## Current Phase

v0.9 — Phase 5 (Agent Interface). Hindi NFC normalization and `fill`/`profile` commands are complete. Pending: slash-command REPL polish, semantic search (`aiclerk find`), mobile/web UI.

<!-- >>> context-kit >>> -->
This repo uses context-kit. Consult CODE_MAP / DEPS_MAP / ENV_MAP before Grep/Read.
At the start of the session, run 'sh .context-kit/ck brief' to orient yourself on the repository status, active maps, and pending tasks.
- Find where a symbol is defined: 'sh .context-kit/ck where <query>'
- Inspect a specific file's structure: 'sh .context-kit/ck show <path>'
- Print a compartment's symbol index: 'sh .context-kit/ck compartment <name>'
@AGENTS.md
<!-- <<< context-kit <<< -->
