# Data Model — Termo Module

## Entity: ThermalBC

| Field | Type | Description |
|-------|------|-------------|
| bc_id | TEXT | UUID |
| type | TEXT | `temperature`, `flux`, `convection` |
| value | FLOAT | BC magnitude (K, W/m², W/m²K) |
| node_set | TEXT | Target node set reference |
| ref_temp | FLOAT | Reference temp for convection (K) |

## Entity: ThermalMaterial

| Field | Type | Description |
|-------|------|-------------|
| material_id | TEXT | FK to materials DB |
| k | FLOAT | Thermal conductivity (W/mK) |
| alpha | FLOAT | CTE (1/K) |
| cp | FLOAT | Specific heat (J/kgK) |
| rho | FLOAT | Density (kg/m³) |

## Entity: TemperatureField

| Field | Type | Description |
|-------|------|-------------|
| field_id | TEXT | UUID |
| node_temps | JSON | Per-node temperature array |
| min_temp | FLOAT | Minimum temperature (K) |
| max_temp | FLOAT | Maximum temperature (K) |
| converged | BOOLEAN | Solver converged |
