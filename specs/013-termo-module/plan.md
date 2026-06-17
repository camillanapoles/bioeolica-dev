# Implementation Plan: Termo Module

## Technical Context

| Campo | Valor |
|-------|-------|
| Language | Python 3.11+ |
| Dependencies | numpy, scipy (sparse solvers) |
| Testing | pytest, analytical validation (1D rod) |
| Storage | data/bioeolica.db (materials with CTE) |
| Pre-requisites | C7 DB ✅ (materials with thermal props needed) |

## Project Structure

```
src/termo/
├── solver.py        # Steady-state heat conduction FEM solver
├── stress.py        # Thermal stress computation (σ = -E·α·ΔT)
├── bc.py            # Thermal BC types (Dirichlet, Neumann, Robin)
├── materials.py     # Thermal material properties (k, α, Cp)
├── coupling.py      # Thermal-structural coupling bridge
└── __init__.py
tests/
├── test_solver.py
├── test_stress.py
└── test_coupling.py
```

## Execution Order

1. BC types → Solver (K·T=Q) → Thermal stress → Coupling → Tests
