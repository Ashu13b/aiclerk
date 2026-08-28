<!-- context-kit ARCH_MAP · v0.1.0 · generated 2026-06-23 10:38 UTC · sha 9f903c3 · host vnic-trading -->

# ARCH_MAP

Top-level directories — what each is for + which dirs it imports. Consult before adding a cross-directory import; flagged cycles are architectural smells.

## Directories
- `./` — Docclerk is an agentic document orchestrator within the **Expeei** monorepo.
- `aiclerk/` — _(unset — add to `.context-kit/purposes`)_ → `app/`
- `app/` — _(unset — add to `.context-kit/purposes`)_ → `aiclerk/`

## Cycles
- `aiclerk/` → `app/` closes a cycle — consider breaking this edge
- `app/` → `aiclerk/` closes a cycle — consider breaking this edge
