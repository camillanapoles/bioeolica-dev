# Data Model: Quality & Compliance Optimization

## BenchmarkAnalytic

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Unique benchmark name (e.g., "cantilever_beam") |
| `domain` | enum | mecânica, fluidos, termo, materiais |
| `formula` | string | Analytical formula (LaTeX notation) |
| `expected_value` | float | Expected result (dimensionless or SI) |
| `tolerance_coarse` | float | Error tolerance for coarse mesh (%) |
| `tolerance_fine` | float | Error tolerance for refined mesh (%) |
| `min_elements` | int | Minimum elements for fine mesh |
| `method` | enum | FEM, FVM, SPH, MPM, DEM |
| `reference` | string | Literature/norm reference |

**Validation**: tolerance_coarse must be > tolerance_fine. expected_value must be > 0.

## VVVCertificate

| Field | Type | Description |
|-------|------|-------------|
| `simulation_id` | string | UUID of the simulation run |
| `timestamp` | datetime | Certification timestamp |
| `domain` | string | Domain being certified |
| `scale` | enum | macro, meso, micro |
| `criteria` | dict | {criterion_name: bool} — 6 binary criteria |
| `metrics` | dict | {metric_name: float} — quantified error/convergence/conservation |
| `overall_status` | enum | PASS, FAIL |
| `return_phase` | string | Suggested return phase if FAIL (F5→F4, F5→F3, etc.) |
| `return_reason` | string | Explanation of why failed and what to fix |

**Validation**: If any criterion is False → overall_status = FAIL. return_phase must be populated only if FAIL.

## WorkspacePackage

| Field | Type | Description |
|-------|------|-------------|
| `workspace_name` | string | Directory name (physics-m3, cad-cae, kdi-m3) |
| `package_name` | string | Python package name (physics_m3, cad_cae, kdi_m3) |
| `dependencies` | list[str] | Python package dependencies |
| `system_deps` | list[str] | System dependencies (CalculiX, etc.) |
| `has_gpu` | bool | Whether module requires GPU |
| `pyproject_path` | string | Path to pyproject.toml |

## ComplianceReport

| Field | Type | Description |
|-------|------|-------------|
| `timestamp` | datetime | Report generation time |
| `fdcu_scores` | dict | {objective: score} — O1 through O6 |
| `pqms_current` | float | Current PQMS score (0-100%) |
| `pqms_target` | float | Target PQMS score (94%) |
| `non_conformances` | list[dict] | Open non-conformances with status |
| `non_conformances_closed` | int | Count of closed non-conformances |
| `phase_summary` | dict | {phase: status} — PASS/FAIL per phase |
