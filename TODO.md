# Docclerk — TODO / Roadmap

Status: v0.9 — Hindi matra Optimization & Agent Interface.

---

## ✅ Phase 1: Foundation (Complete)
- [x] Satisficed Reading (header/footer OCR)
- [x] Person-centric metadata schema
- [x] Multi-axis symlink index architecture

## ✅ Phase 2: Interactive Clerk CLI (Complete)
- [x] Person Discovery workflow (confirm + track new persons)
- [x] List Indexer (page/row mapping with visual verification)
- [x] Relational Matrix (institutions, assets, domains)
- [x] Official Form Preservation (GA 55, Form 16, etc.)

## ✅ Phase 3: Three Intelligence Loops (Complete)
- [x] **P0 — Registry write-back**: every ingest appends to `v2_metadata_results.json`
- [x] **P0 — Vault routing**: physical symlinks into `service_records/`, `professional_output/`, `insights/`
- [x] **Loop 2 — `relevance_intent`**: user states *why* they saved
- [x] **Loop 2 — `docclerk review`**: process queued low-confidence items
- [x] **Loop 3 — `docclerk timeline <prefix>`**: chronological markdown service book

## ✅ Phase 4: Reliable Sync
- [x] **Incremental Sync**: `docclerk sync` — reconcile inbox with registry to process only new/changed files
- [ ] **Search**: `docclerk find <query>` — sqlite-vss semantic search

---

## 🔭 Phase 5: Agent Interface (UI & Slash CLI)
- [x] **Hindi Matra Optimization**: Implement Unicode NFC normalization in `clerk.py`.
- [ ] **Slash Command REPL**: Interactive shell with `/` commands.
- [ ] **DocClerk Mobile-Web UI**: React Native (Expo) dashboard.
- [ ] **Real-time Notifications**: Background agent alerts.

---
*Last Update: 2026-05-11 — v0.9 added Hindi Fixes & Interface roadmap.*
