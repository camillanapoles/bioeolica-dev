# Implementation Plan: Quality & Compliance Optimization — 94% Target

**Branch**: `007-quality-compliance-94pct` | **Date**: 2026-06-16 | **Spec**: `specs/007-quality-compliance-94pct/spec.md`

**Input**: Feature spec from `/speckit-specify` — optimization plan targeting 94% compliance based on FDC-U evaluation and quality audit findings.

---

## Context

The project was audited and found with **8 non-conformances** against INSTRUCTIONS.md quality mandates. FDC-U evaluation shows current PQMS at **56.2%** with target of **91.8%**. The user demands strict compliance with GitNexus-first analysis, FDC-U decision-making, mandatory integration tests + pytests with PQMS ≥ 95%, and Git workflow + Ops for continuity management.

---

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: pytest, numpy, scipy, CalculiX (system), Gmsh, CadQuery, CuPy (GPU)
**Storage**: Git LFS for binary data (meshes, results); Git for text/config
**Testing**: pytest (675 existing tests), per-task mandatory validation per M4
**Target Platform**: Linux (Ubuntu 22.04+), CPU fallback for GPU modules
**Project Type**: Multi-workspace engineering simulation platform (physics-m3, cad-cae, kdi-m3)
**Performance Goals**: CI pipeline < 15 min, test suite coverage ≥ 80%
**Constraints**: PYTHONUTF8 elimination, no sudo in CI, importlib workaround removal
**Scale/Scope**: 94 modules, 64 test files, ~856 tests, 5,303 GitNexus nodes

---

## Constitution Check

**GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.**

| Mandate | Status | Evidence |
|---------|--------|----------|
| **M1** — Singleton Execution | ✅ PASS | All tasks designed sequential, one per turn |
| **M2** — Sequential Dependency | ✅ PASS | Task dependency tree is linear, no parallel execution planned |
| **M3** — GitNexus-First Analysis | ✅ PASS | Every edit requires `node .gitnexus/run.cjs query` + `impact()` analysis |
| **M4** — Test-Only Validation | ✅ PASS | Every task validated by pytest exit code 0 (not file presence) |
| FSM: SPECIFY→HUMAN_GATE | ✅ PASS | Spec complete, awaiting plan approval gate |
| DoD rigor | ✅ PASS | All tasks require test PASS + commit + GitHub issue sync |

**Complexity justification**: Not applicable — no constitution violations.

---

## FDC-U Priority Order (from evaluation)

```
O2 Physical Validation (0.25) → gap 0.0975 — HIGHEST PRIORITY
O3 Architecture (0.20)       → gap 0.0880
O1 Completeness (0.30)       → gap 0.0870
O4 Portability (0.10)        → gap 0.0400
O5 Documentation (0.10)      → gap 0.0350
O6 Performance (0.05)        → gap 0.0075
```

---

## Project Structure

```
specs/007-quality-compliance-94pct/
├── spec.md           # Feature specification (done)
├── plan.md           # This file
├── research.md       # Phase 0 output — resolved unknowns
├── data-model.md     # Phase 1 output — entities & validation
├── quickstart.md     # Phase 1 output — validation guide
├── contracts/        # Phase 1 output — interface contracts
└── tasks.md          # Phase 2 output — task breakdown

workspaces/physics-m3/
├── modules/          # Physics modules (94 modules)
├── tests/            # Test suites (64 files, 856 tests)
│   ├── test_benchmarks/  # NEW: analytic benchmark tests
│   └── test_vvv_multiscale/  # NEW: VVV C11 automated suite

workspaces/cad-cae/
├── modules/          # CAD/CAE modules
└── tests/            # CAD/CAE tests

workspaces/kdi-m3/
├── modules/          # KDI M³ modules
└── tests/            # KDI tests
```

---

## Implementation Tasks

### Phase 0: Research (resolve unknowns)

1. **T001 — Research benchmark analytic solutions**: Document PL³/(3EI) cantilever, Kirsch Kt=3.0, NBR 6123 wind pressure formulas, tolerances per mesh refinement
2. **T002 — Research cross-workspace packaging**: Determine best approach (pip install -e . vs pyproject.toml vs namespace packages) for physics-m3, cad-cae, kdi-m3
3. **T003 — Research VVV certification criteria**: Define 6-criteria PASS/FAIL algorithm based on INSTRUCTIONS.md M3 VVV section
4. **T004 — Research CI/CD patterns**: GitHub Actions workflow for simulation projects with system dependencies (no sudo, no PYTHONUTF8)

### Phase 1: Design & Contracts

5. **T005 — Design BenchmarkAnalytic data model**: Fields: name, formula, domain, tolerance_by_mesh, expected_value, method
6. **T006 — Design VVVCertificate schema**: 6 binary criteria, error metrics, return_phase suggestion
7. **T007 — Design WorkspacePackage structure**: pyproject.toml per workspace, dependency graph between workspaces
8. **T008 — Design ComplianceReport model**: FDC-U scores by O1-O6, non-conformance tracking, PQMS trend
9. **T009 — Define interface contracts**: Cross-workspace public API surfaces, import stability guarantees

### Phase 2: Implementation — O2 Physical Validation

10. **T010 — Implement cantilever beam benchmark**: FEM vs PL³/(3EI) analytic, mesh refinement study, tolerance < 5%
11. **T011 — Implement plate_with_hole Kt benchmark**: FEM vs Kirsch (3.0), convergence with refinement, tolerance < 10%
12. **T012 — Implement wind pressure benchmark**: Pressure coefficient vs NBR 6123, tolerance < 10%
13. **T013 — Fix weak test asserts**: Replace isinstance/is not None with quantitative asserts in test_erosion.py (4 asserts), audit all 64 test files
14. **T014 — Implement test_benchmarks/ suite**: Pytest collection of all analytic benchmarks, CI-integrated

### Phase 3: Implementation — O3 Architecture

15. **T015 — Create pyproject.toml per workspace**: physics-m3, cad-cae, kdi-m3 as installable packages
16. **T016 — Refactor cross-workspace imports**: Replace importlib hack with proper package imports
17. **T017 — Update kdi_forwarder**: Remove _imp() workaround, use direct imports
18. **T018 — Test cross-workspace imports in clean env**: Validate no sys.path manipulation needed

### Phase 4: Implementation — O1 Completeness

19. **T019 — Implement VVV multi-escala C11 suite**: 6 criteria automated (convergence, stability, conservation, benchmark, cross-code, units)
20. **T020 — Implement VVVCertificate generator**: PASS/FAIL with quantified metrics + return_phase
21. **T021 — Implement WAL patch_protocol**: unified diff (git diff style), JSON Schema validation, rollback via snapshot
22. **T022 — Implement Mapa Único versioning**: Git LFS for binary, Git standard for text, DVC for data pipelines

### Phase 5: Implementation — O4 Portability

23. **T023 — Eliminate PYTHONUTF8 dependency**: Audit all scripts for encoding assumptions, fix to portable UTF-8
24. **T024 — Implement CuPy CPU fallback**: Graceful fallback with warning when CUDA unavailable
25. **T025 — Document system dependencies**: CalculiX, libGLU, Gmsh — install docs without sudo requirement
26. **T026 — Create Makefile/Justfile**: Unified build/test/setup commands for CI and local use

### Phase 6: Implementation — O5 Documentation + O6 Performance

27. **T027 — Create CI/CD GitHub Actions workflow**: pytest + coverage + GitNexus analysis, < 15 min
28. **T028 — Implement ComplianceReport generator**: FDC-U scoreboard, non-conformance tracking, PQMS dashboard
29. **T029 — Performance optimization of test suite**: Parallel pytest (xdist OK after all dependencies fixed), profile slow tests
30. **T030 — Final compliance audit**: Verify all 8 non-conformances closed, PQMS ≥ 95%, report generated

---

## Task Dependencies (M2 Sequential)

```
T001 → T002 → T003 → T004  (Phase 0 - can run in research at same time)
T005 → T006 → T007 → T008 → T009  (Phase 1 - sequential design)
T010 → T011 → T012 → T013 → T014  (Phase 2 - sequential implementation)
T015 → T016 → T017 → T018         (Phase 3 - sequential)
T019 → T020 → T021 → T022         (Phase 4 - sequential)
T023 → T024 → T025 → T026         (Phase 5 - sequential)
T027 → T028 → T029 → T030         (Phase 6 - sequential)
```

Per M2: Tasks are sequential within each phase. Each task requires previous task validated (test PASS) before starting.

---

## Mandates Alignment

| Mandate (INSTRUCTIONS.md) | Coverage |
|---------------------------|----------|
| **M1** Open Source First | Already ✅ — all tools open source (CalculiX, Gmsh, etc.) |
| **M2** Tool Selection & Integration | T015-T018 resolve cross-workspace integration |
| **M3** VVV | T019-T020 implement automated VVV C11 |
| **M4** Mapa Único | T022 implements versioning |
| **M5** Logs 5W1H | T021 WAL patch_protocol |
| **M6** RAG Knowledge | Existing RAG structure maintained |
| **M7** Foco Pertinente | Spec aligned to product (composite wind energy) |
| **M8** Segurança e Ética | Compliance audit ensures safety-critical coverage |
| **M9** Comunicação | T030 generates compliance report |

---

## Verification

1. **GitNexus** (M3 mandatory): Before any edit, run `node .gitnexus/run.cjs query <symbol>` + `impact()`
2. **FDC-U**: After each phase, recalculate FDC-U score to verify gap closure
3. **pytest per task** (M4 mandatory): Every task validated by `pytest path/to/test.py --exit-code-only`
4. **Integration test**: After Phase 3, run full cross-workspace import test
5. **Final audit**: `python -m pytest --coverage` + PQMS calculation = target ≥ 95%

---

## Artifacts to Generate

- `specs/007-quality-compliance-94pct/research.md` — Phase 0 findings
- `specs/007-quality-compliance-94pct/data-model.md` — Phase 1 entity definitions
- `specs/007-quality-compliance-94pct/quickstart.md` — Phase 1 validation guide
- `specs/007-quality-compliance-94pct/contracts/` — Interface definitions
- `specs/007-quality-compliance-94pct/tasks.md` — Task breakdown (post-plan approval)
