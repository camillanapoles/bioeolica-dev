# Plan: Physics M³ Workspace — Domain Expansion (Phase 2)

## Context

O workspace `physics-m3` (22 módulos, 152 testes, ~8.500 linhas) cobre 10 domínios KDI, mas faltam 8 domínios especializados identificados como gaps no último ciclo. O usuário solicita incrementar todos os domínios faltantes, seguindo obrigatoriamente o KDI/INSTRUCTIONS.md como referência metodológica.

## What Already Exists

**22 módulos** em `/home/cnmfs/bioeolica-dev2/workspaces/physics-m3/modules/`:
- Núcleo M³: m3_analysis, composite_model, structural_analysis
- Simulação: fem_solver, fluid_dynamics, thermodynamics, electromechanical
- CAD 3D: cad_visualization (1447 linhas, HeatMap3D, M3Visualizer, etc.)
- Qualidade: vvv_protocol, uncertainty, method_selector
- Infraestrutura: mapa_unico (M4), logging_wal (M5), knowledge_base (M6)
- Normas: normativo, economico, context_engine, scientific_writing
- Cinemática: kinematic_machine, mkdelagen
- **152 testes — 0 falhas**, demo completa 33/33 checks

## What Needs to Be Built (8 novos módulos)

### 1. `modules/peridynamics.py`
- Bond-based Peridynamics solver (1D/2D)
- Horizon and influence function
- Damage tracking, crack propagation
- Bond stretch criterion
- Integration with fem_solver for hybrid models

### 2. `modules/topology_optimization.py`
- SIMP (Solid Isotropic Material with Penalization)
- Sensitivity analysis
- Optimality criteria (OC) update
- Compliance minimization
- Volume constraint
- Integration with fem_solver for structural problems

### 3. `modules/fatigue.py`
- S-N curves (Woehler, Basquin)
- Rainflow cycle counting
- Palmgren-Miner linear damage rule
- Haigh diagram (mean stress effect)
- Goodman, Gerber, Soderberg criteria
- Variable amplitude loading spectrum

### 4. `modules/creep.py`
- Norton-Bailey power law
- Arrhenius temperature dependence
- Larson-Miller parameter
- Creep strain vs time curves
- Stress relaxation
- Composite creep behavior

### 5. `modules/cfd_solver.py`
- Finite difference method (1D/2D)
- Navier-Stokes (incompressible, laminar)
- SIMPLE algorithm basics
- Heat transfer coupling
- Boundary layer resolution
- Integration with fluid_dynamics.py

### 6. `modules/digital_twin.py`
- Sensor data simulation (temperature, strain, vibration)
- Model updating / parameter estimation
- Kalman filter basics
- Anomaly detection (residual-based)
- Remaining Useful Life (RUL) estimation
- Integration with M4/M5 for data logging

### 7. `modules/piezoelectric.py`
- Constitutive equations (e-form, d-form)
- d31, d33, d15 coupling modes
- Actuator force/displacement
- Sensor voltage/charge
- Energy harvesting (power vs load)
- Integration with fem_solver

### 8. `modules/erosion.py`
- Particle impact erosion model
- Finnie erosion model
- Leading edge erosion of wind turbine blades
- Depth of erosion vs time / particle count
- Integration with fluid_dynamics (particle tracking)

## KDI Compliance per Module

Each module MUST follow INSTRUCTIONS.md KDI methodology:

| Module | M³ Alignment | Open Source | Tests | M4/M5 Integration |
|--------|-------------|-------------|-------|-------------------|
| Peridynamics | Micro (fracture) | ✅ numpy/scipy | 8+ | Yes |
| Topology Opt | Meso (structure) | ✅ numpy/scipy | 8+ | Yes |
| Fatigue | Meso (cycles) | ✅ numpy/scipy | 8+ | Yes |
| Creep | Micro-Meso | ✅ numpy/scipy | 8+ | Yes |
| CFD | Macro (domain) | ✅ numpy/scipy | 8+ | Yes |
| Digital Twin | All scales | ✅ numpy/scipy | 8+ | Yes |
| Piezoelectric | Micro (coupling) | ✅ numpy/scipy | 8+ | Yes |
| Erosion | Meso (surface) | ✅ numpy/scipy | 8+ | Yes |

## Implementation Process (per module)

1. **Create module** with full docstrings, KDI references, usage examples
2. **Create 8+ pytest tests** in tests/test_{module}.py
3. **Add to demo_completa.py** — 2 checks per new module
4. **Verify M4/M5 integration** — all functions accept mapa/log params
5. **Run full test suite** — confirm 0 regressions

## Verification

```bash
python -m pytest tests/ -q           # All tests pass (152 + 64 = 216 expected)
python demo_completa.py | grep RESULT  # 33 + 16 = 49 checks expected
python scripts/agentic/python/fsm_orchestrator.py status  # DONE
```

## Files to Modify

- **CREATE** `modules/peridynamics.py` (novo)
- **CREATE** `modules/topology_optimization.py` (novo)
- **CREATE** `modules/fatigue.py` (novo)
- **CREATE** `modules/creep.py` (novo)
- **CREATE** `modules/cfd_solver.py` (novo)
- **CREATE** `modules/digital_twin.py` (novo)
- **CREATE** `modules/piezoelectric.py` (novo)
- **CREATE** `modules/erosion.py` (novo)
- **CREATE** `tests/test_peridynamics.py` (8+ tests)
- **CREATE** `tests/test_topology.py` (8+ tests)
- **CREATE** `tests/test_fatigue.py` (8+ tests)
- **CREATE** `tests/test_creep.py` (8+ tests)
- **CREATE** `tests/test_cfd.py` (8+ tests)
- **CREATE** `tests/test_digital_twin.py` (8+ tests)
- **CREATE** `tests/test_piezoelectric.py` (8+ tests)
- **CREATE** `tests/test_erosion.py` (8+ tests)
- **MODIFY** `demo_completa.py` (add 16 new checks)
- **MODIFY** `build_notebook.py` (add 8 new lab sections)
