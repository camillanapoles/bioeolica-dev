# Feature Specification: CAD+REPORT — Integrated Engineering Pipeline

**Feature Branch**: `012-cad-report`

**Status**: Draft

## Objective

Combine C2 (CRSLR Generator) and C3 (CAD Integration) into a unified pipeline: parameters → CAD model + engineering report + mesh, delivered in one command.

## User Story 1 — Engineer: Generate CAD+Report (Priority: P1) 🎯 HERO

An engineer wants to input parameters and receive a complete engineering package: STEP model + CRSLR report + MSH mesh.

**Independent Test**: `python -m src.cadreport.pipeline --params params.json --output-dir /tmp/package` succeeds.

**Acceptance Scenarios:**
1. Given parameters JSON, When pipeline runs, Then directory contains `.step`, `.md`, `.json` (metadata)
2. Given the same parameters, When run twice, Then STEP checksums match (deterministic CAD)
3. Given the output, When rendered, Then CRSLR report contains CAD metadata + metrics

## Technical Approach

### Pipeline

```
params.json → ParametricModel → [CAD pipeline → STEP]
                               → [CRSLR engine → Report (.md)]
                               → [Export → Package (.step + .md + .json)]
```

### Integration

- Reuse `src/cad/` modules: pipeline.py, export.py, parametric.py
- Reuse `src/crslr/` modules: engine.py, schema.py, templates/
- New: `src/cadreport/pipeline.py` — orchestrator
- New: `src/cadreport/metadata.py` — CAD metadata → CRSLR input bridge

## Out of Scope

- 3D visualization (C9 — future)
- Interactive editing
