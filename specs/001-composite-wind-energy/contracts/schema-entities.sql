-- =============================================================================
-- Entity Schema: Composite Biomaterial for Wind Energy
-- Part of contracts/ — Phase 1 Design Artifacts
-- Reference: data-model.md (all 10 entities)
-- =============================================================================
-- This file defines the 10 entity-specific tables, each with:
--   - Complete field definitions matching data-model.md
--   - Foreign key constraints referencing objects(id)
--   - Validation CHECK constraints where applicable
--   - Indexes for query performance
-- =============================================================================

-- =============================================================================
-- 1. Material Specimen
-- =============================================================================
CREATE TABLE IF NOT EXISTS material_specimens (
    id                      TEXT PRIMARY KEY,    -- UUID v4 (also FK → objects.id)
    specimen_type           TEXT NOT NULL,       -- 'baseline' OR 'composite'
    paper_type              TEXT NOT NULL,       -- e.g., 'newspaper', 'office_paper', 'mixed'
    binder_type             TEXT NOT NULL,       -- e.g., 'PVA'
    binder_ratio            TEXT NOT NULL,       -- e.g., '1:3' (glue:water)
    curing_time_hours       REAL NOT NULL,       -- Curing duration in hours
    curing_temp_c           REAL NOT NULL,       -- Curing temperature in Celsius
    graphite_grade          TEXT,                -- NULL for baseline specimens
    graphite_particle_size_um REAL,              -- NULL for baseline (mean particle size in microns)
    blasting_pressure_bar   REAL,                -- NULL for baseline
    standoff_distance_mm    REAL,                -- NULL for baseline
    coating_thickness_mm    REAL,                -- NULL for baseline
    geometry_type           TEXT NOT NULL,       -- 'dogbone', 'rectangular', etc.
    geometry_dimensions     TEXT NOT NULL,       -- JSON: {"length":?, "width":?, "thickness":?}
    production_date         TEXT NOT NULL,       -- ISO 8601 date
    production_notes        TEXT,                -- Free-text notes
    storage_conditions      TEXT,                -- e.g., '25°C, 50% RH'
    quality_score           REAL,                -- 0-10 (NULL until computed)

    FOREIGN KEY (id) REFERENCES objects(id)
        ON DELETE CASCADE ON UPDATE CASCADE,

    -- Validation: specimen_type must be valid
    CONSTRAINT ck_specimen_type CHECK (specimen_type IN ('baseline', 'composite')),

    -- Validation: composite specimens require graphite fields
    CONSTRAINT ck_composite_requires_graphite CHECK (
        (specimen_type = 'baseline') OR
        (specimen_type = 'composite' AND
         graphite_grade IS NOT NULL AND
         blasting_pressure_bar IS NOT NULL AND
         coating_thickness_mm IS NOT NULL)
    ),

    -- Validation: coating thickness process limit
    CONSTRAINT ck_coating_thickness CHECK (
        coating_thickness_mm IS NULL OR
        coating_thickness_mm <= 2.0
    ),

    -- Validation: curing parameters must be positive
    CONSTRAINT ck_curing_time CHECK (curing_time_hours > 0),
    CONSTRAINT ck_curing_temp CHECK (curing_temp_c > -50 AND curing_temp_c < 200),

    -- Validation: blasting parameters (when present)
    CONSTRAINT ck_blasting_pressure CHECK (
        blasting_pressure_bar IS NULL OR
        (blasting_pressure_bar >= 1 AND blasting_pressure_bar <= 10)
    ),
    CONSTRAINT ck_standoff_distance CHECK (
        standoff_distance_mm IS NULL OR
        (standoff_distance_mm >= 10 AND standoff_distance_mm <= 500)
    ),
    CONSTRAINT ck_particle_size CHECK (
        graphite_particle_size_um IS NULL OR
        graphite_particle_size_um > 0
    ),

    -- Validation: quality_score range
    CONSTRAINT ck_quality_score CHECK (
        quality_score IS NULL OR (quality_score >= 0 AND quality_score <= 10)
    )
);

CREATE INDEX idx_specimens_type ON material_specimens(specimen_type);
CREATE INDEX idx_specimens_paper ON material_specimens(paper_type);
CREATE INDEX idx_specimens_date ON material_specimens(production_date);

-- =============================================================================
-- 2. Test Result
-- =============================================================================
CREATE TABLE IF NOT EXISTS test_results (
    id                  TEXT PRIMARY KEY,        -- UUID v4 (also FK → objects.id)
    specimen_id         TEXT NOT NULL,           -- FK → material_specimens.id
    test_standard       TEXT NOT NULL,           -- e.g., 'ASTM D638', 'ASTM D790'
    test_type           TEXT NOT NULL,           -- ENUM: tensile, flexural, compressive, hardness, fatigue, impact
    property_measured   TEXT NOT NULL,           -- e.g., 'tensile_strength', 'elastic_modulus'
    value               REAL NOT NULL,           -- Measured value (must be > 0)
    unit                TEXT NOT NULL,           -- e.g., 'MPa', 'GPa', 'Shore D'
    uncertainty         REAL NOT NULL,           -- Measurement uncertainty (±) (>= 0 AND < value)
    uncertainty_type    TEXT NOT NULL,           -- ENUM: standard_deviation, confidence_interval, instrument_error
    num_replicates      INTEGER NOT NULL,        -- Number of replicate tests (>= 1)
    test_date           TEXT NOT NULL,           -- ISO 8601 date
    testing_machine     TEXT NOT NULL,           -- Equipment used
    operator            TEXT,                    -- Operator name/ID
    temperature_c       REAL,                    -- Test ambient temperature
    humidity_pct        REAL,                    -- Test ambient humidity (0-100)
    failure_mode        TEXT,                    -- e.g., 'brittle_fracture', 'delamination'
    notes               TEXT,                    -- Free-text notes
    raw_data_file       TEXT,                    -- Path to raw data file
    validation_status   TEXT DEFAULT 'PENDING',  -- PENDING, PASS, FAIL

    FOREIGN KEY (id) REFERENCES objects(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (specimen_id) REFERENCES material_specimens(id)
        ON DELETE RESTRICT ON UPDATE CASCADE,

    -- Validation: value must be positive
    CONSTRAINT ck_value_positive CHECK (value > 0),

    -- Validation: uncertainty must be non-negative and less than value
    CONSTRAINT ck_uncertainty_range CHECK (
        uncertainty >= 0 AND uncertainty < value
    ),

    -- Validation: num_replicates >= 1
    CONSTRAINT ck_replicates CHECK (num_replicates >= 1),

    -- Validation: test_type
    CONSTRAINT ck_test_type CHECK (
        test_type IN ('tensile', 'flexural', 'compressive', 'hardness', 'fatigue', 'impact')
    ),

    -- Validation: uncertainty_type
    CONSTRAINT ck_uncertainty_type CHECK (
        uncertainty_type IN ('standard_deviation', 'confidence_interval', 'instrument_error')
    ),

    -- Validation: humidity (when present)
    CONSTRAINT ck_humidity CHECK (
        humidity_pct IS NULL OR (humidity_pct >= 0 AND humidity_pct <= 100)
    ),

    -- Validation: temperature (when present)
    CONSTRAINT ck_temperature CHECK (
        temperature_c IS NULL OR (temperature_c > -100 AND temperature_c < 200)
    ),

    -- Validation: validation_status
    CONSTRAINT ck_validation_status CHECK (
        validation_status IN ('PENDING', 'PASS', 'FAIL')
    )
);

CREATE INDEX idx_test_specimen ON test_results(specimen_id);
CREATE INDEX idx_test_type ON test_results(test_type);
CREATE INDEX idx_test_standard ON test_results(test_standard);
CREATE INDEX idx_test_property ON test_results(property_measured);
CREATE INDEX idx_test_date ON test_results(test_date);

-- =============================================================================
-- 3. Microstructure Image
-- =============================================================================
CREATE TABLE IF NOT EXISTS microstructure_images (
    id                  TEXT PRIMARY KEY,        -- UUID v4 (also FK → objects.id)
    specimen_id         TEXT NOT NULL,           -- FK → material_specimens.id
    image_type          TEXT NOT NULL,           -- ENUM: SEM, optical
    magnification       REAL NOT NULL,           -- Magnification factor (> 0)
    imaging_mode        TEXT,                    -- e.g., 'SE', 'BSE' (for SEM)
    analyzed_region     TEXT,                    -- e.g., 'cross_section', 'surface_top', 'interface'
    measured_features   TEXT,                    -- JSON: {particle_penetration_um, porosity_pct,
                                                 --         coating_thickness_um}
    image_file          TEXT NOT NULL,           -- Path to image file
    analysis_software   TEXT,                    -- Software used for measurement
    notes               TEXT,                    -- Free-text

    FOREIGN KEY (id) REFERENCES objects(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (specimen_id) REFERENCES material_specimens(id)
        ON DELETE RESTRICT ON UPDATE CASCADE,

    -- Validation: image_type
    CONSTRAINT ck_image_type CHECK (image_type IN ('SEM', 'optical')),

    -- Validation: magnification must be positive
    CONSTRAINT ck_magnification CHECK (magnification > 0)
);

CREATE INDEX idx_microimage_specimen ON microstructure_images(specimen_id);
CREATE INDEX idx_microimage_type ON microstructure_images(image_type);

-- =============================================================================
-- 4. Computational Model
-- =============================================================================
CREATE TABLE IF NOT EXISTS computational_models (
    id                      TEXT PRIMARY KEY,    -- UUID v4 (also FK → objects.id)
    model_type              TEXT NOT NULL,       -- ENUM: FEM, CFD, analytical, multi_scale, PINN
    domain                  TEXT NOT NULL,       -- ENUM: structural, fluid, thermal, coupled
    solver_software         TEXT NOT NULL,       -- e.g., 'CalculiX', 'OpenFOAM', 'Python'
    solver_version          TEXT NOT NULL,       -- Software version
    mesh_type               TEXT,                -- e.g., 'tetrahedral', 'hexahedral', 'polyhedral'
    mesh_num_elements       INTEGER,             -- Element count (> 0 when present)
    mesh_num_nodes          INTEGER,             -- Node count (> 0 when present)
    boundary_conditions     TEXT NOT NULL,       -- JSON: BC definition
    material_model          TEXT NOT NULL,       -- e.g., 'linear_elastic', 'von_mises_plastic'
    material_properties     TEXT NOT NULL,       -- JSON: material property values
    solver_parameters       TEXT,                -- JSON: solver settings, convergence criteria
    calibration_status      TEXT DEFAULT 'uncalibrated',  -- ENUM: uncalibrated, calibrated, validated
    calibrated_against      TEXT,                -- FK → test_results.id OR validation_references.id
    calibration_error_pct   REAL,                -- Relative error after calibration
    input_files             TEXT,                -- JSON: paths to input files
    notes                   TEXT,                -- Free-text

    FOREIGN KEY (id) REFERENCES objects(id)
        ON DELETE CASCADE ON UPDATE CASCADE,

    -- Validation: model_type
    CONSTRAINT ck_model_type CHECK (
        model_type IN ('FEM', 'CFD', 'analytical', 'multi_scale', 'PINN')
    ),

    -- Validation: domain
    CONSTRAINT ck_domain CHECK (
        domain IN ('structural', 'fluid', 'thermal', 'coupled')
    ),

    -- Validation: calibration_status
    CONSTRAINT ck_calibration_status CHECK (
        calibration_status IN ('uncalibrated', 'calibrated', 'validated')
    ),

    -- Validation: calibrated/validated requires calibrated_against and error_pct
    CONSTRAINT ck_calibrated_requires_ref CHECK (
        calibration_status = 'uncalibrated' OR
        (calibrated_against IS NOT NULL AND calibration_error_pct IS NOT NULL)
    ),

    -- Validation: calibration error < 10% (per SC-002)
    CONSTRAINT ck_calibration_error CHECK (
        calibration_error_pct IS NULL OR
        calibration_error_pct < 10.0
    ),

    -- Validation: mesh element and node counts (when present)
    CONSTRAINT ck_mesh_elements CHECK (
        mesh_num_elements IS NULL OR mesh_num_elements > 0
    ),
    CONSTRAINT ck_mesh_nodes CHECK (
        mesh_num_nodes IS NULL OR mesh_num_nodes > 0
    )
);

CREATE INDEX idx_cm_type ON computational_models(model_type);
CREATE INDEX idx_cm_domain ON computational_models(domain);
CREATE INDEX idx_cm_calibration ON computational_models(calibration_status);
CREATE INDEX idx_cm_software ON computational_models(solver_software);

-- =============================================================================
-- 5. Simulation Result
-- =============================================================================
CREATE TABLE IF NOT EXISTS simulation_results (
    id                          TEXT PRIMARY KEY,-- UUID v4 (also FK → objects.id)
    model_id                    TEXT NOT NULL,   -- FK → computational_models.id
    run_timestamp               TEXT NOT NULL,   -- ISO 8601
    convergence_metric          REAL,            -- Residual or convergence value
    convergence_threshold       REAL,            -- Target threshold
    mesh_convergence_pct        REAL,            -- Variation between mesh refinements
    output_quantities           TEXT NOT NULL,   -- JSON: {stress_max, strain_max, displacement_max, ...}
    output_files                TEXT,            -- JSON: paths to output files
    validation_status           TEXT DEFAULT 'PENDING',  -- PENDING, PASS, FAIL
    validation_vs_experiment    TEXT,            -- FK → test_results.id (if validated)
    validation_error_pct        REAL,            -- Error vs. experimental reference
    uncertainty_quantification  TEXT,            -- Method used: Monte_Carlo, interval, perturbation, etc.
    notes                       TEXT,            -- Free-text

    FOREIGN KEY (id) REFERENCES objects(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (model_id) REFERENCES computational_models(id)
        ON DELETE RESTRICT ON UPDATE CASCADE,

    -- Validation: convergence_metric (when present)
    CONSTRAINT ck_convergence_metric CHECK (
        convergence_metric IS NULL OR convergence_metric >= 0
    ),

    -- Validation: convergence_threshold (when present)
    CONSTRAINT ck_convergence_threshold CHECK (
        convergence_threshold IS NULL OR convergence_threshold >= 0
    ),

    -- Validation: mesh_convergence (when present)
    CONSTRAINT ck_mesh_convergence CHECK (
        mesh_convergence_pct IS NULL OR mesh_convergence_pct >= 0
    ),

    -- Validation: validation_error (when present)
    CONSTRAINT ck_validation_error CHECK (
        validation_error_pct IS NULL OR validation_error_pct >= 0
    ),

    -- Validation: validation_status
    CONSTRAINT ck_validation_status CHECK (
        validation_status IN ('PENDING', 'PASS', 'FAIL')
    )
);

CREATE INDEX idx_sim_model ON simulation_results(model_id);
CREATE INDEX idx_sim_validation ON simulation_results(validation_status);
CREATE INDEX idx_sim_timestamp ON simulation_results(run_timestamp);

-- =============================================================================
-- 6. Blade Design
-- =============================================================================
CREATE TABLE IF NOT EXISTS blade_designs (
    id                      TEXT PRIMARY KEY,    -- UUID v4 (also FK → objects.id)
    blade_length_m          REAL NOT NULL,       -- Blade length in meters (> 0)
    airfoil_profile         TEXT NOT NULL,       -- Profile identifier(s)
    num_blades              INTEGER NOT NULL,    -- Number of blades (>= 2)
    material_id             TEXT NOT NULL,       -- FK → material_specimens.id
    structural_layup        TEXT,                -- Layup description
    safety_factor_static    REAL NOT NULL,       -- Static safety factor (>= 2.0 per IEC 61400-2, SC-003)
    safety_factor_fatigue   REAL NOT NULL,       -- Fatigue safety factor (>= 2.0)
    design_wind_speed_ms    REAL NOT NULL,       -- Rated wind speed (> 0)
    extreme_wind_speed_ms   REAL NOT NULL,       -- Survival gust wind speed (> design speed)
    mass_kg                 REAL,                -- Blade mass estimate (> 0 when present)
    geometry_file           TEXT,                -- CAD file path
    created_at              TEXT NOT NULL,       -- ISO 8601

    FOREIGN KEY (id) REFERENCES objects(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (material_id) REFERENCES material_specimens(id)
        ON DELETE RESTRICT ON UPDATE CASCADE,

    -- Validation: physical constraints
    CONSTRAINT ck_blade_length CHECK (blade_length_m > 0 AND blade_length_m < 200),
    CONSTRAINT ck_num_blades CHECK (num_blades >= 2 AND num_blades <= 6),
    CONSTRAINT ck_safety_factor_static CHECK (safety_factor_static >= 2.0),
    CONSTRAINT ck_safety_factor_fatigue CHECK (safety_factor_fatigue >= 2.0),
    CONSTRAINT ck_design_wind CHECK (design_wind_speed_ms > 0 AND design_wind_speed_ms < 100),
    CONSTRAINT ck_extreme_wind CHECK (extreme_wind_speed_ms > design_wind_speed_ms),
    CONSTRAINT ck_mass CHECK (mass_kg IS NULL OR mass_kg > 0)
);

CREATE INDEX idx_blade_material ON blade_designs(material_id);

-- =============================================================================
-- 7. Wind Turbine System
-- =============================================================================
CREATE TABLE IF NOT EXISTS wind_turbine_systems (
    id                  TEXT PRIMARY KEY,        -- UUID v4 (also FK → objects.id)
    turbine_type        TEXT NOT NULL,           -- ENUM: VAWT, Archimedes
    configuration       TEXT,                    -- e.g., 'H-rotor Darrieus', 'helical 3-blade'
    rated_power_kw      REAL NOT NULL,           -- Rated power (> 0)
    rotor_diameter_m    REAL NOT NULL,           -- Rotor diameter (> 0)
    tower_height_m      REAL NOT NULL,           -- Hub/tower height (> 0)
    swept_area_m2       REAL NOT NULL,           -- Rotor swept area (> 0)
    cut_in_speed_ms     REAL NOT NULL,           -- Minimum operational wind (> 0)
    cut_out_speed_ms    REAL NOT NULL,           -- Maximum operational wind (> cut_in)
    rated_wind_speed_ms REAL NOT NULL,           -- Wind speed at rated power (> cut_in, < cut_out)
    control_type        TEXT,                    -- e.g., 'passive_stall', 'furling', 'electronic'
    blade_design_id     TEXT NOT NULL,           -- FK → blade_designs.id
    created_at          TEXT NOT NULL,           -- ISO 8601

    FOREIGN KEY (id) REFERENCES objects(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (blade_design_id) REFERENCES blade_designs(id)
        ON DELETE RESTRICT ON UPDATE CASCADE,

    -- Validation: turbine_type
    CONSTRAINT ck_turbine_type CHECK (
        turbine_type IN ('VAWT', 'Archimedes')
    ),

    -- Validation: physical constraints
    CONSTRAINT ck_rated_power CHECK (rated_power_kw > 0 AND rated_power_kw < 10000),
    CONSTRAINT ck_rotor_diameter CHECK (rotor_diameter_m > 0 AND rotor_diameter_m < 200),
    CONSTRAINT ck_tower_height CHECK (tower_height_m > 0 AND tower_height_m < 200),
    CONSTRAINT ck_swept_area CHECK (swept_area_m2 > 0),

    -- Validation: wind speed ordering
    CONSTRAINT ck_wind_speed_order CHECK (
        cut_in_speed_ms > 0 AND
        rated_wind_speed_ms > cut_in_speed_ms AND
        cut_out_speed_ms > rated_wind_speed_ms AND
        cut_out_speed_ms < 100
    )
);

CREATE INDEX idx_turbine_type ON wind_turbine_systems(turbine_type);
CREATE INDEX idx_turbine_blade ON wind_turbine_systems(blade_design_id);

-- =============================================================================
-- 8. Energy System
-- =============================================================================
CREATE TABLE IF NOT EXISTS energy_systems (
    id                      TEXT PRIMARY KEY,    -- UUID v4 (also FK → objects.id)
    turbine_id              TEXT NOT NULL,       -- FK → wind_turbine_systems.id
    battery_capacity_kwh    REAL NOT NULL,       -- Total battery storage (> 0)
    battery_type            TEXT,                -- e.g., 'lead_acid', 'lithium_ion'
    inverter_rating_kw      REAL NOT NULL,       -- Inverter power rating (> 0)
    inverter_efficiency_pct REAL NOT NULL,       -- Efficiency (0-100)
    charge_controller_type  TEXT,                -- e.g., 'MPPT', 'PWM'
    distribution_voltage_v  REAL NOT NULL,       -- Distribution voltage (> 0)
    annual_energy_kwh       REAL NOT NULL,       -- Estimated annual production (> 0)
    capacity_factor_pct     REAL NOT NULL,       -- Annual capacity factor (0-100)
    autonomy_days           REAL NOT NULL,       -- Battery autonomy (> 0)
    lcoe_usd_per_kwh        REAL NOT NULL,       -- Levelized cost of energy (> 0)
    installed_cost_usd      REAL NOT NULL,       -- Total installed cost (> 0)
    cost_per_kw_usd         REAL NOT NULL,       -- Cost per rated kW (> 0)
    created_at              TEXT NOT NULL,       -- ISO 8601

    FOREIGN KEY (id) REFERENCES objects(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (turbine_id) REFERENCES wind_turbine_systems(id)
        ON DELETE RESTRICT ON UPDATE CASCADE,

    -- Validation: physical and economic constraints
    CONSTRAINT ck_battery_capacity CHECK (battery_capacity_kwh > 0),
    CONSTRAINT ck_inverter_rating CHECK (inverter_rating_kw > 0),
    CONSTRAINT ck_inverter_efficiency CHECK (
        inverter_efficiency_pct > 0 AND inverter_efficiency_pct <= 100
    ),
    CONSTRAINT ck_distribution_voltage CHECK (distribution_voltage_v > 0 AND distribution_voltage_v < 1000),
    CONSTRAINT ck_annual_energy CHECK (annual_energy_kwh > 0),
    CONSTRAINT ck_capacity_factor CHECK (capacity_factor_pct > 0 AND capacity_factor_pct <= 100),
    CONSTRAINT ck_autonomy CHECK (autonomy_days > 0 AND autonomy_days < 365),
    CONSTRAINT ck_lcoe CHECK (lcoe_usd_per_kwh > 0),
    CONSTRAINT ck_installed_cost CHECK (installed_cost_usd > 0 AND installed_cost_usd < 10000000),
    CONSTRAINT ck_cost_per_kw CHECK (cost_per_kw_usd > 0),

    -- Per SC-004: LCOE < $0.15/kWh, installed cost < $3,000/kW
    CONSTRAINT ck_sc004_lcoe CHECK (lcoe_usd_per_kwh < 0.15),
    CONSTRAINT ck_sc004_cost_per_kw CHECK (cost_per_kw_usd < 3000)
);

CREATE INDEX idx_energy_turbine ON energy_systems(turbine_id);

-- =============================================================================
-- 9. Community Profile
-- =============================================================================
CREATE TABLE IF NOT EXISTS community_profiles (
    id                      TEXT PRIMARY KEY,    -- UUID v4 (also FK → objects.id)
    name                    TEXT NOT NULL,       -- Community name/identifier
    location                TEXT,                -- Geographic location
    num_families            INTEGER NOT NULL,    -- Number of households (> 0)
    total_population        INTEGER,             -- Estimated population (> 0 when present)
    irrigated_area_ha       REAL NOT NULL,       -- Irrigated crop area (>= 0)
    water_demand_l_per_day  REAL NOT NULL,       -- Daily irrigation water demand (>= 0)
    energy_pumping_kwh_day  REAL NOT NULL,       -- Pumping energy (>= 0)
    energy_processing_kwh_day REAL NOT NULL,     -- Food processing energy (>= 0)
    energy_community_kwh_day REAL NOT NULL,      -- Lighting, refrigeration (>= 0)
    energy_total_kwh_day    REAL NOT NULL,       -- Total daily demand (> 0)
    energy_monthly_kwh      TEXT,                -- JSON array: [month1, ..., month12]
    seasonal_variation_pct  REAL,                -- ± seasonal variation (0-100)
    growth_margin_pct       REAL NOT NULL,       -- Projected growth margin (>= 0)
    data_source             TEXT NOT NULL,       -- Source of profile data
    created_at              TEXT NOT NULL,       -- ISO 8601

    FOREIGN KEY (id) REFERENCES objects(id)
        ON DELETE CASCADE ON UPDATE CASCADE,

    -- Validation: demographic constraints
    CONSTRAINT ck_num_families CHECK (num_families > 0 AND num_families < 10000),
    CONSTRAINT ck_population CHECK (
        total_population IS NULL OR total_population > 0
    ),

    -- Validation: energy consistency
    -- total >= sum of components (5% tolerance for rounding/transform losses)
    CONSTRAINT ck_energy_total CHECK (energy_total_kwh_day > 0),
    CONSTRAINT ck_energy_parts_not_negative CHECK (
        energy_pumping_kwh_day >= 0 AND
        energy_processing_kwh_day >= 0 AND
        energy_community_kwh_day >= 0
    ),

    -- Validation: irrigation and water
    CONSTRAINT ck_irrigated_area CHECK (irrigated_area_ha >= 0),
    CONSTRAINT ck_water_demand CHECK (water_demand_l_per_day >= 0),

    -- Validation: margins
    CONSTRAINT ck_seasonal_variation CHECK (
        seasonal_variation_pct IS NULL OR
        (seasonal_variation_pct >= 0 AND seasonal_variation_pct <= 100)
    ),
    CONSTRAINT ck_growth_margin CHECK (
        growth_margin_pct >= 0 AND growth_margin_pct <= 100
    )
);

CREATE INDEX idx_community_name ON community_profiles(name);

-- =============================================================================
-- 10. Validation Reference
-- =============================================================================
CREATE TABLE IF NOT EXISTS validation_references (
    id                      TEXT PRIMARY KEY,    -- UUID v4 (also FK → objects.id)
    source_type             TEXT NOT NULL,       -- ENUM: journal, standard, dataset, thesis, report
    title                   TEXT NOT NULL,       -- Full reference title
    authors                 TEXT NOT NULL,       -- JSON: author list
    year                    INTEGER NOT NULL,    -- Publication year
    doi                     TEXT,                -- DOI identifier
    url                     TEXT,                -- Access URL
    source_quality_score    INTEGER NOT NULL,    -- 0-10 quality assessment
    validation_metric_type  TEXT NOT NULL,       -- e.g., 'correlation', 'rmse', 'max_error'
    validation_threshold    REAL NOT NULL,       -- Acceptance threshold (> 0)
    applicability           TEXT,                -- JSON: domains where applicable
    file_path               TEXT,                -- Local file path if downloaded
    created_at              TEXT NOT NULL,       -- ISO 8601

    FOREIGN KEY (id) REFERENCES objects(id)
        ON DELETE CASCADE ON UPDATE CASCADE,

    -- Validation: source_type
    CONSTRAINT ck_source_type CHECK (
        source_type IN ('journal', 'standard', 'dataset', 'thesis', 'report')
    ),

    -- Validation: year (>= 2000 unless seminal)
    CONSTRAINT ck_year CHECK (year >= 1900 AND year <= 2100),

    -- Validation: source quality (>= 8 for methodology validation sub-score = 1.0)
    CONSTRAINT ck_source_quality CHECK (
        source_quality_score >= 0 AND source_quality_score <= 10
    ),

    -- Validation: threshold must be positive
    CONSTRAINT ck_validation_threshold CHECK (validation_threshold > 0)
);

CREATE INDEX idx_ref_type ON validation_references(source_type);
CREATE INDEX idx_ref_year ON validation_references(year);
CREATE INDEX idx_ref_quality ON validation_references(source_quality_score);
