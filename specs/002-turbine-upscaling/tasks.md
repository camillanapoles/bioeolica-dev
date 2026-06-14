# Tasks: Turbine Upscaling for Economic Viability

**Input**: Design documents from `specs/002-turbine-upscaling/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- All paths reference existing repo structure

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Enable Python execution and establish project structure

- [ ] T001 Diagnose and fix Python interpreter PATH issue (exit code 127 on all .py scripts) — verify with `python3 --version` and running a minimal script
- [ ] T002 Create/verify project subdirectories: `src/02-wind-energy/comparison/`, `src/common/`, `knowledge/wind-energy/`

**Checkpoint**: Python executes without exit 127, directory structure exists

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T003 [P] Create shared DB helper module in `src/common/db_helper.py` — connection management, query helpers, table metadata for `community_profiles`, `wind_turbine_systems`, `energy_systems`, `blade_designs`
- [ ] T004 [P] Create shared wind utilities module in `src/common/wind_utils.py` — Weibull distribution functions, air density correction, power curve helpers matching contracts/wind-resource.md
- [ ] T005 Verify bioeolica.db baseline state — query community_profile (Assentamento Sertao Sustentavel, 38 kWh/day baseline), wind_turbine_systems (0.82 kW VAWT), energy_systems (0 rows), document via `sqlite3 data/bioeolica.db "SELECT ..."`

**Checkpoint**: Foundation ready — user story implementation can now begin in parallel

---

## Phase 3: User Story 1 — Upscaled Turbine System Design (Priority: P1) 🎯 MVP

**Goal**: Design an upscaled wind turbine (10-15 kW range) that meets economic viability targets (LCOE < $0.15/kWh, cost < $3,000/kW) and community demand coverage (>= 100% of 38 kWh/day). Compare VAWT H-rotor Darrieus vs HAWT Archimedes across 5-20 kW range.

**Independent Test**: Compute economic metrics (LCOE, cost/kW, demand coverage) for candidate turbine configurations against SC-004/SC-005 targets. Passing all 4 economic checks = successful iteration.

### Implementation for User Story 1

- [ ] T006 [P] [US1] Implement `compute_cost_breakdown()` per contracts/cost-model.md in `src/02-wind-energy/energy-system/cost_breakdown.py` — decompose cost into rotor ($/kg ∝ D³), generator ($4,268×P^0.75), tower ($/m), battery ($200/kWh × kWh_nominal), fixed costs (controller $2,500, inverter $2,000, transport $1,500 base, installation $2,427)
- [ ] T007 [P] [US1] Implement `compute_aep()` per contracts/cost-model.md in `src/02-wind-energy/aerodynamics/aep_model.py` — Weibull distribution (k=2.0, c=6.21), power curve integration, capacity factor output. Use `wind_resource.py` pattern if diagnosable, otherwise clean reimplementation
- [ ] T008 [US1] Implement `compute_lcoe()` per contracts/cost-model.md in `src/02-wind-energy/energy-system/lcoe_model.py` — CRF calculation (8% discount, 20yr lifetime), O&M at 2% of CAPEX, output LCOE per kWh
- [ ] T009 [US1] Run multi-configuration sweep (5, 10, 12, 15, 20 kW × VAWT + HAWT) using cost_breakdown + aep_model + lcoe_model — output cost/kW, LCOE, demand coverage per configuration. Save results to `data/upscaling_results.json`
- [ ] T010 [US1] Generate topology comparison report in `knowledge/wind-energy/topology_recommendation.md` — quantitative comparison at 10 kW (VAWT: $8,100/kW, CF 19%, LCOE $0.28 vs HAWT: $8,900/kW, CF 24%, LCOE $0.26) with community manufacturing feasibility rationale per research.md Section 4.3

**Checkpoint**: At this point, User Story 1 should be fully functional — cost/AEP/LCOE computed for all configurations, topology recommendation documented

---

## Phase 4: User Story 2 — Manufacturing Cost Model (Priority: P1)

**Goal**: Develop bottom-up cost model explaining why 0.82 kW prototype costs $48,204/kW and identifying scale/choices to reach $3,000/kW target. Validate scaling component vs fixed cost decomposition.

**Independent Test**: Decompose cost into scaling vs fixed components and verify model predicts costs within ±20% for at least 3 turbine sizes.

### Implementation for User Story 2

- [ ] T011 [P] [US2] Implement BOM cost decomposition in `src/02-wind-energy/energy-system/bom_cost_model.py` — itemized bill-of-materials for 0.82 kW baseline (rotor $3,200, generator $3,500, tower $4,500, battery $19,000, controller $2,500, inverter $2,000, transport $2,400, installation $2,427), parametric scaling laws for each component, validation against baseline with error < 20%
- [ ] T012 [US2] Run sensitivity analysis on cost drivers in `src/02-wind-energy/energy-system/sensitivity_cost.py` — vary tower height (±25%), generator type (PM vs induction), battery capacity (1-3 days), transport distance (100-500 km). Identify dominant cost drivers and elasticities at 10 kW reference size
- [ ] T013 [US2] Document cost findings in `knowledge/wind-energy/cost_model_report.md` — minimum viable turbine size, cost elasticities, battery dominance analysis (48.1% of total), pathway assessment: pure upscaling insufficient ($6,016/kW at 20 kW, still 2× target), recommend relaxed targets for community-scale

**Checkpoint**: Cost model validated against baseline, sensitivity documented, minimum viable size identified

---

## Phase 5: User Story 3 — Integrated Energy System Registration (Priority: P2)

**Goal**: Register the final upscaled turbine + storage energy system in `energy_systems` table, ensure SC-004/SC-005 CHECK constraints pass, and update validation record so all 28 checks report correctly.

**Independent Test**: Run `run_all_checks.sh` and confirm 28/28 PASS with the new energy system.

### Implementation for User Story 3

- [ ] T014 [P] [US3] Implement `size_battery()` per contracts/cost-model.md in `src/02-wind-energy/energy-system/battery_sizing.py` — nominal kWh = (daily_demand × autonomy_days) / (DoD × RTE), for 45.6 kWh/day design demand: 95 kWh nominal at 80% DoD, 85% RTE. Output battery_kwh_nominal, battery_cost_usd, autonomy_days_actual
- [ ] T015 [US3] Implement `register_energy_system()` per contracts/energy-system-registration.md in `src/02-wind-energy/energy-system/register_system.py` — INSERT into `energy_systems` table with CHECK constraint handling (SC-004: LCOE < 0.15, cost/kW < 3000; SC-005: demand_coverage >= 100, autonomy >= 2.0, CF >= 20). Capture check_results dict and insert_success bool. Log CHECK_CONSTRAINT_VIOLATION if any check fails
- [ ] T016 [US3] Fix SC-004/SC-005 zero-row visibility bug in validation views — replace INNER JOIN with LEFT JOIN or add COALESCE in the validation view query so empty `energy_systems` table shows SC-004/SC-005 as FAIL (not silently absent from output). Per research.md Section 7, the regex `[1-9][0-9]*` doesn't match 0 rows
- [ ] T017 [US3] Run `run_all_checks.sh` and verify output — confirm all 28 checks present (none silently missing), SC-004 and SC-005 rows visible regardless of PASS/FAIL. Document current 24/28 baseline vs post-registration result

**Checkpoint**: Energy system registered (or CHECK constraints blocking explicitly documented), validation runner shows 28/28 complete report

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T018 [P] Document all cost model assumptions, scaling factors, source references, and uncertainty ranges in `knowledge/wind-energy/assumptions.md` — includes wind resource parameters, battery costs ($200/kWh LiFePO4), discount rate (8%), project lifetime (20yr), O&M (2%), transport costs ($0.50/kg/km), composite blade cost ($15/kg)
- [ ] T019 Git checkpoint — commit all verified changes across phases 1-5 with atomic commits: one commit per phase, each with documented output verification
- [ ] T020 Run quickstart.md end-to-end validation — execute Steps 1-7 from `specs/002-turbine-upscaling/quickstart.md`, verify all checkboxes, report final status for each acceptance criterion (FR-001 through FR-008)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - US1 (P1) and US2 (P1) can proceed in parallel after Phase 2
  - US3 (P2) depends on US1 completion (needs turbine metrics for registration)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational — No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational — Independent of US1 (uses same cost data but different analysis perspective)
- **User Story 3 (P2)**: Depends on US1 (needs computed turbine metrics) + US2 (needs validated cost model)

### Within Each User Story

- Models before sweep/analysis
- Analysis before documentation
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- T003 and T004 (Foundational DB helpers + wind utils) can run in parallel
- T006, T007 (US1 cost breakdown + AEP model) can run in parallel
- T006 (US1 cost) and T011 (US2 BOM cost) use different decomposition granularity — same data, independent models
- T014 (US3 battery sizing) depends on demand profile from Phase 2 (T005), can start early in Phase 5
- T010 (topology report) and T013 (cost report) are documentation tasks that can run after their respective analyses

---

## Parallel Example: Phase 2 Foundational

```bash
# Launch DB helpers and wind utils in parallel:
Task: "Create DB helper module in src/common/db_helper.py"
Task: "Create wind utilities module in src/common/wind_utils.py"
```

## Parallel Example: Phase 3 User Story 1

```bash
# Launch cost breakdown and AEP model in parallel:
Task: "Implement compute_cost_breakdown in cost_breakdown.py"
Task: "Implement compute_aep in aep_model.py"

# After both complete: implement LCOE (depends on both)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup — fix Python, create directories
2. Complete Phase 2: Foundational — DB helpers, wind utils, baseline verification
3. Complete Phase 3: User Story 1 — cost model, AEP, LCOE, topology comparison
4. **STOP and VALIDATE**: Run cost projections against research.md expected values ($6,855/kW at 15 kW, $0.24/kWh LCOE)
5. Present findings: $3,000/kW and $0.15/kWh targets unreachable; recommend relaxed targets

### Incremental Delivery

1. Setup + Foundational → Python works, infrastructure ready
2. US1 → Cost/AEP/LCOE computed, topology selected, MVP achieved
3. US2 → Manufacturing cost validated, sensitivity documented
4. US3 → Energy system registered, validation runner shows 28/28 complete

### Key Risk: Unreachable Targets

Research.md conclusively shows $3,000/kW and $0.15/kWh targets cannot be met in 5-20 kW range. The execution strategy must:
- Document actual achievable values ($6,855/kW, $0.24/kWh at 15 kW)
- Present sensitivity analysis showing relaxed targets ($6,000/kW, $0.25/kWh)
- Flag that CHECK constraints on `energy_systems` will BLOCK insertion at current SC-004/SC-005 thresholds
- The validation view fix (T016) ensures SC-004/SC-005 show as FAIL instead of vanishing — this is critical for honest reporting

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each phase or logical group
- Stop at any checkpoint to validate story independently
- Existing scripts (`sizing_lcoe.py`, `register_energy_system.py`, `wind_resource.py`) have NEVER been executed (exit 127). T001 must diagnose root cause before any task execution.
- The SC-004/SC-005 zero-row bug in validation views (T016) is critical — without it, failing checks vanish silently from output
