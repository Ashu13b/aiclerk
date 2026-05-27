# Docclerk — Intelligent Document Clerk

Docclerk is an agentic document orchestrator within the **Expeei** monorepo. It moves beyond simple OCR toward **Context-Aware Document Understanding** and **Relational Indexing**.

## Core Capabilities
- **Growing Intelligence**: Dynamically identifies administrative actions (Application, Order, Certificate) from text context without hardcoded rules.
- **Relational Matrix**: Maintains a persistent "Web of Associations" linking individuals to institutions, professional domains (e.g., Doctor), and personal assets (e.g., Vehicle RJ23...).
- **Cross-Language Mapping**: Natively recognizes names and locations across Hindi (Devanagari) and English scripts.
- **Visual Verification**: Interactively pauses to verify multi-person "List" entries (e.g., Selection Orders) by OCRing specific pages.
- **Perfect Naming**: Generates high-density, professional filenames: `[Prefix]_[Action]_[Year]_[AssetID].pdf`.

## Current Status (v0.5)
- **Phase 2 Complete**: Interactive CLI (`clerk.py`) is fully operationalized and stabilized.
- **Library Status**: 27 sample documents processed, organized, and archived with 'Perfect' naming standards.
- **Next Phase**: Focus on **Automated Timelines** and **Semantic Search Integration**.

## Usage
```bash
python3 clerk.py ingest path/to/document.pdf
```

## Project Structure
- `clerk.py`: The primary interactive engine.
- `SPEC.md`: Detailed technical logic (Triple-Stream, Significance Hierarchy).
- `SCHEMA.json`: Canonical metadata structure.
- `organized_docs/`: The organized physical and virtual document library.
