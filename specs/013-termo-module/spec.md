# Feature Specification: Termo Module — Thermal Analysis

**Feature Branch**: `013-termo-module`

**Status**: Draft

## Objective

Implement thermal analysis capabilities: thermal expansion, thermal stress, steady-state heat conduction, and convection boundary conditions. Required for multi-domain (C10) and preCICE FSI coupling (C5).

## User Story 1 — Engineer: Steady-State Thermal (Priority: P1)

An engineer wants to compute temperature distribution and thermal stresses in a component given thermal BCs.

**Independent Test**: `pytest tests/test_termo.py -v --tb=short` passes.

**Acceptance Scenarios:**
1. Given a mesh + thermal BCs (temperature, flux, convection), When solver runs, Then temperature field converges
2. Given temperature field + material CTE, When thermal stress computed, Then stress field is output
3. Given convection BC, When solver runs, Then heat transfer coefficient is respected

## User Story 2 — Multi-Physics: Thermal-Structural Coupling (Priority: P2)

An analyst wants to compute thermal expansion-induced stresses coupling thermal and structural solvers.

**Independent Test**: Coupled solve produces different result than uncoupled.

## Technical Approach

### Pipeline

```
Mesh (.msh) → Thermal BCs → FEM Heat Solve → Temperature Field → Thermal Strain → Stress Field
```

### FEM Formulation

- Steady-state heat conduction: K·T = Q
- Element: Linear tetrahedral (same mesh as structural)
- BCs: Temperature (Dirichlet), Flux (Neumann), Convection (Robin)
- Thermal stress: σ_th = -E·α·ΔT/(1-ν)

## Out of Scope

- Transient thermal analysis (future)
- Radiation (future)
- Phase change
