# Implementation Plan: CAD+REPORT Pipeline

## Technical Context

| Campo | Valor |
|-------|-------|
| Language | Python 3.11+ |
| Dependencies | cadquery, jinja2, numpy |
| Existing | C2 src/crslr/ (11 tests), C3 src/cad/ (8 tests) |
| New | src/cadreport/ — orchestrator |
| Testing | pytest, deterministic output comparison |

## Project Structure

```
src/cadreport/
├── pipeline.py    # CLI orchestrator
├── metadata.py    # CAD metadata → CRSLR bridge
└── __init__.py
tests/
└── test_cadreport.py
```

## Dependencies

- C2 src/crslr/ ✅ (complete)
- C3 src/cad/ ✅ (complete)

## Execution Order

1. metadata bridge → pipeline orchestration → tests → CLI
