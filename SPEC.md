# Docclerk - Technical Specification

Docclerk is an intelligent document orchestrator. Unlike a bulk OCR tool, its goal is to **understand** a document's intent and metadata to determine its "place" in a system or workflow.

## Core Logic: Triple-Stream Intelligence
Docclerk categorizes documents into three primary "Vaults" to handle personal history, professional work, and general knowledge:

### 1. The Service Record (Career Timeline)
Documents **about** the person's employment status, benefits, and history.
- *Examples*: Appointment orders, Leave approvals, Salary GA55A, Promotions.
- *Goal*: Tracking the individual's career path.

### 2. The Professional Output (Work Log)
Documents **prepared by** or **signed by** the person in their official capacity.
- *Examples*: Medical opinions, Post-mortem reports, Fitness certificates.
- *Naming*: Drop generic words like "Report". Use specific output tags (e.g., `ash-medical-opinion-2026.pdf`).
- *Goal*: Tracking the person's professional contributions and workload.

### 3. The Knowledge Base (Insights & Precedents)
Focuses on the **Content/Rules**. Saved for general reference.
- *Goal*: Insight extraction and legal/medical reference.

## Operations: Interactive Intelligence
Docclerk transitions from purely automated filing to an **Interactive Clerk** model to ensure high-stakes accuracy.

### 1. Person Discovery Workflow
For documents with a clear primary subject:
- **Known Person**: Auto-file into their specific vault using high-density naming (e.g., `ash-`).
- **New Person Found**: 
  1. The Clerk pauses and presents the person's details to the user.
  2. Ask: "I found a new person: [Name]. Should I add them to the database and track their Service Record?"
  3. If YES: Create a new vault and add to `KNOWN_PERSONS`.
  4. If NO: File the document under `insights/`.

### 2. Multi-Person List Mapping
Documents are automatically flagged as `is_list: true` using a **Wide-Spectrum Deduction Logic**. Once flagged, the Clerk triggers the **Interactive Phase**:
- **Pause & Request**: The Clerk identifies the file as a "Wide Spectrum List" and asks for specific page/row details.
- **Visual Verification**: The Clerk OCRs the specific page requested to confirm the target person is present.
- **Result**: Create a **Point-of-Interest Symlink** in the target person's vault.

### 3. Weighted Priority Deduction
The Clerk uses a **Tiered Weight System** (Self, Family, Anchor Inst, Friends, General) to filter document importance.

## Interface: The Multi-Modal Agent

### 1. Slash Command CLI (`docclerk /`)
To provide a modern "ChatOps" experience, the CLI will support an interactive shell with slash commands:
- `/ingest [file]`: Manual trigger for document processing.
- `/review`: Enter the interactive loop for low-confidence or high-priority findings.
- `/find [query]`: Execute a semantic search across the entire vault.
- `/ls [person]`: List documents and status for a specific person.
- `/gaps [person]`: Run the gap analysis reporter.

### 2. DocClerk UI (Mobile/Web)
A React Native interface (inspired by `medqa-app`) to provide visual oversight:
- **Dashboard**: High-level stats on Vault health and recent ingests.
- **Inbox Hub**: A unified "Needs Review" queue with document previews.
- **Interactive Correction**: Touch-based UI to refine metadata (date, subject, vault).
- **Timeline View**: Visual representation of a person's Service Record with linked documents.

## Multi-Language Constraints: Hindi Matra Support
The agent must correctly handle Devanagari script (Hindi). 
- **Unicode Normalization**: All extracted text is normalized to **NFC (Canonical Composition)** during ingestion to ensure matras (combining marks) are properly assimilated into base characters.
- **Rendering**: The UI version must use fonts that support complex text layout (CTL) to prevent broken matra rendering.

## Operational Constraints
- **Efficient Processing**: For large documents, do NOT OCR the entire file. Satisfy classification using anchor pages.
- **Multilingual Support**: Must handle Hindi and English headers and subjects.
- **Shared State**: All metadata is stored in a structured JSON format.
- **Stateful Sync**: The `sync` operation uses a reconciliation pattern to allow for reliable offline processing.
- **Concurrency**: Use file locking (via `ai-commons`) to prevent processing collisions.

## Extraction Schema
See `SCHEMA.json` for the formal metadata structure.
