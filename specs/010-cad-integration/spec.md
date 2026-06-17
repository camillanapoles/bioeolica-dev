# Feature Specification: CAD Integration — Production CAD Pipeline

**Feature Branch**: `010-cad-integration`

**Status**: Draft

## Objective

Bridge existing AI Assist CAD prototypes (NLP parser, layer designer, CAD generator) into a production-grade pipeline that outputs engineering drawings and 3D models ready for analysis.

## User Story 1 — Design Engineer: Generate CAD from Parameters (Priority: P1)

A design engineer wants to input engineering parameters and receive a CAD model (STEP) ready for FEM mesh.

**Independent Test**: `python -m src.cad.pipeline --params params.json --output model.step` succeeds.

**Acceptance Scenarios:**
1. Given engineering parameters (length, width, material), When pipeline runs, Then `.step` file is generated
2. Given the same parameters, When run twice, Then output models are identical (deterministic)
3. Given generated STEP, When meshed with Gmsh, Then mesh converges (no geometry errors)

## User Story 2 — Multimaterial: Layer Designer (Priority: P2)

A design engineer wants to create multimaterial layered composites with coating.

**Independent Test**: `python -m src.cad.layers --config layer_config.json --output composite.step` succeeds.

## Technical Approach

### Pipeline

```
params.json → ParametricModel → CadQuery → STEP → Gmsh → MSH → CalculiX → FRD
                                                         → LLM-NLP Layer Designer
```

### Architecture

- `src/cad/pipeline.py` — CLI orchestrator
- `src/cad/parametric.py` — ParametricModel from JSON spec
- `src/cad/layer_designer.py` — N×M multimaterial layer composer (from AI Assist CAD prototype)
- `src/cad/export.py` — STEP export with metadata

## Out of Scope

- 3D visualization (C9 — future)
- Interactive CAD editing
- Assembly-level CAD (single parts only)
