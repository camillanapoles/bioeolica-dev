# M³-KDI Integration — Implementation Plan

**Goal:** Integrate the CAD/CAE platform with the KDI M³ (Macro-Meso-Micro) analysis framework from physics-m3, enabling multi-scale engineering calculations across all 10 KDI domains.

**Architecture:** Bridge the CAD parametric geometry + FEM pipeline with the M³ analytical modules. Each cycle adds one integration layer: Macro (system-level), Meso (interface-level), Micro (material-level), plus cross-domain coupling.

**Tech Stack:** Python + CadQuery + Gmsh + CalculiX + NumPy/SciPy + Matplotlib + VTK

---

## FDC-U Scoring — Integration Cycles

| # | Ciclo | Descrição | Score FDC-U | Dependência |
|---|-------|-----------|-------------|-------------|
| C7 | **KDI Macro Bridge** | Macro-scale: loads, BCs, system-level M³ from CAD geometry | **0.74** | C1-C6 + physics-m3/m3_analysis |
| C8 | **KDI Meso Bridge** | Meso-scale: interfaces, stress concentrations, joints from FEM | **0.68** | C7 |
| C9 | **KDI Micro Bridge** | Micro-scale: materials, composites, crystallography from CAD params | **0.65** | C7 |
| C10 | **KDI Multi-Physics** | Multi-physics: fluid-thermal-structural coupling | **0.58** | C7-C9 |
| C11 | **KDI VVV Pipeline** | Unified VVV: validate M³ results across macro-meso-micro | **0.55** | C7-C10 |
| C12 | **KDI Dashboard** | Streamlit M³ dashboard: Macro→Meso→Micro drill-down | **0.52** | C7-C11 |

**FDC-U Justificativa:** C7 (Macro Bridge) has the highest score because it's the gateway — without macro-level geometry→M³ mapping, meso and micro cannot be fed. C8/C9 are tied at similar scores because they are independent but both depend on C7.

---

## File Structure

```
workspaces/kdi-m3-bridge/
├── modules/
│   ├── kdi_macro.py          ← C7: Macro-scale KDI linkage
│   ├── kdi_meso.py           ← C8: Meso-scale KDI linkage
│   ├── kdi_micro.py          ← C9: Micro-scale KDI linkage
│   ├── kdi_multiphysics.py   ← C10: Multi-physics coupling
│   ├── kdi_vvv.py            ← C11: VVV validation pipeline
│   └── kdi_dashboard.py      ← C12: Streamlit dashboard
├── tests/
│   └── test_kdi_*.py
└── examples/
    └── wind_blade_m3.py      ← End-to-end M³ example
```

---

## Cycle C7 — KDI Macro Bridge (Score: 0.74)

**Goal:** Import CAD geometry parameters → instantiate Macro-scale M³ analysis (wind, loads, environment, global BCs).

### Files
- Create: `modules/kdi_macro.py`
- Create: `tests/test_kdi_macro.py`
- Modify: `app/app.py` (add KDI tab)

### Tasks
- [ ] T001 Extract macro-scale parameters from CadModel bounding box + material
- [ ] T002 Map to MacroScale(altitude_m, wind_speed_ms, density_air) from m3_analysis
- [ ] T003 Create `MacroAnalysis` class: `from_cad(cad_model, location, wind_class)`, `run()`, `report()`
- [ ] T004 Link global forces from macro → CalculiX BC inputs
- [ ] T005 Create tests: import, from_cad, run, report
- [ ] T006 Validate: cantilever beam → MacroScale → compare analytical
- [ ] T007 Commit

### KDI Macro Details (from INSTRUCTIONS.md)
```
Macro = ambiente externo:
  - Fronteiras externas (bounding box, supports)
  - Condições de contorno globais (wind, pressure, temperature)
  - Stakeholders / regulamentação (normas ISO, IEC)
  - Cargas ambientais (vento, onda, corrente)
```

---

## Cycle C8 — KDI Meso Bridge (Score: 0.68)

**Goal:** Map FEM results (stress, strain, displacement) → Meso-scale interface analysis (joints, connections, stress concentrations).

### Files
- Create: `modules/kdi_meso.py`
- Create: `tests/test_kdi_meso.py`

### Tasks
- [ ] T008 Read CalculiX .dat result → extract nodal stresses at interfaces
- [ ] T009 Map stress concentrations (Kt) from FEM → Tsai-Wu / von Mises at joint level
- [ ] T010 Create `MesoAnalysis` class: `from_fem_results(fem_solver)`, `run()`, `report()`
- [ ] T011 Create tests: Kt extraction, stress concentration, interface stress
- [ ] T012 Validate: plate with hole FEM → Kt ≈ 3.0 (Kirsch)
- [ ] T013 Commit

### KDI Meso Details (from INSTRUCTIONS.md)
```
Meso = fronteira + interface:
  - Interfaces físicas (juntas, soldas, contato)
  - Acoplamentos (térmico, mecânico, elétrico)
  - Concentração de tensão em entalhes/furos
  - Distribuição de carga entre subsistemas
```

---

## Cycle C9 — KDI Micro Bridge (Score: 0.65)

**Goal:** Link CAD material selection → Micro-scale material analysis (composites, crystallography, damage).

### Files
- Create: `modules/kdi_micro.py`
- Create: `tests/test_kdi_micro.py`

### Tasks
- [ ] T014 Import material parameters from composite_model + crystal_lattice
- [ ] T015 Map CAD material selection → CompositeMaterial E1, E2, G12, nu12
- [ ] T016 Create `MicroAnalysis` class: `from_material(material_name, params)`, `run()`, `report()`
- [ ] T017 Link micro-scale properties → FEM material input (homogenized)
- [ ] T018 Create tests: material mapping, homogenization, failure envelope
- [ ] T019 Validate: waste paper/PVA composite → FEM beam → compare analytical
- [ ] T020 Commit

### KDI Micro Details (from INSTRUCTIONS.md)
```
Micro = interior, componentes:
  - Propriedades materiais (E, nu, rho — homogeneizadas)
  - Microestrutura (fibra, matriz, grafite)
  - Modelos de falha (Tsai-Wu, von Mises, Tresca)
  - Fadiga, creep, dano iniciação
```

---

## Cycle C10 — KDI Multi-Physics (Score: 0.58)

**Goal:** Couple fluid (CFD) + thermal + structural analyses across M³ scales.

### Files
- Create: `modules/kdi_multiphysics.py`
- Create: `tests/test_kdi_multiphysics.py`

### Tasks
- [ ] T021 Import cfd_solver + thermodynamics + electromechanical results
- [ ] T022 Create `MultiPhysicsCoupling` class: fluid→structure, thermal→stress
- [ ] T023 Map fluid pressure → FEM structural load (FSI chain)
- [ ] T024 Map thermal gradient → FEM thermal strain
- [ ] T025 Create tests: FSI coupling, thermal-structural, convergence
- [ ] T026 Validate: CFD pressure on beam → FEM → coupled deformation
- [ ] T027 Commit

---

## Cycle C11 — KDI VVV Pipeline (Score: 0.55)

**Goal:** Unified VVV certification across macro-meso-micro with quantitative gates.

### Files
- Create: `modules/kdi_vvv.py`
- Create: `tests/test_kdi_vvv.py`

### Tasks
- [ ] T028 Create `VVVMultiScale` class: aggregate macro + meso + micro metrics
- [ ] T029 Define certification gates per scale (from vvv_protocol + INSTRUCTIONS.md)
- [ ] T030 Run cross-code validation: FEM analytical benchmark vs CalculiX
- [ ] T031 Generate VVV report with PASS/FAIL per scale
- [ ] T032 Create tests: certification, cross-code, benchmark
- [ ] T033 Validate: cantilever analytical vs FEM → error < 5%
- [ ] T034 Commit

---

## Cycle C12 — KDI Dashboard (Score: 0.52)

**Goal:** Streamlit dashboard with M³ drill-down: Macro→Meso→Micro results.

### Files
- Create: `app/kdi_dashboard.py`
- Create: `tests/test_kdi_dashboard.py`

### Tasks
- [ ] T035 Create 3-tier dashboard: Macro (system), Meso (interface), Micro (material)
- [ ] T036 Add VVV certification status per scale
- [ ] T037 Add export: full M³ report (PDF/JSON)
- [ ] T038 Integrate with existing CAD/CAE `app/app.py`
- [ ] T039 Create tests: page structure, import, section presence
- [ ] T040 Validate: `streamlit run app/kdi_dashboard.py` launches
- [ ] T041 Commit

---

## Execution Order

```
C7  → C8  → C9  → C10  → C11  → C12
 │     │      │       │       │       └── KDI Dashboard
 │     │      │       │       └────────── VVV Multi-Scale
 │     │      │       └────────────────── Multi-Physics
 │     │      └────────────────────────── Micro Bridge
 │     └───────────────────────────────── Meso Bridge
 └─────────────────────────────────────── Macro Bridge (GATEWAY)
```

---

## MANDATOS DE EXECUÇÃO (from INSTRUCTIONS.md)

### M0 — GitNexus
- `node .gitnexus/run.cjs analyze` ANTES de cada cycle

### M1 — Sucesso por Task
- Código executado + teste passado = ✅
- **NUNCA** avançar com falha

### M2 — Uma Task Por Vez
- Sequencial: C7→C8→C9→C10→C11→C12
- Cada task depende do sucesso da anterior

### M3 — Reimplementar, Não Verificar
- Gerar código + pytest
- Teste passando = única métrica

### M4 — Sincronização
- Commit + push após cada task
- Atualizar tasks.md

---

## Self-Review Checklist

- [ ] All 6 cycles map to KDI M³ scales (macro, meso, micro)
- [ ] C7 (Macro Bridge) is gateway — all others depend on it
- [ ] Each cycle references INSTRUCTIONS.md KDI domain descriptions
- [ ] Test files specified for every module
- [ ] File paths are exact
- [ ] No placeholder code in any task
- [ ] Dependency graph is acyclic
