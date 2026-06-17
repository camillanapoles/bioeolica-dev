# Implementation Plan: CAD Integration Pipeline

## Technical Context

| Campo | Valor |
|-------|-------|
| Language | Python 3.11+ |
| Dependencies | cadquery, gmsh, numpy, pydantic |
| Testing | pytest, deterministic geometry comparison |
| Storage | data/cad_models/ (STEP files) |
| Target | Linux (WSL2) |

## Constitution Check

✅ C1 (singleton): Uses data/bioeolica.db as metadata store
✅ C3 (GitNexus): import existing ai_assist_cad/ modules
✅ M4 (test-only validation): Each module independently testable

## AI Assist CAD Integration

Existing prototype modules to integrate:
- `ai_assist_cad/cad_generator.py` → refactor into `src/cad/pipeline.py`
- `ai_assist_cad/layer_designer.py` → refactor into `src/cad/layer_designer.py`
- `ai_assist_cad/nlp_parser.py` → refactor into `src/cad/parametric.py`

## Project Structure

```
src/cad/
├── pipeline.py         # CLI orchestrator
├── parametric.py       # ParametricModel from JSON (from nlp_parser)
├── layer_designer.py   # N×M multimaterial layer composer
├── cad_generator.py    # CadQuery geometry builder
├── export.py           # STEP export with metadata
├── mesh.py             # Gmsh meshing bridge
└── __init__.py
tests/
├── test_pipeline.py
├── test_parametric.py
├── test_layer_designer.py
└── test_mesh.py
```

## Execution Order

1. Parametric model → Layer designer → CAD generator → Export → Mesh → Tests
