# Data Model — CAD+REPORT Pipeline

## Entity: CradReportPackage

| Field | Type | Description |
|-------|------|-------------|
| model_id | TEXT | FK to ParametricModel |
| step_path | TEXT | Path to generated .step |
| report_path | TEXT | Path to generated .md report |
| metadata_path | TEXT | Path to .json metadata |
| checksum_step | TEXT | SHA-256 of STEP file |
| generated_at | TEXT | ISO 8601 timestamp |

## Metadata passed from CAD → CRSLR

| Field | Source | Target |
|-------|--------|--------|
| model dimensions | ParametricModel | CRSLR Context section |
| material | ParametricModel | CRSLR Context section |
| mesh info | Gmsh output | CRSLR Results section |
| step checksum | export.py | CRSLR metadata |
