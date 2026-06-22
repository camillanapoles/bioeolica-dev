---

description: "Task list for TopOpt Avançada — 3D SIMP topology optimization with multi-objective and additive manufacturing constraints"
---

# Tasks: TopOpt Avançada (FDC-U O1 Score: 0.715)

**Input**: FDC-U analysis identified O1 — TopOpt Avançada as best production route

**Prerequisites**: spec.md (001-physics-m3-workspace), existing 30 modules at instruments/physics-m3/

**Tests**: pytest — each task generates test file alongside module

## Format: `[ID] [P?] [Story] Description`

---

## Phase 1: Setup (Núcleo)

- [X] T001 Verificar workspace atual: 30 módulos, 295 testes — baseline OK
- [X] T002 Criar diretório `specs/002-topopt-avancada/` com spec, plan, tasks, contracts
- [X] T003 [P] Rodar GitNexus analyze para baseline de dependências

---

## Phase 2: TopOpt 3D SIMP Multi-Objetivo

**Goal**: Implementar otimização topológica 3D com SIMP, multi-objetivo (massa × rigidez × custo) e restrições de manufatura aditiva (overhang, suporte, anisotropia)

**Independent Test**: `pytest tests/test_topopt_avancada.py -v` — 0 falhas

- [X] T004 [P] Criar `modules/topopt_avancada.py` — SIMP 3D (extensão do topology_optimization existente)
- [X] T005 Criar `tests/test_topopt_avancada.py` — testes para SIMP 3D
- [X] T006 [P] Adicionar `modules/topopt_multiobj.py` — weighted-sum multi-objetivo (compliance + massa + custo)
- [X] T007 Criar `tests/test_topopt_multiobj.py` — testes multi-objetivo
- [X] T008 [P] Adicionar `modules/topopt_manufacturing.py` — restrições de manufatura (overhang angle, suporte mínimo, anisotropia do processo)
- [X] T009 Criar `tests/test_topopt_manufacturing.py` — testes de manufatura
- [X] T010 Integrar TopOpt Avançada no `demo_completa.py`
- [X] T011 Validar: `python validate_completo.py` — pipeline completo

**Checkpoint**: TopOpt 3D funcional, multi-objetivo validado, restrições de manufatura ativas

---

## Dependencies & Execution Order

- T001 → T002 → T003 (Setup)
- T004 → T005 (SIMP 3D)
- T006 → T007 (Multi-objetivo, paralelo a T004)
- T008 → T009 (Manufatura, paralelo a T004/T006)
- T010 → T011 (Integração, depende de T005+T007+T009)

### Parallel Opportunities

- T004/T006/T008 podem rodar em paralelo (diferentes módulos, sem dependência)
- T005/T007/T009 (testes dos módulos) podem rodar em paralelo
