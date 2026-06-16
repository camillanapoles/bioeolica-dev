# CAD/CAE Platform — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement plan task-by-task.

**Goal:** Transform Physics M³ Workspace into an interactive CAD/CAE design and analysis platform supporting arbitrary geometries, FEM simulation, and parametric engineering calculations.

**Architecture:** 4 sequential cycles, each adding a critical capability: (1) FreeCAD integration for parametric 3D modeling, (2) Gmsh meshing for arbitrary geometries, (3) CalculiX solver bridge for full FEM, (4) Streamlit parametric UI for interactive use. Each cycle is independently deliverable and testable.

**Tech Stack:** Python + NumPy/SciPy + FreeCAD Python API + Gmsh Python API + CalculiX (`ccx`) CLI + Streamlit + VTK (ParaView export)

## FDC-U Scoring — Cycles Prioritization

| # | Ciclo | Descrição | Score FDC-U | Dependência | Esforço |
|---|-------|-----------|-------------|-------------|---------|
| C1 | **FreeCAD Bridge** | Modelagem paramétrica 3D via FreeCAD Python | **0.72** | Nenhuma (módulo novo) | 5 dias |
| C2 | **Gmsh Meshing** | Malha triangular/tetraédrica de geometrias STEP | **0.65** | C1 (entrada STEP) | 4 dias |
| C3 | **CalculiX Solver** | FEM em malhas arbitrárias via CalculiX | **0.68** | C1 + C2 | 5 dias |
| C4 | **Streamlit UI** | Interface paramétrica interativa completa | **0.58** | C1 + C2 + C3 | 3 dias |
| C5 | **VTK/ParaView** | Pós-processo e visualização FEM | **0.55** | C3 | 2 dias |
| C6 | **Otimização paramétrica** | TopOpt + DOE em geometrias arbitrárias | **0.52** | C1-C4 | 4 dias |

**FDC-U Justificativa:** C1 (FreeCAD) tem maior score por ser o gateway — sem geometria paramétrica, os demais ciclos não têm entrada. C3 (CalculiX) tem score alto por ser o motor FEM que desbloqueia análises reais.

---

## File Structure

```
workspaces/cad-cae-platform/
├── modules/                     ← All CAD/CAE modules
│   ├── freecad_bridge.py       ← C1: FreeCAD integration
│   ├── gmsh_mesher.py          ← C2: Gmsh meshing
│   ├── calculix_solver.py      ← C3: CalculiX FEM
│   ├── parametric_ui.py        ← C4: Streamlit UI
│   ├── vtk_export.py           ← C5: VTK/ParaView
│   └── design_optimizer.py     ← C6: Parametric optimization
├── tests/                      ← Per-module tests
├── examples/                   ← Example designs
│   ├── beam.py
│   ├── bracket.py
│   └── wind_blade.py
└── data/                       ← STEP files, results
```

---

## Cycle C1 — FreeCAD Bridge (Score: 0.72)

**Goal:** Enable parametric 3D modeling of arbitrary geometries via FreeCAD Python API.

**Dependencies:** FreeCAD installed (`apt install freecad`), `python -c "import FreeCAD"` succeeds.

### Files
- Create: `modules/freecad_bridge.py`
- Create: `tests/test_freecad_bridge.py`
- Test: Integration checking STEP/STL export

### Tasks
- [ ] T001 Verify FreeCAD Python API availability
- [ ] T002 Create `freecad_bridge.py` — `ParametricModel` class with:
  - `extrude_sketch(sketch_points, height)` — 2D sketch → 3D solid
  - `revolve(profile, axis, angle)` — revolved solid
  - `boolean_union(a, b)` / `boolean_cut(a, b)` — CSG operations
  - `fillet(edge, radius)` / `chamfer(edge, distance)` — edge treatments
  - `export_step(filepath)` — STEP export
  - `export_stl(filepath)` — STL export for meshing
- [ ] T003 Create `tests/test_freecad_bridge.py` — tests per method
- [ ] T004 Validate: export simple beam to STEP, confirm file size > 0
- [ ] T005 Commit

---

## Cycle C2 — Gmsh Mesher (Score: 0.65)

**Goal:** Generate quality tetrahedral/hexahedral meshes from STEP geometries.

**Dependencies:** `pip install gmsh`

### Files
- Create: `modules/gmsh_mesher.py`
- Create: `tests/test_gmsh_mesher.py`

### Tasks
- [ ] T006 Verify Gmsh Python API availability
- [ ] T007 Create `gmsh_mesher.py`:
  - `MeshGenerator.import_step(filepath)` — load STEP
  - `.set_element_size(min_size, max_size)` — mesh size control
  - `.generate_volume_mesh()` — tetrahedral mesh
  - `.generate_surface_mesh()` — triangular surface mesh
  - `.apply_boundary_condition(face_ids, type, value)` — BC tagging
  - `.export_msh(filepath)` — CalculiX-compatible .msh export
  - `.plot()` — matplotlib visualization of mesh
- [ ] T008 Create tests: mesh quality, element count, BC tagging
- [ ] T009 Validate: beam STEP → tetrahedral mesh → .msh file
- [ ] T010 Commit

---

## Cycle C3 — CalculiX Solver (Score: 0.68)

**Goal:** Full FEM on arbitrary meshes via CalculiX `ccx` CLI.

**Dependencies:** `apt install calculix-ccx calculix-ccx-doc`

### Files
- Create: `modules/calculix_solver.py`
- Create: `tests/test_calculix_solver.py`

### Tasks
- [ ] T011 Verify `ccx` CLI availability
- [ ] T012 Create `calculix_solver.py`:
  - `FEMSolver(msh_path, material, bc)` — input setup
  - `.set_material(E, nu, rho)` — isotropic material
  - `.add_fixed_support(face_id)` — encastre
  - `.add_pressure(face_id, value)` — pressure load
  - `.add_force(node_set, fx, fy, fz)` — point load
  - `.solve_static()` — run `ccx` and parse .dat/.frd
  - `.solve_modal(n_modes=10)` — eigenvalue extraction
  - `.solve_buckling(n_modes=5)` — linear buckling
  - `.export_vtk(filepath)` — VTK for ParaView
  - `.max_stress`, `.max_displacement`, `.strain_energy` — results
- [ ] T013 Create tests: cantilever beam validation
- [ ] T014 Validate: cantilever FEM vs analytical δ = PL³/(3EI)
- [ ] T015 Commit

---

## Cycle C4 — Streamlit Parametric UI (Score: 0.58)

**Goal:** Interactive web UI for parametric design, meshing, solving, and visualization.

**Dependencies:** `pip install streamlit plotly vtk`

### Files
- Create: `app/cad_cae_app.py`
- Create: `app/requirements.txt`

### Tasks
- [ ] T016 Create `cad_cae_app.py` with pages:
  - **Design page**: sliders for beam length/width/height, bracket dimensions, blade parameters → real-time FreeCAD geometry preview (matplotlib screenshot)
  - **Mesh page**: element size slider → Gmsh mesh visualization
  - **Solve page**: load/boundary condition selectors → CalculiX solve → VTK result display
  - **Optimize page**: objective selection → parametric DOE → Pareto visualization
  - **Export page**: download STEP, STL, MSH, VTK
- [ ] T017 Create tests: page structure, import verification, section presence
- [ ] T018 Validate: `streamlit run app/cad_cae_app.py` launches without error
- [ ] T019 Commit

---

## Cycle C5 — VTK/ParaView Export (Score: 0.55)

**Goal:** Professional FEM visualization via VTK file format for ParaView.

**Dependencies:** `pip install vtk`

### Files
- Modify: `modules/calculix_solver.py` (add VTK export)
- Create: `modules/vtk_export.py`
- Create: `tests/test_vtk_export.py`

### Tasks
- [ ] T020 Create `vtk_export.py`:
  - `VtkWriter.write_unstructured_grid(nodes, elements, results, filepath)`
  - Supports: displacement, stress, strain, modal shapes
  - Writes .vtu format (XML VTK Unstructured Grid)
- [ ] T021 Integrate with CalculiX solver
- [ ] T022 Create tests: file validity, ParaView-readable format
- [ ] T023 Validate: open in ParaView, verify field data
- [ ] T024 Commit

---

## Cycle C6 — Design Optimization (Score: 0.52)

**Goal:** Parametric design optimization (DOE + TopOpt) in arbitrary geometries.

**Dependencies:** C1-C4

### Files
- Create: `modules/design_optimizer.py`
- Create: `tests/test_design_optimizer.py`

### Tasks
- [ ] T025 Create `design_optimizer.py`:
  - `ParametricStudy(geometry_func, params, ranges)` — sweep definition
  - `.run_doe(method='full_factorial')` — design of experiments
  - `.pareto_frontier(objectives)` — multi-objective trade-off
  - `.sensitivity_analysis()` — Morris/Sobol on design params
  - `.optimize(objective, constraints)` — scipy optimization loop
  - `.plot_pareto()` — 2D/3D Pareto visualization
- [ ] T026 Integrate with FreeCAD + CalculiX pipeline
- [ ] T027 Create tests: DOE sweep, Pareto, sensitivity
- [ ] T028 Validate: optimize beam mass vs stiffness
- [ ] T029 Commit

---

## Execution Order

```
  C1 → C2 → C3 → C4 → C5 → C6
   │     │     │     │     │     └── Otimização paramétrica
   │     │     │     │     └──────── VTK/ParaView
   │     │     │     └────────────── Streamlit UI
   │     │     └──────────────────── CalculiX FEM
   │     └────────────────────────── Gmsh mesh
   └──────────────────────────────── FreeCAD bridge
```

**Dependency rules:**
- C2 (Gmsh) requer C1 (FreeCAD) para STEP import
- C3 (CalculiX) requer C2 para .msh mesh input
- C4 (UI) integra C1+C2+C3
- C5 (VTK) integra C3
- C6 (Optim) integra C1-C4

**Independent sub-task rule:** Tasks within the same cycle that touch different files can run in parallel.

---

## MANDATOS DE EXECUÇÃO

### M0 — GitNexus
- `node .gitnexus/run.cjs analyze` ANTES de cada cycle

### M1 — Sucesso por Task
- Código executado + teste passado = ✅
- NUNCA avançar com falha

### M2 — Uma Task Por Vez
- Sequencial: T001 → T002 → T003...
- Nunca pular sequência
- Cada task depende do sucesso da anterior

### M3 — Reimplementar, Não Verificar
- Gerar código + pytest equivalente
- Teste passando = única métrica

### M4 — Sincronização
- Commit + push após cada task
- Atualizar tasks.md

## Scoring Rationale (FDC-U)

| Critério | Peso | Justificativa |
|----------|------|---------------|
| Dependências (desbloqueia outros) | 35% | C1 gateway para todo o pipeline |
| Valor entregue ao usuário | 25% | C3 (FEM real) > C4 (UI) > C2 (mesh) |
| Esforço (inverso) | 20% | C4 (3d) < C5 (2d) < C2 (4d) |
| Risco técnico (inverso) | 10% | C1 (FreeCAD API) > C3 (`ccx` parse) |
| Manutenibilidade | 10% | C1 (API estável) > C3 (formato texto) |

## Self-Review Checklist

- [ ] All 6 cycles have clear, independent deliverables
- [ ] No placeholder code in any task
- [ ] Test files specified for every module
- [ ] File paths are exact
- [ ] Dependency graph is acyclic
- [ ] Each task produces working, testable software

