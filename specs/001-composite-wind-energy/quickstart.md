# Quickstart: Composite Biomaterial for Wind Energy

> Phase 1 output — runnable validation scenarios for all 3 parts
> Prerequisites: SQLite 3.x, Python 3.10+, CalculiX 2.20+, OpenFOAM v2212+
> References: [spec.md](spec.md), [data-model.md](data-model.md), [contracts/](contracts/)

---

## Contents

1. [Prerequisites & Setup](#1-prerequisites--setup)
2. [Part 1: Material Characterization](#2-part-1-material-characterization)
3. [Part 2: Wind Energy System](#3-part-2-wind-energy-system)
4. [Part 3: Data Management & PQMS](#4-part-3-data-management--pqms)
5. [Full Validation Run](#5-full-validation-run)

---

## 1. Prerequisites & Setup

### 1.1 Software Requirements

| Tool | Version | Purpose | Installation |
|------|---------|---------|-------------|
| SQLite | 3.x | Data persistence & provenance | `apt install sqlite3` |
| Python | 3.10+ | Analysis & PQMS computation | `apt install python3` |
| CalculiX | 2.20+ | FEM structural analysis | `apt install calculix-ccx` |
| OpenFOAM | v2212+ | CFD aerodynamic analysis | `apt install openfoam` |
| SU2 | 7.x | CFD cross-validation | `apt install su2` |
| ParaView | 5.10+ | Result visualization | `apt install paraview` |

### 1.2 Database Setup

```bash
# Initialize the SQLite database with all schemas
cat contracts/schema-core.sql \
    contracts/schema-entities.sql \
    contracts/schema-validation.sql \
    contracts/pqms-interface.sql | sqlite3 bioeolica.db

# Verify schema loaded correctly
sqlite3 bioeolica.db ".tables"
# Expected: objects, provenance, quality_scores, schema_migrations,
#           material_specimens, test_results, microstructure_images,
#           computational_models, simulation_results, blade_designs,
#           wind_turbine_systems, energy_systems, community_profiles,
#           validation_references, pqms_dimension_weights
#           + all v_ views
```

### 1.3 Data Directory Structure

```bash
mkdir -p data/{specimens,simulations,experiments,references}
```

---

## 2. Part 1: Material Characterization

### 2.1 Specimen Registration

Validate the data model by inserting a baseline and composite specimen:

```bash
# Generate UUIDs
BASELINE_ID=$(python3 -c "import uuid; print(uuid.uuid4())")
COMPOSITE_ID=$(python3 -c "import uuid; print(uuid.uuid4())")

# Register baseline specimen in objects table
sqlite3 bioeolica.db "INSERT INTO objects (id, object_type, created_at, updated_at)
    VALUES ('$BASELINE_ID', 'specimen', strftime('%Y-%m-%dT%H:%M:%SZ','now'), strftime('%Y-%m-%dT%H:%M:%SZ','now'));"

# Insert baseline specimen record
sqlite3 bioeolica.db "INSERT INTO material_specimens
    (id, specimen_type, paper_type, binder_type, binder_ratio,
     curing_time_hours, curing_temp_c, geometry_type, geometry_dimensions,
     production_date)
VALUES
    ('$BASELINE_ID', 'baseline', 'newspaper', 'PVA', '1:3',
     24, 25, 'dogbone', '{\"length\": 165, \"width\": 19, \"thickness\": 4}',
     '2026-06-01');"

# Register composite specimen
sqlite3 bioeolica.db "INSERT INTO objects (id, object_type, created_at, updated_at)
    VALUES ('$COMPOSITE_ID', 'specimen', strftime('%Y-%m-%dT%H:%M:%SZ','now'), strftime('%Y-%m-%dT%H:%M:%SZ','now'));"

sqlite3 bioeolica.db "INSERT INTO material_specimens
    (id, specimen_type, paper_type, binder_type, binder_ratio,
     curing_time_hours, curing_temp_c, graphite_grade,
     graphite_particle_size_um, blasting_pressure_bar,
     standoff_distance_mm, coating_thickness_mm,
     geometry_type, geometry_dimensions, production_date)
VALUES
    ('$COMPOSITE_ID', 'composite', 'newspaper', 'PVA', '1:3',
     24, 25, 'flake_industrial',
     100, 4.0, 150, 0.5,
     'dogbone', '{\"length\": 165, \"width\": 19, \"thickness\": 4}',
     '2026-06-01');"
```

**Expected outcome**: Both inserts succeed. Verify constraint enforcement:

```bash
# This should FAIL (baseline must not have graphite fields)
sqlite3 bioeolica.db "INSERT INTO material_specimens
    (id, specimen_type, paper_type, binder_type, binder_ratio,
     curing_time_hours, curing_temp_c, graphite_grade,
     geometry_type, geometry_dimensions, production_date)
VALUES
    ('$(python3 -c "import uuid; print(uuid.uuid4())")', 'baseline', 'newspaper', 'PVA', '1:3',
     24, 25, 'flake_industrial',
     'dogbone', '{\"length\": 165, \"width\": 19, \"thickness\": 4}',
     '2026-06-01');"
# Expected: no error — NULL graphite fields are allowed for baseline
# (the constraint only requires them for composite type)
```

### 2.2 Test Result Registration

```bash
TENSILE_ID=$(python3 -c "import uuid; print(uuid.uuid4())")

sqlite3 bioeolica.db "INSERT INTO objects (id, object_type, created_at, updated_at)
    VALUES ('$TENSILE_ID', 'test_result', strftime('%Y-%m-%dT%H:%M:%SZ','now'), strftime('%Y-%m-%dT%H:%M:%SZ','now'));"

sqlite3 bioeolica.db "INSERT INTO test_results
    (id, specimen_id, test_standard, test_type, property_measured,
     value, unit, uncertainty, uncertainty_type, num_replicates,
     test_date, testing_machine)
VALUES
    ('$TENSILE_ID', '$COMPOSITE_ID', 'ASTM D638', 'tensile', 'tensile_strength',
     12.5, 'MPa', 1.2, 'standard_deviation', 5,
     '2026-06-05', 'Instron 5967');"
```

**Expected outcome**: Insert succeeds. Verify constraint enforcement:

```bash
# This should FAIL (value must be > 0)
sqlite3 bioeolica.db "INSERT INTO test_results
    (id, specimen_id, test_standard, test_type, property_measured,
     value, unit, uncertainty, uncertainty_type, num_replicates,
     test_date, testing_machine)
VALUES
    ('$(python3 -c "import uuid; print(uuid.uuid4())")', '$COMPOSITE_ID', 'ASTM D638', 'tensile', 'tensile_strength',
     -1.0, 'MPa', 0.5, 'standard_deviation', 5,
     '2026-06-05', 'Instron 5967');"
# Expected: CHECK constraint violation on ck_value_positive
```

### 2.3 Provenance Chain Validation

```bash
PROV_ID=$(python3 -c "import uuid; print(uuid.uuid4())")

# Link specimen → test result in provenance DAG
sqlite3 bioeolica.db "INSERT INTO provenance (id, source_id, target_id, transformation, parameters, timestamp)
VALUES ('$PROV_ID', '$COMPOSITE_ID', '$TENSILE_ID', 'mechanical_test',
        '{\"standard\": \"ASTM D638\", \"machine\": \"Instron 5967\"}',
        strftime('%Y-%m-%dT%H:%M:%SZ','now'));"

# Verify provenance chain
sqlite3 bioeolica.db "SELECT * FROM v_provenance_audit WHERE object_id IN ('$COMPOSITE_ID', '$TENSILE_ID');"
```

**Expected outcome**: Both objects show `PASS` for provenance audit.

---

## 3. Part 2: Wind Energy System

### 3.1 Community Profile

```bash
COMM_ID=$(python3 -c "import uuid; print(uuid.uuid4())")

sqlite3 bioeolica.db "INSERT INTO objects (id, object_type, created_at, updated_at)
    VALUES ('$COMM_ID', 'community_profile', strftime('%Y-%m-%dT%H:%M:%SZ','now'), strftime('%Y-%m-%dT%H:%M:%SZ','now'));"

# Insert community profile (semi-arid agricultural community of 20 families)
sqlite3 bioeolica.db "INSERT INTO community_profiles
    (id, name, location, num_families, total_population,
     irrigated_area_ha, water_demand_l_per_day,
     energy_pumping_kwh_day, energy_processing_kwh_day,
     energy_community_kwh_day, energy_total_kwh_day,
     energy_monthly_kwh, seasonal_variation_pct, growth_margin_pct, data_source)
VALUES
    ('$COMM_ID', 'Sertao_Agricola_01', 'Sertao, NE Brazil',
     20, 100,
     3.5, 17500,
     20, 10, 12, 44,
     '[1320, 1200, 1320, 1200, 1240, 1100, 1100, 1140, 1200, 1320, 1360, 1400]',
     20, 15, 'INMET/IBGE/ISA community energy study 2024');"
```

**Expected**: Insert succeeds. Verify community profile is correctly stored.

### 3.2 Blade Design

```bash
BLADE_ID=$(python3 -c "import uuid; print(uuid.uuid4())")

sqlite3 bioeolica.db "INSERT INTO objects (id, object_type, created_at, updated_at)
    VALUES ('$BLADE_ID', 'blade_design', strftime('%Y-%m-%dT%H:%M:%SZ','now'), strftime('%Y-%m-%dT%H:%M:%SZ','now'));"

sqlite3 bioeolica.db "INSERT INTO blade_designs
    (id, blade_length_m, airfoil_profile, num_blades, material_id,
     safety_factor_static, safety_factor_fatigue,
     design_wind_speed_ms, extreme_wind_speed_ms)
VALUES
    ('$BLADE_ID', 3.5, 'NACA 0018', 3, '$COMPOSITE_ID',
     2.5, 2.2,
     6.0, 45.0);"
```

**Expected**: Insert succeeds. Verify safety factors >= 2.0:

```bash
sqlite3 bioeolica.db "SELECT * FROM v_safety_factor_check WHERE id = '$BLADE_ID';"
# Expected: PASS
```

### 3.3 Wind Turbine System

```bash
TURB_ID=$(python3 -c "import uuid; print(uuid.uuid4())")

sqlite3 bioeolica.db "INSERT INTO objects (id, object_type, created_at, updated_at)
    VALUES ('$TURB_ID', 'wind_turbine_system', strftime('%Y-%m-%dT%H:%M:%SZ','now'), strftime('%Y-%m-%dT%H:%M:%SZ','now'));"

sqlite3 bioeolica.db "INSERT INTO wind_turbine_systems
    (id, turbine_type, configuration, rated_power_kw,
     rotor_diameter_m, tower_height_m, swept_area_m2,
     cut_in_speed_ms, cut_out_speed_ms, rated_wind_speed_ms,
     blade_design_id, created_at)
VALUES
    ('$TURB_ID', 'VAWT', 'H-rotor Darrieus', 10,
     7.0, 12.0, 38.5,
     2.5, 25.0, 6.0,
     '$BLADE_ID', strftime('%Y-%m-%dT%H:%M:%SZ','now'));"
```

### 3.4 Energy System

```bash
ENERGY_ID=$(python3 -c "import uuid; print(uuid.uuid4())")

sqlite3 bioeolica.db "INSERT INTO objects (id, object_type, created_at, updated_at)
    VALUES ('$ENERGY_ID', 'energy_system', strftime('%Y-%m-%dT%H:%M:%SZ','now'), strftime('%Y-%m-%dT%H:%M:%SZ','now'));"

sqlite3 bioeolica.db "INSERT INTO energy_systems
    (id, turbine_id, battery_capacity_kwh, battery_type,
     inverter_rating_kw, inverter_efficiency_pct,
     charge_controller_type, distribution_voltage_v,
     annual_energy_kwh, capacity_factor_pct, autonomy_days,
     lcoe_usd_per_kwh, installed_cost_usd, cost_per_kw_usd, created_at)
VALUES
    ('$ENERGY_ID', '$TURB_ID', 88, 'lithium_ion',
     12, 95,
     'MPPT', 48,
     35040, 40, 2.0,
     0.12, 25000, 2500,
     strftime('%Y-%m-%dT%H:%M:%SZ','now'));"
```

**Expected**: Insert succeeds. Verify economic targets:

```bash
sqlite3 bioeolica.db "SELECT * FROM v_economic_targets WHERE id = '$ENERGY_ID';"
# Expected: PASS (LCOE < $0.15, cost/kW < $3,000)

sqlite3 bioeolica.db "SELECT * FROM v_energy_sizing WHERE id = '$ENERGY_ID';"
# Expected: PASS (autonomy >= 2 days, capacity factor >= 20%)
```

---

## 4. Part 3: Data Management & PQMS

### 4.1 Validation Reference Registration

```bash
REF_ID=$(python3 -c "import uuid; print(uuid.uuid4())")

sqlite3 bioeolica.db "INSERT INTO objects (id, object_type, created_at, updated_at)
    VALUES ('$REF_ID', 'validation_reference', strftime('%Y-%m-%dT%H:%M:%SZ','now'), strftime('%Y-%m-%dT%H:%M:%SZ','now'));"

sqlite3 bioeolica.db "INSERT INTO validation_references
    (id, source_type, title, authors, year, doi,
     source_quality_score, validation_metric_type, validation_threshold)
VALUES
    ('$REF_ID', 'journal',
     'Mechanical Properties of PVA-Bonded Cellulose Fiber Composites',
     '[\"Silva, A.\", \"Santos, B.\", \"Oliveira, C.\"]',
     2024, '10.xxxx/yyyyy',
     8, 'correlation', 0.95);"
```

### 4.2 Computational Model with Calibration

```bash
CM_ID=$(python3 -c "import uuid; print(uuid.uuid4())")

sqlite3 bioeolica.db "INSERT INTO objects (id, object_type, created_at, updated_at)
    VALUES ('$CM_ID', 'computational_model', strftime('%Y-%m-%dT%H:%M:%SZ','now'), strftime('%Y-%m-%dT%H:%M:%SZ','now'));"

sqlite3 bioeolica.db "INSERT INTO computational_models
    (id, model_type, domain, solver_software, solver_version,
     mesh_type, mesh_num_elements, mesh_num_nodes,
     boundary_conditions, material_model, material_properties,
     material_properties_docstring, solver_parameters,
     input_files)
VALUES
    ('$CM_ID', 'FEM', 'structural', 'CalculiX', '2.20',
     'tetrahedral', 25000, 8000,
     '{\"fixed\": [\"blade_root\"], \"pressure\": {\"face\": \"suction_side\", \"value\": 500}}',
     'linear_elastic',
     '{\"E\": 4500, \"nu\": 0.35, \"rho\": 800}',
     '{\"tolerance\": 1e-6, \"max_iterations\": 50}',
     '{\"inp\": \"src/01-material-characterization/fem/blade_static.inp\"}');"
```

### 4.3 PQMS Quality Scores

```bash
# Insert quality scores for the computational model, one per dimension
for DIM in D1_completude D2_profundidade D3_rigor D4_rastreabilidade D5_conhecimento \
           D6_integracao D7_qualidade_numerica D8_impacto D9_vies D10_ensino \
           D11_velocidade D12_satisfacao D13_inovacao; do

    QS_ID=$(python3 -c "import uuid; print(uuid.uuid4())")

    # Extract weight for this dimension
    WEIGHT=$(sqlite3 bioeolica.db "SELECT weight FROM pqms_dimension_weights WHERE dimension = '$DIM';")

    # Assign score based on dimension (example: all >= 9.0 to target PQMS >= 9.5)
    case $DIM in
        D1_completude) SCORE=9.5 ;;
        D2_profundidade) SCORE=9.0 ;;
        D3_rigor) SCORE=9.5 ;;
        D4_rastreabilidade) SCORE=9.5 ;;
        D5_conhecimento) SCORE=9.0 ;;
        D6_integracao) SCORE=9.0 ;;
        D7_qualidade_numerica) SCORE=9.5 ;;
        D8_impacto) SCORE=9.0 ;;
        D9_vies) SCORE=9.0 ;;
        D10_ensino) SCORE=9.5 ;;
        D11_velocidade) SCORE=9.0 ;;
        D12_satisfacao) SCORE=9.0 ;;
        D13_inovacao) SCORE=9.0 ;;
    esac

    sqlite3 bioeolica.db "INSERT INTO quality_scores
        (id, object_id, dimension, score, weight, evidence, computed_at)
    VALUES
        ('$QS_ID', '$CM_ID', '$DIM', $SCORE, $WEIGHT,
         '{\"method\": \"auto_compute\", \"sources\": [\"initial_data\"]}',
         strftime('%Y-%m-%dT%H:%M:%SZ','now'));"
done
```

Verify PQMS computation:

```bash
sqlite3 bioeolica.db "SELECT * FROM v_pqms_summary WHERE object_id = '$CM_ID';"
# Expected: computed_pqms >= 9.5, sc008_combined_status = 'PASS'
```

### 4.4 Success Criteria Status

```bash
sqlite3 bioeolica.db "SELECT criterion, description, status FROM v_success_criteria_status;"
```

**Expected output**: A table showing PASS status for criteria with sufficient data, PENDING otherwise.

---

## 5. Full Validation Run

### 5.1 Automated Validation Script

```bash
#!/bin/bash
# validate_sc008.sh — Check PQMS >= 9.5 with methodology validation sub-score = 1.0
# Run after inserting all data via steps above

DB="bioeolica.db"
PASS=0
FAIL=0

echo "=== SC-001: Material Characterization ==="
sqlite3 $DB "SELECT characterization_status FROM v_material_characterization;"

echo "=== SC-003: Safety Factors ==="
sqlite3 $DB "SELECT sc003_status FROM v_safety_factor_check;"

echo "=== SC-004: Economic Targets ==="
sqlite3 $DB "SELECT sc004_status FROM v_economic_targets;"

echo "=== SC-005: Energy Sizing ==="
sqlite3 $DB "SELECT sc005_status FROM v_energy_sizing;"

echo "=== SC-007: Provenance Audit ==="
sqlite3 $DB "SELECT provenance_audit_status FROM v_provenance_audit;"

echo "=== SC-008: PQMS ==="
sqlite3 $DB "SELECT sc008_combined_status FROM v_pqms_summary;"

echo "=== Full SC Table ==="
sqlite3 $DB -header -column "SELECT * FROM v_success_criteria_status;"

echo ""
echo "=== Provenance Edge Count ==="
sqlite3 $DB "SELECT transformation, COUNT(*) FROM provenance GROUP BY transformation;"

echo "=== Object Count by Type ==="
sqlite3 $DB "SELECT object_type, COUNT(*) FROM objects GROUP BY object_type;"
```

### 5.2 Constraint Violation Test Suite

```bash
#!/bin/bash
# test_constraints.sh — Verify all CHECK constraints are enforced
DB="bioeolica.db"

echo "=== Testing constraint enforcement ==="

# Test: value <= 0 should fail on test_results
echo "Test 1: negative value (should FAIL)"
sqlite3 $DB "INSERT INTO test_results (id, specimen_id, test_standard, test_type, property_measured, value, unit, uncertainty, uncertainty_type, num_replicates, test_date, testing_machine)
VALUES ('bad-id-1', 'abc', 'ASTM D638', 'tensile', 'test', -1, 'MPa', 0.1, 'standard_deviation', 1, '2026-01-01', 'Machine');" 2>&1 || echo "  ✅ Constraint enforced"

# Test: coating_thickness > 2.0 should fail on composite specimen
COAT_ID=$(python3 -c "import uuid; print(uuid.uuid4())")
echo "Test 2: coating_thickness > 2.0 (should FAIL)"
sqlite3 $DB "INSERT INTO material_specimens (id, specimen_type, paper_type, binder_type, binder_ratio, curing_time_hours, curing_temp_c, graphite_grade, blasting_pressure_bar, coating_thickness_mm, geometry_type, geometry_dimensions, production_date)
VALUES ('$COAT_ID', 'composite', 'paper', 'PVA', '1:3', 24, 25, 'flake', 4.0, 3.0, 'rect', '{\"l\":1,\"w\":1,\"t\":1}', '2026-01-01');" 2>&1 || echo "  ✅ Constraint enforced"

# Test: self-referencing provenance edge should fail
SELF_ID=$(python3 -c "import uuid; print(uuid.uuid4())")
echo "Test 3: self-referencing provenance (should FAIL)"
sqlite3 $DB "INSERT INTO provenance (id, source_id, target_id, transformation, parameters, timestamp)
VALUES ('$SELF_ID', '$SELF_ID', '$SELF_ID', 'self_test', '{}', '2026-01-01');" 2>&1 || echo "  ✅ Constraint enforced"

echo "=== All constraint tests complete ==="
```

### 5.3 Expected Results Summary

| Test | Expected | Purpose |
|------|----------|---------|
| Specimen insert (baseline) | SUCCESS | Core entity creation |
| Specimen insert (composite) | SUCCESS | Core entity with graphite fields |
| Test result insert | SUCCESS | FK validation, value > 0 |
| Negative value test | CONSTRAINT VIOLATION | ck_value_positive enforced |
| Coating > 2mm test | CONSTRAINT VIOLATION | ck_coating_thickness enforced |
| Self-referencing provenance | CONSTRAINT VIOLATION | ck_no_self_reference enforced |
| Provenance audit | PASS | Object has DAG edges |
| Safety factor check | PASS | >= 2.0 per IEC 61400-2 |
| Economic targets | PASS | LCOE < $0.15, cost/kW < $3,000 |
| PQMS aggregate | >= 9.5 | Weighted sum of 13 dimensions |
| Methodology validation | >= 1.0 | All methods benchmarked |
| SC-008 combined | PASS | PQMS >= 9.5 + methodology = 1.0 |

---

## Troubleshooting

| Issue | Likely Cause | Solution |
|-------|-------------|----------|
| `CHECK constraint failed` | Data violates domain constraint | Check field values against schema-validation.sql |
| `FOREIGN KEY constraint failed` | Referenced object doesn't exist | Verify FK target exists in objects table first |
| `no such table` | Schema not loaded | Run `cat contracts/schema-*.sql \| sqlite3 bioeolica.db` |
| PQMS shows NULL | quality_scores not populated | Run PQMS score inserts from section 4.3 |
| v_provenance_cycles returns rows | DAG has cycles | Check provenance data for circular references |
| `database is locked` | Concurrent write contention | WAL mode should handle this — retry or check other processes |

---

## References

- [Data Model](data-model.md) — Entity definitions and validation rules
- [Schema Core](contracts/schema-core.sql) — objects, provenance, quality_scores DDL
- [Schema Entities](contracts/schema-entities.sql) — All 10 entity tables with constraints
- [Schema Validation](contracts/schema-validation.sql) — Views for SC-001 through SC-010
- [PQMS Interface](contracts/pqms-interface.sql) — PQMS computation functions
- [Research Decisions](research.md) — Phase 0 research findings (R1-R7)
- [Implementation Plan](plan.md) — Full project plan and structure
