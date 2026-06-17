---

description: "Task list for Spec 012 — CAD+REPORT (C8)"
---

# Tasks: 012 CAD+REPORT — Integrated Engineering Pipeline

**Prerequisites:** C2 src/crslr/ ✅ | C3 src/cad/ ✅

## Phase 1: Setup

- [X] T001 Create directory `src/cadreport/` with `__init__.py`
- [X] T002 Create test file `tests/test_cadreport.py`

## Phase 2: Foundational

- [X] T003 Implement `src/cadreport/metadata.py` — bridge from ParametricModel → CRSLR input JSON (extracts width, height, depth, material, machine_type)
- [X] T004 Implement `src/cadreport/pipeline.py` — CLI orchestrator: load params → CAD (STEP) → CRSLR report (MD) → metadata (JSON) → checksums

## Phase 3: User Story 1 — Engineer: Generate CAD+Report (P1) 🎯 HERO

- [X] T005 [US1] Add `--format` (markdown/html/pdf) and `--no-mesh` flags to pipeline CLI
- [X] T006 [US1] Implement output directory creation with all 4 artifacts: model.step, report.md, metadata.json, checksums.sha256
- [X] T007 [US1] Wire metadata.py to the CRSLR engine for report context section

**Checkpoint**: `python -m src.cadreport.pipeline --params tests/fixtures/cube_params.json --output-dir /tmp/package` succeeds

## Phase 4: Polish

- [X] T008 Run full test suite: `pytest tests/test_cadreport.py -v --tb=short`
- [X] T009 Run quickstart validation per `specs/012-cad-report/quickstart.md`
- [ ] T010 Commit "012 Fase 2: CAD+REPORT (C8) — integrated engineering pipeline"
