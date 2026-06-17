---

description: "Task list for Spec 010 — CAD Integration (C3)"
---

# Tasks: 010 CAD Integration — Production CAD Pipeline

**Input**: Design documents from `specs/010-cad-integration/`

## Phase 1: Setup

- [X] T001 Create directory `src/cad/` with `__init__.py`
- [X] T002 Create test file `tests/test_cad_pipeline.py`

## Phase 2: Foundational

- [X] T003 Implement `src/cad/parametric.py` — ParametricModel dataclass from JSON spec, positive dimension validation
- [X] T004 Implement `src/cad/cad_generator.py` — CadQuery geometry builder from ParametricModel (box, cylinder, extrusion primitives)

## Phase 3: User Story 1 — Generate CAD from Parameters (P1)

- [X] T005 [US1] Implement `src/cad/pipeline.py` — CLI orchestrator: load JSON → ParametricModel → CAD → STEP export
- [X] T006 [US1] Implement `src/cad/export.py` — STEP file export with SHA-256 metadata
- [X] T007 [US1] Create test fixture `tests/fixtures/cube_params.json` — simple box 100×50×20mm
- [X] T008 [US1] Implement `src/cad/mesh.py` — Gmsh meshing bridge from STEP to MSH
- [X] T009 [US1] Run pipeline validation: `python -m src.cad.pipeline --params tests/fixtures/cube_params.json --output /tmp/test_cube.step`

## Phase 4: User Story 2 — Multimaterial Layer Designer (P2)

- [X] T010 [US2] Implement `src/cad/layer_designer.py` — N×M multimaterial composer, layer thickness validation
- [X] T011 [US2] Create test fixture `tests/fixtures/layer_config.json` — 3-layer composite with coating
- [X] T012 [US2] Run layer validation: `python -m src.cad.layers --config tests/fixtures/layer_config.json --output /tmp/test_composite.step`

## Phase 5: Polish

- [X] T013 Run full test suite: `pytest tests/test_cad_pipeline.py -v --tb=short`
- [ ] T014 Commit "010 Fase 1: CAD Integration (C3) — production pipeline"
