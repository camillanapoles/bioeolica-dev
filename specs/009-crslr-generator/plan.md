# Implementation Plan: CRSLR Generator

## Technical Context

| Campo | Valor |
|-------|-------|
| Language | Python 3.11+ |
| Dependencies | jinja2, weasyprint, markdown, numpy |
| Testing | pytest, golden file tests for report outputs |
| Storage | None (stateless — reads JSON, writes report) |
| Target | Linux (WSL2) |

## Constitution Check

✅ C2 (sequential): No parallel phases needed
✅ C3 (GitNexus): src/ directory clean, no conflicts
✅ M9 (Communication): CRSLR is the M9 delivery format

## Project Structure

```
src/crslr/
├── engine.py           # CRSLR report generator
├── templates/
│   ├── report.md.j2    # Jinja2 Markdown template
│   └── report.html.j2  # Jinja2 HTML template (for PDF)
├── render.py           # Markdown → PDF (WeasyPrint)
├── schema.py           # Input JSON schema validation
└── __init__.py
tests/
├── test_engine.py
├── test_render.py
└── fixtures/
    └── sample_results.json
```

## Phase 0: Research

- Jinja2 template patterns for engineering docs
- WeasyPrint PDF rendering
- KaTeX for equations

## Phase 1: Design

- `data-model.md`: ReportSection entity (name, content, priority)
- Contract: CRSLR input JSON schema
- Quickstart: `pytest tests/ -k "crslr" -v`

## Execution Order

1. Template design → Engine → Render → Tests → CLI
