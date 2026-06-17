---

description: "Task list for Spec 006 — Validação Experimental"
---

# Tasks: 006 Validação Experimental

## Phase 1: Contracts

- [ ] T001 [P] Create `specs/006-validacao-experimental/contracts/hidrologia.md`
- [ ] T002 [P] Create `specs/006-validacao-experimental/contracts/materiais.md`
- [ ] T003 [P] Create `specs/006-validacao-experimental/contracts/estrutural.md`

## Phase 2: VVV Implementation

- [ ] T004 Map `tests/validation/test_hidrologia_pressao.py` to validation protocol with ASTM D
- [ ] T005 [P] Map `tests/validation/test_hidrologia_vazao.py` to validation protocol
- [ ] T006 [P] Map `tests/validation/test_materiais_tracao.py` to protocol with ASTM E8
- [ ] T007 [P] Map `tests/validation/test_materiais_fadiga.py` to protocol with ASTM E466
- [ ] T008 [P] Map `tests/validation/test_materiais_dureza.py` to protocol with ASTM E18
- [ ] T009 [P] Map `tests/validation/test_estrutural_vibracao.py` to protocol with ISO 7626

## Phase 3: VVV Report

- [ ] T010 Add 6 certification criteria to each protocol
- [ ] T011 Run `pytest tests/validation/ -v --tb=short --junitxml=reports/vvv-006.xml`
- [ ] T012 Verify all 6 protocols PASS
