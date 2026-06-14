# Implementation Plan: Turbine Upscaling for Economic Viability

**Branch**: `002-turbine-upscaling` | **Date**: 2026-06-13 | **Spec**: [specs/002-turbine-upscaling/spec.md](../spec.md)

**Input**: Feature specification from `specs/002-turbine-upscaling/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Design an upscaled wind turbine (10-15 kW range) that meets economic viability targets (LCOE < $0.15/kWh, cost < $3,000/kW) and community demand coverage (>= 100% of 38 kWh/day). Compare VAWT H-rotor Darrieus vs HAWT Archimedes topologies. Current 0.82 kW prototype fails all economic targets (LCOE $1.42/kWh, $48,204/kW) — fixed costs dominate at sub-1 kW scale requiring cost scaling model to identify minimum viable size.

Approach: Bottom-up cost scaling model from material bill-of-materials → wind resource AEP computation → LCOE/economic metrics → energy storage sizing → DB registration → validation. Part 1 (material computational modeling) is the PRIMARY scope per user directive; Part 2 (turbine application/energy analysis) is the secondary scope addressed in this iteration.

## Technical Context

**Language/Version**: Python 3.11+ (existing scripts in `src/02-wind-energy/`)

**Primary Dependencies**:
- NumPy/SciPy — numerical computation, Weibull statistics, matrix operations
- Matplotlib — visualization of cost scaling curves, AEP, sensitivity analysis
- SQLite3 — database operations (stdlib, bioeolica.db)
- pytest — test framework (validation checks)

**Storage**: SQLite (existing `data/bioeolica.db`) — single source of truth for all objects, metrics, and validation state

**Testing**: pytest (`tests/validation/`) + `run_all_checks.sh` (28-check validation suite, currently 24/28 PASS)

**Target Platform**: Linux (Ubuntu 22.04+), single machine, no deployment pipeline

**Project Type**: Engineering analysis scripts (computational modeling + DB registration) — not a library, CLI tool, or web service

**Performance Goals**: Computational models must complete in < 60s per turbine configuration to enable multi-configuration sweep (5-20 kW range, 2 topologies, sensitivity analysis). SQLite registration < 1s.

**Constraints**:
- SC-004/SC-005 CHECK constraints on `energy_systems` table BLOCK insertion of non-viable designs (by design — prevents invalid data, but requires iterative solving)
- All scripts currently return exit code 127 (Python interpreter not in PATH) — root cause must be diagnosed and fixed before execution
- No CI/CD pipeline — manual execution and verification
- DB populated by unknown method (scripts never ran) — regeneration from scripts required for VVV trust

**Scale/Scope**: 5-20 kW turbine sweep (3-5 candidate sizes × 2 topologies = 6-10 configurations), 1 community (Assentamento Sertao Sustentavel, 38 kWh/day), single-site wind resource

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Gate | Status | Evidence |
|------|--------|----------|
| SPECIFY → HUMAN_GATE | ✅ PASS | spec-002 drafted, clarified, user-approved priority refocus documented in spec `## Clarifications` |
| MAD (research output) | ⏳ PENDING | research.md generated below — awaiting human_approved_plan |
| EXECUTE gate | ❌ BLOCKED | Requires `human_approved_plan = true` per Constitution v2.6 |
| DONE gate | ❌ BLOCKED | Requires Definition of Done + atomic commit per Constitution v2.6 |

**Constitution v2.6 Requirements Met**:
- [x] SPECIFY completed → HUMAN_GATE passed (user approved priority refocus on 2026-06-13)
- [ ] MAD ready for HUMAN_GATE review (this plan is the input)
- [ ] EXECUTE requires `human_approved_plan = true` — plan must be explicitly approved
- [ ] DONE requires Definition of Done + atomic commit — tracked at completion

## Project Structure

### Documentation (this feature)

```text
specs/002-turbine-upscaling/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output — cost scaling, topology decision, Q4 analysis
├── data-model.md        # Phase 1 output — entities, attributes, relationships
├── quickstart.md        # Phase 1 output — validation scenarios, walkthrough
├── contracts/           # Phase 1 output — interface contracts
└── tasks.md             # Phase 2 output (/speckit-tasks command)
```

### Source Code (repository root)

```text
src/
├── 01-material-characterization/   # PART 1 — Material modeling (PRIMARY scope)
│   ├── coating/
│   ├── mechanical/
│   ├── microstructure/
│   └── sensitivity/
├── 02-wind-energy/                 # PART 2 — Turbine upscaling (THIS ITERATION)
│   ├── aerodynamics/               #   wind_resource.py, power curves
│   ├── energy-system/              #   sizing_lcoe.py, system_sizing.py, register_energy_system.py
│   ├── structural/                 #   blade_cost_estimate.py, blade_design
│   └── comparison/                 #   VAWT vs HAWT comparison
├── 03-data-management/            # Database operations
├── common/                        # Shared utilities (unit conversions, Weibull, DB helpers)
└── visualization/                 # Plotting utilities

tests/
├── validation/                    # run_all_checks.sh, constraint tests, PQMS tests
│   ├── run_all_checks.sh          # 28-check validation suite
│   ├── test_constraints.py        # SC CHECK constraint tests
│   └── test_pqms.py               # PQMS scoring tests
├── mesh-convergence/              # Mesh convergence studies
└── reproducibility/               # Reproducibility checks

data/
└── bioeolica.db                   # SQLite single source of truth

knowledge/                         # RAG knowledge base
├── wind-energy/                   # Wind energy references
└── materials/                     # Material science references
```

**Structure Decision**: Single-project layout matching existing repository structure. Domain-organized modules under `src/` mirror the 10 engineering domains from the project constitution. Validation tests are separate from unit tests to match the existing `run_all_checks.sh` pattern.

## Complexity Tracking

> Constitution Check has no violations — single project, direct DB access via SQLite, no repository pattern. Complexity tracking not required.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |
