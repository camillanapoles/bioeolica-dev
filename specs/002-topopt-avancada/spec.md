# Feature Specification: Topology Optimization (TopOpt)

**Feature Branch**: `002-topopt-avancada`

**Status**: Active — OpenMDAO/Dakota stack

## Objective

Topology optimization of structural components using OpenMDAO + CalculiX FEM solver. Find optimal material distribution for minimum compliance under volume constraint.

## User Story 1 — Design Engineer: Run TopOpt (Priority: P1)

A design engineer wants to optimize a structural component's topology given load cases, boundary conditions, and a target volume fraction.

**Independent Test**: `pytest tests/ -k "topopt" -v --tb=short` discovers and passes tests.

**Acceptance Scenarios:**
1. Given a mesh (.msh) + load case + volume fraction, When TopOpt runs, Then compliance converges to minimum
2. Given the same input, When run with two different seeds, Then final topology differs < 5% (mesh-independent)
3. Given volume fraction = 0.3, When converged, Then actual volume fraction is within 1% of target

## User Story 2 — Design Engineer: Sensitivity Analysis (Priority: P2)

A design engineer wants to understand which load cases most affect the optimized topology.

**Independent Test**: `python -c "from openmdao import core; print('openmdao OK')"`

**Acceptance Scenarios:**
1. Given a converged TopOpt result, When sensitivity analysis runs, Then each load case has a quantified sensitivity index
2. Given sensitivity indices, When ranked, Then top 3 drivers are identified

## Technical Approach

### Pipeline

```
Geometry (.step) → Gmsh (.msh) → CalculiX (.frd) → Compliance → OpenMDAO (optimizer) → Density Field
```

### OpenMDAO Integration

```python
class TopOptGroup(om.Group):
    def setup(self):
        self.add_subsystem("fea", FEMComponent(), promotes=["*"])
        self.add_subsystem("objective", ComplianceComponent(), promotes=["*"])
        self.add_subsystem("constraint", VolumeConstraint(vol_frac=0.3), promotes=["*"])
```

### Convergence Criteria

- Mesh study: 3 levels — coarse (5k), medium (15k), fine (50k elements)
- Convergence: compliance change < 1e-4 over 10 consecutive iterations
- Checkerboard-free: sensitivity filter radius ≥ 1.5× element size

## Out of Scope

- Non-linear topology optimization (material non-linearity)
- Multi-material topology optimization (future spec)
- Transient/dynamic topology optimization
