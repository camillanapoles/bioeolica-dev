---

description: "Task list for Spec 008 Fase 0 — Fundação Mantável (C7 + C3)"
---

# Tasks: 008 Evolution Priorities — Fase 0

**Input**: Design documents from `specs/008-evolution-priorities-fdc-u/`

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Scaffold scripts and audit tools needed by all Fase 0 work

- [X] T001 Create `scripts/migrate_unify_db.py` skeleton with argparse (--dry-run, --backup-dir, --force)
- [X] T002 [P] Create `scripts/audit_deps.py` skeleton with argparse (--check, --freeze)
- [X] T003 [P] Create `reports/` directory for VVV and migration reports

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: DB canonicalization + pyproject.toml dependency audit — MUST complete before user story work

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Implement `scripts/migrate_unify_db.py` — auto-detect orphan DBs (`./bioeolica.db`, `data/database.db`), backup to `data/backup/`, attach and merge into `data/bioeolica.db`
- [X] T005 [P] Implement conflict resolution in `scripts/migrate_unify_db.py` — timestamp-based `INSERT OR REPLACE`, log conflicts to stdout in dry-run
- [X] T006 [P] Implement `scripts/audit_deps.py` — scan all `.py` files in `src/`, `cad/`, `scripts/`, `tests/` for `import` statements
- [X] T007 Implement pyproject.toml dependency generation — write `[project.dependencies]` and `[project.optional-dependencies]` from audit results
- [X] T008 [P] Implement post-migration verification in `scripts/migrate_unify_db.py` — row count consistency, SHA-256 checksum
- [X] T009 [P] Implement `--restore` flag in `scripts/migrate_unify_db.py` for rollback from `data/backup/`
- [X] T010 [P] Add entry_points to `pyproject.toml` for CLI scripts

**Checkpoint**: Foundation ready — single DB at `data/bioeolica.db`, pyproject.toml with full dependency declarations

---

## Phase 3: User Story 1 — Spec 002 TopOpt Revision (Priority: P1) 🎯 MVP

**Goal**: Review and supplement spec 002 (topology optimization) for OpenMDAO/Dakota alignment

**Independent Test**: `python -c "from openmdao import core; print('openmdao OK')"` + `pytest tests/ -k "topopt" --co -q` discovers tests

### Implementation for User Story 1

- [X] T011 [US1] Rewrite `specs/002-topopt-avancada/spec.md` — scope to OpenMDAO/Dakota + CalculiX, remove non-topopt concepts
- [X] T012 [US1] Update `specs/002-topopt-avancada/plan.md` — add mesh convergence criteria (3 levels: 5k/15k/50k), sensitivity filter radius ≥ 1.5× element size
- [X] T013 [P] [US1] Add OpenMDAO TopOptGroup contract in `specs/002-topopt-avancada/contracts/openmdao_integration.md`
- [X] T014 [P] [US1] Add Dakota sensitivity analysis contract in `specs/002-topopt-avancada/contracts/dakota_sensitivity.md`
- [X] T015 [US1] Update `specs/002-topopt-avancada/tasks.md` — validate T001-T011 completion, add supplementary convergence tasks if gaps found
- [ ] T016 [US1] Run quickstart validation — `pytest tests/ -k "topopt" -v --tb=short`

**Checkpoint**: Spec 002 fully aligned with OpenMDAO/Dakota stack, mesh convergence criteria documented

---

## Phase 4: User Story 2 — Spec 006 Validação Experimental (Priority: P2)

**Goal**: Create spec 006 from scratch, mapping `tests/validation/` to formal VVV protocol

**Independent Test**: `ls tests/validation/` shows 6+ test files; `pytest tests/validation/ -v --tb=short` passes with ≥6 tests

### Implementation for User Story 2

- [X] T017 [US2] Create `specs/006-validacao-experimental/spec.md` — map each test file to validation_protocol, reference ASTM/ISO standards
- [X] T018 [US2] Create `specs/006-validacao-experimental/plan.md` — tech stack (pytest, junitxml), F1-F9 structure per KDI
- [X] T019 [US2] Create `specs/006-validacao-experimental/tasks.md` — sequential tasks mapping contracts→test→VVV report
- [X] T020 [P] [US2] Create `specs/006-validacao-experimental/contracts/hidrologia.md` — protocol for pressão + vazão, ASTM D reference, acceptance < 5% error
- [X] T021 [P] [US2] Create `specs/006-validacao-experimental/contracts/materiais.md` — protocol for tração (ASTM E8, < 3%), fadiga (ASTM E466, < 10%), dureza (ASTM E18, < 5%)
- [X] T022 [P] [US2] Create `specs/006-validacao-experimental/contracts/estrutural.md` — protocol for vibração (ISO 7626, < 8% modal error)
- [X] T023 [US2] Add VVV certification criteria to each protocol — 6 criteria: source ≥7/10, fair comparison, quantified error, operational coverage, reproducibility, peer review
- [ ] T024 [US2] Run quickstart validation — `pytest tests/validation/ -v --tb=short --junitxml=reports/vvv-006.xml`

**Checkpoint**: Spec 006 fully created with 3 contract protocols, 6 tests mapeados, VVV criteria documented

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Integration verification and cleanup

- [ ] T025 [P] Run `python scripts/migrate_unify_db.py --dry-run` and verify output
- [ ] T026 [P] Run `python scripts/audit_deps.py --check` and verify zero missing deps
- [ ] T027 Verify `data/bioeolica.db` is the only active database — remove or symlink orphans
- [ ] T028 [P] Remove stale `database.db` and `./bioeolica.db` if migration verified
- [ ] T029 Run full quickstart validation per `specs/008-evolution-priorities-fdc-u/quickstart.md`
- [ ] T030 Commit Fase 0 with message "008 Fase 0: DB unify + specs 002/006 revision"

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories
- **User Stories (Phases 3-4)**: Depend on Phase 2 completion
- **Polish (Phase 5)**: Depends on all phases complete

### User Story Dependencies

- **US1 (Spec 002, P1)**: Can start after Phase 2 — independent of US2
- **US2 (Spec 006, P2)**: Can start after Phase 2 — independent of US1

### Within Each User Story

- Contracts before spec/plan
- Spec before plan before tasks
- Validation after all implementation

### Parallel Opportunities

- T002 + T003: both scripts, no shared files
- T005 + T006: different scripts, independent logic
- T013 + T014: different contracts, independent
- T020 + T021 + T022: different contracts, independent
- T025 + T026: different scripts, independent
- T028 can run after T027 only

---

## Parallel Example: Phase 2

```bash
Task: "Implement conflict resolution in scripts/migrate_unify_db.py"
Task: "Implement scripts/audit_deps.py — scan all .py files for import statements"
```

## Parallel Example: Phase 3 (US1)

```bash
Task: "Add OpenMDAO TopOptGroup contract"
Task: "Add Dakota sensitivity analysis contract"
```

## Parallel Example: Phase 4 (US2)

```bash
Task: "Create contracts/hidrologia.md"
Task: "Create contracts/materiais.md"
Task: "Create contracts/estrutural.md"
```

---

## Implementation Strategy

### MVP (Phase 1 + Phase 2 + Phase 3 only)

1. Complete Setup: T001-T003
2. Complete Foundational: T004-T010
3. Complete US1 (Spec 002): T011-T016
4. **STOP and VALIDATE**: DB unified, pyproject deps populated, spec 002 reviewed

### Incremental Delivery

1. Phase 1 + Phase 2 → Foundation ready (single DB, full deps)
2. Add US1 → Spec 002 reviewed and aligned
3. Add US2 → Spec 006 created with VVV protocols
4. Phase 5 → Integration verified and committed

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story is independently testable
- Commit after each logical group
- Stop at any checkpoint to validate independently
- Fase 0 desbloqueia as Fases 1-4 do spec principal (C2, C8, C10, C1, C5, C4, C9, C6)
