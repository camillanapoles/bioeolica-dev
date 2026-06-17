# Contract: OpenMDAO TopOpt Integration

## TopOptGroup Interface

```python
class TopOptGroup(om.Group):
    inputs:
        - density_field: np.ndarray  (n_vars,)
        - load_vector: np.ndarray    (n_dofs,)
    outputs:
        - compliance: float
        - volume_fraction: float
```

## Components

| Component | Type | Inputs | Outputs |
|-----------|------|--------|---------|
| FEMComponent | ExplicitComponent | density_field, load_vector | displacements, compliance |
| ComplianceComponent | ExplicitComponent | displacements, load_vector | compliance_value |
| VolumeConstraint | ExplicitComponent | density_field | volume_fraction |

## Driver

- SLSQP for gradient-based optimization
- MMA (Method of Moving Asymptotes) fallback
- Max iterations: 200
- Tolerance: 1e-4 (compliance change)
