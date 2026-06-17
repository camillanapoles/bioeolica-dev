# Data Model — CAD Integration Pipeline

## Entity: ParametricModel

| Field | Type | Description |
|-------|------|-------------|
| model_id | TEXT | UUID |
| name | TEXT | Model name |
| parameters | JSON | Key-value engineering dimensions (mm) |
| material | TEXT | Material reference |
| layers | JSON[] | Multimaterial layer definitions |

## Entity: CadModel

| Field | Type | Description |
|-------|------|-------------|
| model_id | TEXT | FK to ParametricModel |
| step_path | TEXT | Path to .step file |
| msh_path | TEXT | Path to .msh file |
| checksum | TEXT | SHA-256 of STEP |
| created_at | TEXT | ISO 8601 |

## Validation Rules

- All dimensions must be positive
- Layer thicknesses must sum to total thickness
- Step file must be valid CAD (test: opens in CadQuery)
