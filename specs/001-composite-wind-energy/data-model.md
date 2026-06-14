# Data Model: Composite Biomaterial for Wind Energy

> Phase 1 output — entity definitions, attributes, relationships, validation rules
> References: [spec.md](spec.md) FR-015 through FR-021, [research.md](research.md) R5/R6

---

## Entity-Relationship Diagram (Textual)

```
Validation Reference (benchmark)   
        |
        | validates
        v
Material Specimen ──< Test Result
        |                  |
        |                  +---> Microstructure Image
        |                  +---> Computational Model (calibration)
        |
        +---> Computational Model (material model)
                    |
                    v
              Blade Design
                    |
              Wind Turbine System
                    |
              Energy System <─── Community Profile
```

---

## Entity Definitions

### 1. Material Specimen

The physical test specimen produced and tested. Represents both baseline (paper mache only) and composite (paper mache + graphite).

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | TEXT (UUID v4) | Yes | Primary key |
| specimen_type | ENUM | Yes | `baseline` or `composite` |
| paper_type | TEXT | Yes | Source paper (e.g., newspaper, office paper, mixed) |
| binder_type | TEXT | Yes | e.g., "PVA" |
| binder_ratio | TEXT | Yes | Glue-to-water ratio (e.g., "1:3") |
| curing_time_hours | REAL | Yes | Curing duration |
| curing_temp_c | REAL | Yes | Curing temperature |
| graphite_grade | TEXT | No | Only for composite specimens |
| graphite_particle_size_um | REAL | No | Mean particle size in microns |
| blasting_pressure_bar | REAL | No | Blasting pressure |
| standoff_distance_mm | REAL | No | Nozzle-to-surface distance |
| coating_thickness_mm | REAL | No | Measured coating thickness |
| geometry_type | TEXT | Yes | Specimen shape (dogbone, rectangular, etc.) |
| geometry_dimensions | TEXT | Yes | JSON: {length, width, thickness} |
| production_date | TEXT (ISO 8601) | Yes | Date of production |
| production_notes | TEXT | No | Free-text notes |
| storage_conditions | TEXT | No | e.g., "25°C, 50% RH" |
| validation_status | ENUM | No | PENDING, PASS, FAIL |
| quality_score | REAL | No | 0-10 |
| created_at | TEXT (ISO 8601) | Yes | Auto-timestamp |
| tags | TEXT (JSON) | No | Search/filter tags |

**Validation Rules**:
- `specimen_type = composite` ⟹ `graphite_grade`, `blasting_pressure_bar`, `coating_thickness_mm` all required
- `coating_thickness_mm` must be <= 2.0 mm (process limit)
- `quality_score` defaults to NULL until computed

---

### 2. Test Result

Outcome of a mechanical or physical test performed on a specimen.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | TEXT (UUID v4) | Yes | Primary key |
| specimen_id | TEXT (UUID v4) | Yes | FK → Material Specimen |
| test_standard | TEXT | Yes | e.g., "ASTM D638", "ASTM D790" |
| test_type | ENUM | Yes | tensile, flexural, compressive, hardness, fatigue, impact |
| property_measured | TEXT | Yes | e.g., "tensile_strength", "elastic_modulus" |
| value | REAL | Yes | Measured value |
| unit | TEXT | Yes | e.g., "MPa", "GPa", "Shore D" |
| uncertainty | REAL | Yes | Measurement uncertainty (±) |
| uncertainty_type | ENUM | Yes | standard_deviation, confidence_interval, instrument_error |
| num_replicates | INTEGER | Yes | Number of replicate tests |
| test_date | TEXT (ISO 8601) | Yes | Date of test |
| testing_machine | TEXT | Yes | Equipment used |
| operator | TEXT | No | Operator name/ID |
| temperature_c | REAL | No | Test ambient temperature |
| humidity_pct | REAL | No | Test ambient humidity |
| failure_mode | TEXT | No | e.g., "brittle_fracture", "delamination" |
| notes | TEXT | No | Free-text notes |
| raw_data_file | TEXT | No | Path to raw data file |
| validation_status | ENUM | No | PENDING, PASS, FAIL |
| created_at | TEXT (ISO 8601) | Yes | Auto-timestamp |

**Validation Rules**:
- `value` must be > 0
- `uncertainty` must be >= 0 AND < `value` (sanity check)
- `num_replicates` must be >= 1
- `specimen_id` must reference a valid Material Specimen

---

### 3. Microstructure Image

SEM or optical microscopy image of a specimen's surface or cross-section.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | TEXT (UUID v4) | Yes | Primary key |
| specimen_id | TEXT (UUID v4) | Yes | FK → Material Specimen |
| image_type | ENUM | Yes | SEM, optical |
| magnification | REAL | Yes | Magnification factor |
| imaging_mode | TEXT | No | e.g., "SE", "BSE" (for SEM) |
| analyzed_region | TEXT | No | e.g., "cross_section", "surface_top", "interface" |
| measured_features | TEXT (JSON) | No | JSON: {particle_penetration_um, porosity_pct, coating_thickness_um} |
| image_file | TEXT | Yes | Path to image file |
| analysis_software | TEXT | No | Software used for measurement |
| notes | TEXT | No | Free-text |
| created_at | TEXT (ISO 8601) | Yes | Auto-timestamp |

---

### 4. Computational Model

A simulation setup definition (not results).

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | TEXT (UUID v4) | Yes | Primary key |
| model_type | ENUM | Yes | FEM, CFD, analytical, multi_scale, PINN |
| domain | ENUM | Yes | structural, fluid, thermal, coupled |
| solver_software | TEXT | Yes | e.g., "CalculiX", "OpenFOAM", "Python" |
| solver_version | TEXT | Yes | Software version |
| mesh_type | TEXT | No | e.g., "tetrahedral", "hexahedral", "polyhedral" |
| mesh_num_elements | INTEGER | No | Element count |
| mesh_num_nodes | INTEGER | No | Node count |
| boundary_conditions | TEXT (JSON) | Yes | BC definition |
| material_model | TEXT | Yes | e.g., "linear_elastic", "von_mises_plastic" |
| material_properties | TEXT (JSON) | Yes | Material property values |
| solver_parameters | TEXT (JSON) | No | Solver settings, convergence criteria |
| calibration_status | ENUM | No | uncalibrated, calibrated, validated |
| calibrated_against | TEXT (UUID v4) | No | FK → Test Result or Validation Reference |
| calibration_error_pct | REAL | No | Relative error after calibration |
| input_files | TEXT (JSON) | No | Paths to input files |
| notes | TEXT | No | Free-text |
| created_at | TEXT (ISO 8601) | Yes | Auto-timestamp |

**Validation Rules**:
- `calibration_status = validated` ⟹ `calibrated_against` and `calibration_error_pct` must be present
- `calibration_error_pct` must be < 10.0 (per SC-002)

---

### 5. Simulation Result

Output dataset from a computational model run.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | TEXT (UUID v4) | Yes | Primary key |
| model_id | TEXT (UUID v4) | Yes | FK → Computational Model |
| run_timestamp | TEXT (ISO 8601) | Yes | When simulation ran |
| convergence_metric | REAL | No | Residual or convergence value |
| convergence_threshold | REAL | No | Target threshold |
| mesh_convergence_pct | REAL | No | Variation between mesh refinements |
| output_quantities | TEXT (JSON) | Yes | JSON: {stress_max, strain_max, displacement_max, ...} |
| output_files | TEXT (JSON) | No | Paths to output files |
| validation_status | ENUM | No | PENDING, PASS, FAIL |
| validation_vs_experiment | TEXT (UUID v4) | No | FK → Test Result (if validated) |
| validation_error_pct | REAL | No | Error vs. experimental reference |
| uncertainty_quantification | TEXT | No | Method used (Monte Carlo, interval, etc.) |
| notes | TEXT | No | Free-text |
| created_at | TEXT (ISO 8601) | Yes | Auto-timestamp |

---

### 6. Blade Design

Wind turbine blade geometry and structural design.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | TEXT (UUID v4) | Yes | Primary key |
| blade_length_m | REAL | Yes | Blade length |
| airfoil_profile | TEXT | Yes | Profile identifier(s) |
| num_blades | INTEGER | Yes | Number of blades |
| material_id | TEXT (UUID v4) | Yes | FK → Material Specimen (properties used) |
| structural_layup | TEXT | No | Layup description |
| safety_factor_static | REAL | Yes | Static safety factor |
| safety_factor_fatigue | REAL | Yes | Fatigue safety factor |
| design_wind_speed_ms | REAL | Yes | Rated wind speed |
| extreme_wind_speed_ms | REAL | Yes | Survival wind speed (gust) |
| mass_kg | REAL | No | Blade mass estimate |
| geometry_file | TEXT | No | CAD file path |
| created_at | TEXT (ISO 8601) | Yes | Auto-timestamp |

---

### 7. Wind Turbine System

Complete turbine configuration.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | TEXT (UUID v4) | Yes | Primary key |
| turbine_type | ENUM | Yes | VAWT, Archimedes |
| configuration | TEXT | No | e.g., "H-rotor Darrieus", "helical 3-blade" |
| rated_power_kw | REAL | Yes | Rated power |
| rotor_diameter_m | REAL | Yes | Rotor diameter |
| tower_height_m | REAL | Yes | Hub/tower height |
| swept_area_m2 | REAL | Yes | Rotor swept area |
| cut_in_speed_ms | REAL | Yes | Minimum operational wind |
| cut_out_speed_ms | REAL | Yes | Maximum operational wind |
| rated_wind_speed_ms | REAL | Yes | Wind speed at rated power |
| control_type | TEXT | No | e.g., "passive_stall", "furling", "electronic" |
| blade_design_id | TEXT (UUID v4) | Yes | FK → Blade Design |
| created_at | TEXT (ISO 8601) | Yes | Auto-timestamp |

---

### 8. Energy System

Complete generation, storage, and distribution.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | TEXT (UUID v4) | Yes | Primary key |
| turbine_id | TEXT (UUID v4) | Yes | FK → Wind Turbine System |
| battery_capacity_kwh | REAL | Yes | Total battery storage |
| battery_type | TEXT | No | e.g., "lead_acid", "lithium_ion" |
| inverter_rating_kw | REAL | Yes | Inverter power rating |
| inverter_efficiency_pct | REAL | Yes | Efficiency |
| charge_controller_type | TEXT | No | e.g., "MPPT", "PWM" |
| distribution_voltage_v | REAL | Yes | Distribution voltage |
| annual_energy_kwh | REAL | Yes | Estimated annual production |
| capacity_factor_pct | REAL | Yes | Annual capacity factor |
| autonomy_days | REAL | Yes | Battery autonomy |
| lcoe_usd_per_kwh | REAL | Yes | Levelized cost of energy |
| installed_cost_usd | REAL | Yes | Total installed cost |
| cost_per_kw_usd | REAL | Yes | Cost per rated kW |
| created_at | TEXT (ISO 8601) | Yes | Auto-timestamp |

---

### 9. Community Profile

Energy demand model for a target community.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | TEXT (UUID v4) | Yes | Primary key |
| name | TEXT | Yes | Community name/identifier |
| location | TEXT | No | Geographic location |
| num_families | INTEGER | Yes | Number of households |
| total_population | INTEGER | No | Estimated population |
| irrigated_area_ha | REAL | Yes | Irrigated crop area |
| water_demand_l_per_day | REAL | Yes | Daily irrigation water demand |
| energy_pumping_kwh_day | REAL | Yes | Pumping energy |
| energy_processing_kwh_day | REAL | Yes | Food processing energy |
| energy_community_kwh_day | REAL | Yes | Lighting, refrigeration, appliances |
| energy_total_kwh_day | REAL | Yes | Total daily demand |
| energy_monthly_kwh | REAL (JSON) | No | Monthly profile (12 values) |
| seasonal_variation_pct | REAL | No | ± seasonal variation |
| growth_margin_pct | REAL | Yes | Projected growth margin |
| data_source | TEXT | Yes | Source of the profile data |
| created_at | TEXT (ISO 8601) | Yes | Auto-timestamp |

---

### 10. Validation Reference

Published benchmark or dataset used for method validation.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | TEXT (UUID v4) | Yes | Primary key |
| source_type | ENUM | Yes | journal, standard, dataset, thesis, report |
| title | TEXT | Yes | Full reference title |
| authors | TEXT (JSON) | Yes | Author list |
| year | INTEGER | Yes | Publication year |
| doi | TEXT | No | DOI identifier |
| url | TEXT | No | Access URL |
| source_quality_score | INTEGER | Yes | 0-10 quality assessment |
| validation_metric_type | TEXT | Yes | e.g., "correlation", "rmse", "max_error" |
| validation_threshold | REAL | Yes | Acceptance threshold |
| applicability | TEXT (JSON) | No | Domains where applicable |
| file_path | TEXT | No | Local file path if downloaded |
| created_at | TEXT (ISO 8601) | Yes | Auto-timestamp |

**Validation Rules**:
- `source_quality_score` >= 8 for sources used in methodology validation sub-score = 1.0
- `year` >= 2000 (unless seminal/historical reference)

---

## Provenance Tracking

The `provenance` table records directed edges between objects:

```sql
CREATE TABLE provenance (
    id TEXT PRIMARY KEY,              -- UUID v4
    source_id TEXT NOT NULL,           -- input object FK
    target_id TEXT NOT NULL,           -- output/derived object FK
    transformation TEXT NOT NULL,       -- operation applied
    parameters TEXT,                    -- JSON parameters
    timestamp TEXT NOT NULL,           -- ISO 8601
    FOREIGN KEY (source_id) REFERENCES objects(id),
    FOREIGN KEY (target_id) REFERENCES objects(id)
);
```

Key provenance chains:

| Chain | Path | Description |
|-------|------|-------------|
| Material characterization | Material Specimen → Test Result → Microstructure Image | Full experimental chain |
| Model calibration | Validation Reference → Computational Model → Simulation Result | Model setup to validation |
| Design chain | Material Specimen → Computational Model → Blade Design → Wind Turbine System → Energy System | Material to system |
| Sizing chain | Community Profile → Energy System | Demand-driven design |

---

## PQMS Computation

The `quality_scores` table stores per-dimension scores for any object:

```sql
CREATE TABLE quality_scores (
    id TEXT PRIMARY KEY,
    object_id TEXT NOT NULL,
    dimension TEXT NOT NULL,
    score REAL NOT NULL,
    weight REAL NOT NULL,
    evidence TEXT,
    computed_at TEXT NOT NULL,
    FOREIGN KEY (object_id) REFERENCES objects(id)
);
```

Aggregate PQMS = SUM(score * weight) / SUM(weights), with the constraint that no single dimension falls below 8.5 (per SC-008).
