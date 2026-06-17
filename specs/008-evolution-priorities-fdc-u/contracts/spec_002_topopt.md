# Contract: Spec 002 TopOpt Revision

> Review and supplement spec 002 for OpenMDAO/Dakota topology optimization.

## Scope

- **Existing:** spec.md, plan.md, tasks.md, contracts/ intact (T001-T11 completed)
- **Work:** review scope accuracy, add OpenMDAO/Dakota integration patterns, validate mesh convergence

## Interface

The spec 002 `plan.md` must document:

### TopOpt Pipeline

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

- Mesh study: 3 levels (coarse 5k, medium 15k, fine 50k elements)
- Convergence: compliance change < 1e-4 over 10 consecutive iterations
- Checkerboard-free: sensitivity filter radius ≥ 1.5× element size
