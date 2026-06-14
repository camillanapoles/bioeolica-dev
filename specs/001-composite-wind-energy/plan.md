# Implementation Plan: Composite Biomaterial for Wind Energy

**Branch**: (none — local workspace) | **Date**: 2026-06-12 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification for 3-part research project: (1) paper mache + graphite composite characterization, (2) wind turbine system design for semi-arid Brazil, (3) SQLite-based data management with PQMS >= 9.5

---

## Summary

This plan covers a multi-scale computational-experimental research project to develop and validate an ecological composite biomaterial (paper mache substrate + graphite coating applied by blasting) for use as wind turbine blade base material, targeting low-cost wind energy for agricultural communities in the Brazilian semi-arid Sertao region. Three interconnected workstreams:

1. **Material characterization** — macro/meso/micro analysis of the composite vs. raw paper mache baseline, quantifying mechanical property improvements (target: +40% hardness, +25% flexural modulus)
2. **Wind energy system design** — compare VAWT vs Archimedes-type turbines, size system for community agricultural energy needs, optimize for low wind speeds (4-7 m/s)
3. **Data management & quality** — SQLite-backed provenance tracking with UUID v4, PQMS >= 9.5 target, 100% method validation

---

## Technical Context

**Project Type**: Computational research + experimental validation (material science + wind energy engineering)

**Computational Methods**:
- FEM (structural): CalculiX, Code_Aster — blade structural analysis, stress distribution
- CFD (aerodynamics): OpenFOAM, SU2 — blade aerodynamic profiles, VAWT vs Archimedes comparison
- Multi-scale: Macro (FEM blade-level) → Meso (interface zone) → Micro (particle distribution, adhesion)
- ML/DL (surrogate modeling): Python (PyTorch/DeepXDE) for Physics-Informed Neural Networks as ROM substitutes

**Experimental Methods**:
- Mechanical testing per ASTM D638/D790/D695/D2240/D7774
- Microstructural characterization: SEM/optical microscopy for interface analysis
- LCA for environmental validation

**Storage**: SQLite with UUID v4 primary keys, provenance tracking via object chains, structured querying

**Data Model Entities**: Material Specimen, Test Result, Microstructure Image, Computational Model, Simulation Result, Blade Design, Wind Turbine System, Energy System, Community Profile, Validation Reference

**Validation Framework**: PQMS with 12 dimensions (D1-D13), target >= 9.5/10, methodology validation sub-score = 1.0 (100% methods validated against benchmarks)

**Target Platform**: Linux (computational environment), open source toolchain (CalculiX, OpenFOAM, FreeCAD, ParaView, Python)

**Performance Goals**: 
- Computational model accuracy vs. experiment: < 10% relative error
- FEM mesh convergence: < 5% variation between successive refinements
- LCOE target: < $0.15/kWh
- Installed cost target: < $3,000/kW

**Constraints**:
- Open source tools only (no commercial licenses for ANSYS/ABAQUS/COMSOL)
- Community-scale production: manual/labor-acceptable processes, minimal specialized equipment
- Local material availability: post-consumer recycled paper, industrial-grade graphite
- PQMS >= 9.5 mandatory with methodology validation sub-score = 1.0

**Scale/Scope**:
- ~100-300 material specimens (baseline + composite, multiple parameter variations)
- ~50-100 simulation runs (FEM + CFD, parametric studies)
- 1 complete wind energy system design per turbine type (VAWT + Archimedes)
- 1 community profile (10-30 families, 2-5 ha irrigation)

**NEEDS CLARIFICATION** (resolved during Phase 0 research):
1. Graphite type and application method — default to dry abrasive blasting with flake graphite (most community-viable)
2. Binder composition for paper mache — default to PVA/water ratio to be determined experimentally
3. Specific community energy consumption data — default to published data for similar semi-arid agricultural communities
4. Data access model — default to local SQLite single-user (multi-user sync deferred)

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Gate | Status | Justification |
|------|--------|---------------|
| SPECIFY complete | ✅ PASS | spec.md created with 5 user stories, 21 FRs, 10 entities, 10 SCs |
| HUMAN_GATE passed | ✅ PASS | User invoked /speckit-plan directly, bypassing remaining clarify questions |
| No NEEDS CLARIFICATION in spec | ✅ PASS | All markers resolved via informed assumptions during specify |
| FSM flow respected | ✅ PASS | SPECIFY → (implicit HUMAN_GATE via user action) → PLAN |
| Max 3 self-healing attempts | ✅ PASS | N/A — first planning cycle |
| Open source only | ✅ PASS | All tools in spec are open source (CalculiX, OpenFOAM, FreeCAD, ParaView, Python) |
| PQMS >= 9.5 target | ✅ PASS | Defined in SC-008 with methodology validation sub-score = 1.0 |
| M³ methodology required | ✅ PASS | Macro-Meso-Micro analysis is core to all three parts |

**No violations detected.** Proceeding to Phase 0.

---

## Project Structure

### Documentation (this feature)

```text
specs/001-composite-wind-energy/
├── spec.md              # Feature specification (complete)
├── plan.md              # This file
├── research.md          # Phase 0 — research decisions & rationale
├── data-model.md        # Phase 1 — entity definitions, SQLite schema
├── quickstart.md        # Phase 1 — validation scenarios & reproduction steps
├── contracts/           # Phase 1 — interface contracts (SQL schema, API)
├── checklists/
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Phase 2 — task breakdown (created by /speckit-tasks)
```

### Source Code (repository root)

```text
# Scientific research project — code organized by workstream

src/                                # Computational models and analysis code
├── 01-material-characterization/   # Part 1: Material composite analysis
│   ├── fem/                        # FEM models (CalculiX .inp files)
│   ├── meso-interface/             # Meso-scale interface models
│   ├── micro-particle/             # Micro-scale particle distribution
│   └── analysis/                   # Python analysis scripts
│
├── 02-wind-energy/                 # Part 2: Wind turbine design
│   ├── aerodynamics/               # CFD models (OpenFOAM cases)
│   ├── structural/                 # Blade structural FEM
│   ├── energy-system/              # System sizing calculations
│   └── comparison/                 # VAWT vs Archimedes comparison
│
├── 03-data-management/             # Part 3: SQLite + provenance
│   ├── schema/                     # SQLite schema definitions
│   ├── etl/                        # Data ingestion pipelines
│   └── quality/                    # PQMS computation framework
│
├── common/                         # Shared utilities
│   ├── materials-db/               # Material property database
│   └── validation/                 # VVV framework implementation
│
└── visualization/                  # ParaView states, plotting scripts

tests/                              # Validation and verification
├── validation/                      # Cross-code validation benchmarks
├── mesh-convergence/               # Mesh independence studies
└── reproducibility/                # Third-party reproducibility tests

data/                               # Data directory (gitignored, tracked via DVC)
├── specimens/                       # Material specimen records
├── simulations/                     # Simulation input/output files
├── experiments/                     # Experimental test data
└── references/                      # Published benchmarks & standards

knowledge/                           # RAG knowledge base (existing)
├── MathematicalEngineeringDeepLearning/
├── materials/
└── wind-energy/
```

**Structure Decision**: Single monorepo with three workstream subdirectories under `src/`, mirroring the three parts of the spec. Shared utilities in `common/`. All data in `data/` (not committed to git — managed via DVC + Git LFS). Validation and reproducibility tests in `tests/`.

---

## Complexity Tracking

No constitution violations detected. No complexity justification needed.

---

## Phase 0: Research Plan

### Unknowns Requiring Research

| # | Unknown | Research Approach | Expected Output |
|---|---------|-------------------|-----------------|
| R1 | Paper mache binder formulation (PVA type, ratio, curing) | Literature review of paper mache composites + preliminary experimental data | Recommended binder formulation for target mechanical properties |
| R2 | Graphite blasting equipment availability in NE Brazil | Market survey of compressed air / blasting equipment distributors in Sertao region | Feasibility assessment with cost estimates |
| R3 | Community energy consumption baselines for semi-arid agriculture | INMET/SONDA wind data + published community energy studies + ISA/IBGE agricultural statistics | Energy demand profile (kWh/day) with seasonal variation |
| R4 | VAWT vs Archimedes performance at low wind speeds (4-7 m/s) | Literature comparison + preliminary CFD screening | Decision framework with evaluation criteria |
| R5 | SQLite schema for scientific provenance tracking | Provenance tracking patterns (W3C PROV, CWL) adapted to SQLite | Schema design with UUID v4 + provenance chains |
| R6 | PQMS computation framework for multi-domain research | Adapt existing 12-dimension framework from KDI/INSTRUCTIONS.md | Automated PQMS calculator |
| R7 | OpenFOAM vs SU2 for low-Re blade aerodynamics | Benchmark comparison for relevant Re range (1e5-5e5) | Recommended CFD tool for this application |

### Research Execution

Each R item above will be investigated using available literature, web resources, and computational benchmarks. Findings consolidated in [research.md](research.md).

---

## Phase 1: Design & Contracts

**Prerequisites**: research.md complete

1. **Data Model** → [data-model.md](data-model.md): SQLite schema with 10 entities, UUID v4, provenance chains
2. **Contracts** → [contracts/](contracts/): SQL schema DDL, validation rules, PQMS computation interface
3. **Quickstart** → [quickstart.md](quickstart.md): Reproduction guide for all 3 parts
4. **Agent Context Update**: Update CLAUDE.md with plan reference

---

## Phase 2: Task Breakdown

Generated by `/speckit-tasks` — creates [tasks.md](tasks.md) with decomposed work items per workstream.

---

## Success Criteria (from spec)

- **SC-001**: +40% hardness, +25% flexural modulus. Validated by 10+ replicates.
- **SC-002**: Model vs. experiment < 10% error. All primary properties.
- **SC-003**: Blade safety factor >= 2.0 per IEC 61400-2.
- **SC-004**: LCOE < $0.15/kWh, installed cost < $3,000/kW.
- **SC-005**: 100% demand met, 2-day autonomy, capacity factor >= 20%.
- **SC-006**: Data-driven VAWT vs Archimedes recommendation across 8+ criteria.
- **SC-007**: Full provenance audit pass for every data object.
- **SC-008**: PQMS >= 9.5, methodology validation sub-score = 1.0.
- **SC-009**: 3 independent results reproducible from stored data.
- **SC-010**: LCA confirms 60% lower carbon vs. fiberglass; 80% biodegradable/recyclable.
