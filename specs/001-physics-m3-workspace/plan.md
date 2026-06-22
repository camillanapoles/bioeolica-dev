# Implementation Plan: Physics M³ Workspace

**Branch**: `main` | **Date**: 2026-06-14 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/001-physics-m3-workspace/spec.md`

## Summary

Computational mechanics workspace for multi-scale (M³) analysis of bio-based composite materials (waste paper + PVA + graphite). Covers material characterization → mechanical test emulation → structural/fluid/thermal/electrical/CFD analysis → CAD 3D visualization → VVV certification → domain expansion (peridynamics, topology optimization, fatigue, creep, digital twin, piezoelectric, erosion). Python + NumPy/SciPy stack, open source per KDI M1.

## Technical Context

**Language/Version**: Python 3.13

**Primary Dependencies**: NumPy, SciPy, Matplotlib, pytest

**Storage**: SQLite (embedded, `bioeolica.db`), JSONL logs (`data/logs/`), JSON index (`master_index.json`)

**Testing**: pytest (295 tests, 0 failures across 19 test files)

**Target Platform**: Linux (CLI + Jupyter notebooks)

**Project Type**: Library + Jupyter workspace (30 analytical engineering modules)

**Performance Goals**: M³ analysis < 0.1s, FEM solve < 0.01s, all 295 tests < 30s

**Constraints**: Zero proprietary dependencies, all analytical models deterministic, no GPU required

**Scale/Scope**: 10 engineering domains (all implemented), 30 modules, 4 Jupyter labs, 295 tests

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Gate | Status | Evidence |
|------|--------|----------|
| M1 — Singleton | ✅ | Sequential task execution per module |
| M2 — Sequential Dependency | ✅ | Each module builds on previous dependencies |
| M3 — GitNexus Analysis | ✅ | `node .gitnexus/run.cjs analyze` — 3,795 nodes, 6,143 edges |
| M4 — Test Validation | ✅ | 295 tests passing, pytest per module |

**Gate verdict**: PASS ✅ — all constitution gates satisfied.

## Project Structure

### Documentation (this feature)

```text
specs/001-physics-m3-workspace/
├── spec.md              ← Feature specification
├── plan.md              ← This file
├── research.md          ← Phase 0 output
├── data-model.md        ← Phase 1 output
├── quickstart.md        ← Phase 1 output
├── contracts/           ← Phase 1 output
└── tasks.md             ← Phase 2 output (/speckit-tasks)
```

### Source Code (repository root)

```text
instruments/physics-m3/
├── modules/             ← 30 Python analytical modules (core + expansion)
├── notebooks/           ← 4 Jupyter labs
├── tests/               ← 19 test files, 295 tests
├── data/                ← M4/M5/M6 data storage
└── cad/                 ← STL export directory

tests/ (project root)
└── validation/          ← Project-level validation tests
```

**Structure Decision**: Brownfield project complete. Next feature cycle (TopOpt Avançada) follows same patterns.

## Complexity Tracking

N/A — all Constitution gates passed without violations.

## Phases

### Phase 0: Research

Already completed via MCP web-search-prime. 30+ sources collected on:
- Bio-based composite materials (paper mache, PVA, graphite)
- Open source FEM/CFD tools
- Wind turbine LCA methodologies
- VVV certification standards

**No NEEDS CLARIFICATION markers** — all technical decisions made per KDI methodology.

### Phase 1: Design & Contracts

**Data Model**: Defined in spec Key Entities. Implemented as Python dataclasses.

**Contracts**: Internal module APIs via imports. 12 modules with documented interfaces.

**Quickstart**: 3 Jupyter notebooks providing executable demonstrations.

### Phase 2: Tasks

To be generated via `/speckit-tasks`. Current implementation state:
- 30 modules, 295 tests, 4 notebooks — all functional
- All 10 KDI domains implemented (mecanica, fluidos, termo, energia, eletricidade, materiais, construcao, ambiente, normativo, economico)
- M4+M5+M6 infrastructure complete
- P1-P5 all complete per spec requirements

## Next Feature Cycle (FDC-U Result)

**FDC-U scoring identified O1 — TopOpt Avançada (Score: 0.715) as best next route.**

### FDC-U Ranking
| Rank | Route | Score | Gate |
|------|-------|-------|------|
| 🥇 1 | O1 TopOpt Avançada | 0.715 | ✅ KDI |
| 🥈 2 | O6 Validação Experimental | 0.690 | ✅ KDI |
| 🥉 3 | O5 Pacote PIP + CI/CD | 0.625 | ✅ KDI |

### Next Actions
1. Create new spec: `specs/002-topopt-avancada/spec.md`
2. Follow speckit lifecycle: specify → plan → tasks → implement
3. TopOpt Avançada features: 3D SIMP, multi-objetivo (massa×rigidez×custo), manufatura aditiva (overhang)
