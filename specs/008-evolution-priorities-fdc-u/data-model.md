# Data Model — Spec 008 Evolution Priorities (Fase 0)

> Entities for C7 (DB unify + pyproject) and C3 (specs 002/006).

## C7 — Database Unification

### Entity: `migration_log` (runtime only, not persistent)

| Field | Type | Description |
|-------|------|-------------|
| migration_id | TEXT (UUID) | Unique migration run |
| source_db | TEXT | Path to source DB (`./bioeolica.db` or `database.db`) |
| target_db | TEXT | Path to target (`data/bioeolica.db`) |
| tables_migrated | INTEGER | Count of tables transferred |
| rows_migrated | INTEGER | Total rows transferred |
| conflicts_resolved | INTEGER | Timestamp-based conflict count |
| status | TEXT | `PASS`, `FAIL`, `PARTIAL` |
| started_at | TEXT (ISO 8601) | Timestamp start |
| finished_at | TEXT (ISO 8601) | Timestamp end |
| checksum_source | TEXT | SHA-256 of source pre-migration |
| checksum_target | TEXT | SHA-256 of target post-migration |

### Entity: `dependency_entry` (pyproject.toml)

| Field | Type | Description |
|-------|------|-------------|
| package_name | TEXT | Pip package name |
| version_spec | TEXT | Version constraint (`>=X.Y`) |
| category | TEXT | `main`, `dev`, `test`, `doc` |
| source_file | TEXT | Original file (`requirements.txt`, `requirements-dev.txt`, etc.) |
| used_in | TEXT[] | Modules that import this package (audit) |

## C3 — Spec 002 (TopOpt)

### Entity: `topopt_case`

| Field | Type | Description |
|-------|------|-------------|
| case_id | TEXT | Unique identifier |
| mesh_file | TEXT | Path to `.msh` file |
| load_case | TEXT | Load boundary condition reference |
| material_id | TEXT | Reference to materials DB |
| volume_fraction | FLOAT | Target volume fraction (0-1) |
| optimizer | TEXT | `OpenMDAO` or `Dakota` |
| max_iterations | INTEGER | Convergence limit |
| convergence_tol | FLOAT | Tolerance (default 1e-4) |

### Entity: `topopt_result`

| Field | Type | Description |
|-------|------|-------------|
| case_id | TEXT | FK to `topopt_case` |
| iteration | INTEGER | Iteration number |
| compliance | FLOAT | Current compliance value |
| volume | FLOAT | Current volume fraction |
| density_field | BLOB | Serialized density array |
| status | TEXT | `running`, `converged`, `failed` |

## C3 — Spec 006 (Validação Experimental)

### Entity: `validation_protocol`

| Field | Type | Description |
|-------|------|-------------|
| protocol_id | TEXT | Unique ID (e.g., `V001`) |
| name | TEXT | Protocol name |
| domain | TEXT | Domain (`hidrologia`, `materiais`) |
| test_file | TEXT | Path to test file in `tests/validation/` |
| reference_standard | TEXT | Norma aplicável (ISO, ASTM, ABNT) |
| acceptance_criterion | TEXT | PASS/FAIL criterion |
| measurement_type | TEXT | Type of validation measurement |

### Entity: `validation_run`

| Field | Type | Description |
|-------|------|-------------|
| run_id | TEXT (UUID) | Unique run |
| protocol_id | TEXT | FK to `validation_protocol` |
| timestamp | TEXT | ISO 8601 |
| status | TEXT | `PASS`, `FAIL` |
| error_metric | FLOAT | Measured error |
| confidence_interval | TEXT | e.g., `95%` |
| vvv_report | TEXT | Path to VVV report artifact |

## Validation Rules

1. **Migration**: checksum_source + checksum_target must match expected post-migration
2. **TopOpt**: convergence_tol must be > 0; density_field must be reproducible (seed fixed)
3. **Validation**: each `validation_run` must link to exactly one protocol; each protocol must have ≥1 acceptance criterion

## State Transitions

### Migration: PENDING → RUNNING → PASS | FAIL
### TopOpt case: PENDING → RUNNING → CONVERGED | FAILED
### Validation run: SCHEDULED → RUNNING → PASS | FAIL
