# Implementation Plan: Topology Optimization (TopOpt)

## Technical Context

| Campo | Valor |
|-------|-------|
| Language | Python 3.11+ |
| Dependencies | openmdao, numpy, scipy, gmsh, calculix (ccx subprocess) |
| Testing | pytest, mesh convergence study |
| Storage | SQLite via data/bioeolica.db |
| Target | Linux (WSL2) |

## Mesh Convergence Criteria

Three levels of mesh refinement:

| Level | Elements | Expected Error | Use Case |
|-------|----------|---------------|----------|
| Coarse | 5k | < 10% | Quick iteration |
| Medium | 15k | < 5% | Standard analysis |
| Fine | 50k | < 2% | Final validation |

Sensitivity filter radius: ≥ 1.5× element size to prevent checkerboarding.

## Project Structure

```
src/topopt/
├── fem_component.py      # FEMComponent(om.ExplicitComponent)
├── compliance.py          # ComplianceComponent
├── volume_constraint.py   # VolumeConstraint(om.ExplicitComponent)
├── topopt_group.py        # TopOptGroup assembly
├── run_optimization.py    # CLI entry point
└── __init__.py
tests/
├── test_fem_component.py
├── test_compliance.py
├── test_volume_constraint.py
└── test_mesh_convergence.py
```

## Execution Order

1. Mesh generation (Gmsh) → CalculiX FEA → Compliance extraction
2. OpenMDAO group assembly → Driver configuration (SLSQP/MMA)
3. Optimization loop → Convergence check → Density field output
