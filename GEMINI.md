# Docclerk - Intelligent Document Clerk

Docclerk is a specialized document management component within the **Expeei** monorepo. It acts as an agentic "clerk" that handles complex document workflows.

## Primary Goal: Classification & Placement
The core objective is **not** full-text transcription, but **document understanding**:
1. **Identify**: What is this document? (e.g., Office Order, Medical Degree, Receipt)
2. **Index**: Extract the crucial "who, what, when" metadata (Ref No, Date, Persons).
3. **Place**: Direct the document to the correct logical or physical destination based on its type.

## Satisficed Reading Strategy
To optimize for speed and token efficiency:
- **Anchor Pages**: Focus on the first and last pages to extract context and signatures.
- **Heuristics**: If a document is identified as a "Book" or "Large Report," skip internal pages unless specifically requested.

## Key Files (Current)
- **`README.md`**: General project overview and setup instructions.
- **`SPEC.md`**: Technical specification, including workflow definitions and API contracts.
- **`TODO.md`**: Active roadmap and task tracking for the implementation phase.
- **`GEMINI.md`**: (This file) Instructional context for Gemini CLI interactions.

## Development Conventions
As a part of the Expeei monorepo, Docclerk follows these standards:
- **Shared State**: Uses `ai-commons` for atomic persistence and process tracking.
- **Local-First**: Prioritizes local model discovery and execution via `ailocal`.
- **Declarative**: Aims to define workflows via YAML/JSON "shapes" similar to `aistack`.

## Commands (Anticipated)
*Note: Since the project is in its early documentation phase, these commands are inferred from the Expeei architecture.*
- `pip install -e .` (within the project directory to install in editable mode).
- Integration with the `ai` CLI from `aistack`.

---
*TODO: Update this file as implementation begins and specific build/test commands are established.*
