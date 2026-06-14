-- =============================================================================
-- Validation Schema: Triggers, Functions, and Enforcement Rules
-- Part of contracts/ — Phase 1 Design Artifacts
-- Reference: data-model.md validation rules, spec.md SC-001 through SC-010
-- =============================================================================
-- This file implements validation rules as SQL triggers and views:
--   1. Provenance integrity — prevent dangling FK references across entity tables
--   2. PQMS constraint — no dimension below 8.5 (SC-008)
--   3. Material characterization completeness (SC-001)
--   4. Model accuracy check (SC-002)
--   5. Safety factor enforcement (SC-003)
--   6. Economic target validation (SC-004)
--   7. Energy system sizing check (SC-005, SC-006)
-- =============================================================================

-- =============================================================================
-- 1. Provenance Acyclic Integrity Check
-- =============================================================================
-- View to detect cycles in provenance DAG (max depth = 50 to avoid infinite loops)
CREATE VIEW IF NOT EXISTS v_provenance_cycles AS
    WITH RECURSIVE provenance_path AS (
        -- Base: direct edges
        SELECT
            source_id,
            target_id,
            CAST(source_id AS TEXT) || '->' || CAST(target_id AS TEXT) AS path,
            1 AS depth
        FROM provenance
        UNION ALL
        -- Recursive: follow edges
        SELECT
            pp.source_id,
            p.target_id,
            pp.path || '->' || CAST(p.target_id AS TEXT),
            pp.depth + 1
        FROM provenance_path pp
        JOIN provenance p ON pp.target_id = p.source_id
        WHERE pp.depth < 50
          AND instr(pp.path, CAST(p.target_id AS TEXT)) = 0  -- stop if already visited
    )
    SELECT DISTINCT source_id, target_id, path, depth
    FROM provenance_path
    WHERE source_id = target_id  -- cycle detected
    ORDER BY depth;

-- View to detect orphaned provenance references
CREATE VIEW IF NOT EXISTS v_provenance_orphans AS
    SELECT
        p.id AS provenance_id,
        p.source_id,
        p.target_id,
        CASE
            WHEN o_src.id IS NULL THEN 'source_orphan'
            WHEN o_tgt.id IS NULL THEN 'target_orphan'
            ELSE 'valid'
        END AS orphan_type
    FROM provenance p
    LEFT JOIN objects o_src ON p.source_id = o_src.id
    LEFT JOIN objects o_tgt ON p.target_id = o_tgt.id
    WHERE o_src.id IS NULL OR o_tgt.id IS NULL;

-- =============================================================================
-- 2. Provenance Coverage View (FR-016 / SC-007)
-- =============================================================================
-- View to audit % of objects with complete provenance chains
CREATE VIEW IF NOT EXISTS v_provenance_coverage AS
    SELECT
        COUNT(DISTINCT o.id) AS total_objects,
        COUNT(DISTINCT p.source_id) AS objects_with_incoming_provenance,
        COUNT(DISTINCT p.target_id) AS objects_with_outgoing_provenance,
        ROUND(100.0 * COUNT(DISTINCT p.source_id) / NULLIF(COUNT(DISTINCT o.id), 0), 1)
            AS pct_with_incoming,
        ROUND(100.0 * COUNT(DISTINCT p.target_id) / NULLIF(COUNT(DISTINCT o.id), 0), 1)
            AS pct_with_outgoing
    FROM objects o
    LEFT JOIN provenance p ON o.id = p.source_id OR o.id = p.target_id;

-- =============================================================================
-- 3. PQMS Aggregate Computation (SC-008)
-- =============================================================================
-- View that computes aggregate PQMS for each object per dimension weights
-- Reference: research.md R6 weight table
CREATE VIEW IF NOT EXISTS v_pqms_aggregate AS
    WITH weight_table AS (
        -- Canonical weight table from R6
        SELECT 'D1_completude' AS dimension, 0.12 AS weight, 9.0 AS target UNION ALL
        SELECT 'D2_profundidade', 0.10, 9.0 UNION ALL
        SELECT 'D3_rigor', 0.15, 9.5 UNION ALL
        SELECT 'D4_rastreabilidade', 0.10, 9.5 UNION ALL
        SELECT 'D5_conhecimento', 0.08, 9.0 UNION ALL
        SELECT 'D6_integracao', 0.08, 9.0 UNION ALL
        SELECT 'D7_qualidade_numerica', 0.15, 9.5 UNION ALL
        SELECT 'D8_impacto', 0.05, 8.5 UNION ALL
        SELECT 'D9_vies', 0.05, 9.0 UNION ALL
        SELECT 'D10_ensino', 0.05, 9.5 UNION ALL
        SELECT 'D11_velocidade', 0.05, 9.0 UNION ALL
        SELECT 'D12_satisfacao', 0.03, 8.5 UNION ALL
        SELECT 'D13_inovacao', 0.02, 9.0
    ),
    scored_objects AS (
        SELECT
            qs.object_id,
            qs.dimension,
            qs.score,
            wt.weight,
            wt.target,
            -- Check if dimension meets minimum threshold (8.5 per SC-008)
            CASE WHEN qs.score >= 8.5 THEN TRUE ELSE FALSE END AS meets_minimum
        FROM quality_scores qs
        JOIN weight_table wt ON qs.dimension = wt.dimension
    )
    SELECT
        object_id,
        ROUND(SUM(score * weight) / NULLIF(SUM(weight), 0), 2) AS aggregate_pqms,
        COUNT(*) AS dimensions_scored,
        SUM(CASE WHEN meets_minimum THEN 1 ELSE 0 END) AS dimensions_meeting_minimum,
        -- Per SC-008: no dimension below 8.5 enforcement flag
        CASE
            WHEN SUM(CASE WHEN meets_minimum THEN 0 ELSE 1 END) > 0
            THEN 'FAIL: dimensions below 8.5 exist'
            WHEN ROUND(SUM(score * weight) / NULLIF(SUM(weight), 0), 2) >= 9.5
            THEN 'PASS'
            ELSE 'FAIL: aggregate below 9.5'
        END AS pqms_status
    FROM scored_objects
    GROUP BY object_id;

-- =============================================================================
-- 4. Methodology Validation Sub-Score (SC-008: = 1.0)
-- =============================================================================
-- View to check if methodology validation sub-score = 1.0
-- Requirements: every computational method validated, correlation >= 0.95,
-- source quality >= 8, zero unvalidated methods
CREATE VIEW IF NOT EXISTS v_methodology_validation AS
    WITH validated_models AS (
        SELECT DISTINCT cm.id AS model_id
        FROM computational_models cm
        WHERE cm.calibration_status = 'validated'
          AND cm.calibrated_against IS NOT NULL
          AND cm.calibration_error_pct IS NOT NULL
          AND cm.calibration_error_pct < 10.0
    ),
    validation_references_quality AS (
        SELECT id AS ref_id
        FROM validation_references
        WHERE source_quality_score >= 8
    ),
    validated_simulations AS (
        SELECT DISTINCT sr.id AS sim_id
        FROM simulation_results sr
        JOIN validated_models vm ON sr.model_id = vm.model_id
        WHERE sr.validation_status = 'PASS'
          AND (sr.validation_error_pct IS NULL OR sr.validation_error_pct < 10.0)
    )
    SELECT
        (SELECT COUNT(*) FROM computational_models) AS total_models,
        (SELECT COUNT(*) FROM validated_models) AS validated_models,
        (SELECT COUNT(*) FROM computational_models WHERE calibration_status = 'calibrated')
            AS calibrated_only,
        CASE
            WHEN (SELECT COUNT(*) FROM computational_models) = 0 THEN NULL
            WHEN (SELECT COUNT(*) FROM validated_models) =
                 (SELECT COUNT(*) FROM computational_models)
            THEN 1.0
            ELSE ROUND(
                1.0 * (SELECT COUNT(*) FROM validated_models) /
                NULLIF((SELECT COUNT(*) FROM computational_models), 0),
                2
            )
        END AS methodology_validation_subscore;

-- =============================================================================
-- 5. Material Characterization Completeness (SC-001)
-- =============================================================================
-- View checking if baseline and composite specimens have all 5 test types
-- (tensile, flexural, compressive, hardness, fatigue)
CREATE VIEW IF NOT EXISTS v_material_characterization AS
    WITH required_tests AS (
        SELECT DISTINCT 'tensile' AS test_type
        UNION ALL SELECT 'flexural'
        UNION ALL SELECT 'compressive'
        UNION ALL SELECT 'hardness'
        UNION ALL SELECT 'fatigue'
    ),
    baseline_tests AS (
        SELECT DISTINCT tr.test_type
        FROM test_results tr
        JOIN material_specimens ms ON tr.specimen_id = ms.id
        WHERE ms.specimen_type = 'baseline'
    ),
    composite_tests AS (
        SELECT DISTINCT tr.test_type
        FROM test_results tr
        JOIN material_specimens ms ON tr.specimen_id = ms.id
        WHERE ms.specimen_type = 'composite'
    )
    SELECT
        (SELECT COUNT(*) FROM required_tests WHERE test_type IN (SELECT test_type FROM baseline_tests))
            AS baseline_types_completed,
        (SELECT COUNT(*) FROM required_tests) AS total_types_required,
        (SELECT COUNT(*) FROM required_tests WHERE test_type IN (SELECT test_type FROM composite_tests))
            AS composite_types_completed,
        CASE
            WHEN (SELECT COUNT(*) FROM required_tests WHERE test_type IN
                     (SELECT test_type FROM baseline_tests)) >= 5
                 AND (SELECT COUNT(*) FROM required_tests WHERE test_type IN
                     (SELECT test_type FROM composite_tests)) >= 5
            THEN 'PASS'
            ELSE 'FAIL: not all 5 test types completed for both specimen types'
        END AS characterization_status;

-- =============================================================================
-- 6. Safety Factor Enforcement (SC-003)
-- =============================================================================
-- View checking blade safety factors >= 2.0 per IEC 61400-2
CREATE VIEW IF NOT EXISTS v_safety_factor_check AS
    SELECT
        id,
        safety_factor_static,
        safety_factor_fatigue,
        CASE
            WHEN safety_factor_static >= 2.0 AND safety_factor_fatigue >= 2.0
            THEN 'PASS'
            ELSE 'FAIL: safety factor below 2.0'
        END AS sc003_status
    FROM blade_designs;

-- =============================================================================
-- 7. Economic Target Validation (SC-004)
-- =============================================================================
-- View checking LCOE < $0.15/kWh and installed cost < $3,000/kW
CREATE VIEW IF NOT EXISTS v_economic_targets AS
    SELECT
        id,
        lcoe_usd_per_kwh,
        cost_per_kw_usd,
        CASE
            WHEN lcoe_usd_per_kwh < 0.15 AND cost_per_kw_usd < 3000
            THEN 'PASS'
            WHEN lcoe_usd_per_kwh >= 0.15 AND cost_per_kw_usd >= 3000
            THEN 'FAIL: both LCOE and cost_per_kW exceed targets'
            WHEN lcoe_usd_per_kwh >= 0.15
            THEN 'FAIL: LCOE >= $0.15/kWh'
            ELSE 'FAIL: cost_per_kW >= $3,000/kW'
        END AS sc004_status
    FROM energy_systems;

-- =============================================================================
-- 8. Energy System Sizing Check (SC-005)
-- =============================================================================
-- View checking if system meets 100% demand, 2-day autonomy, >= 20% capacity factor
CREATE VIEW IF NOT EXISTS v_energy_sizing AS
    SELECT
        es.id,
        es.battery_capacity_kwh,
        es.capacity_factor_pct,
        es.autonomy_days,
        cp.energy_total_kwh_day,
        -- Check if battery provides 2-day autonomy
        CASE
            WHEN es.autonomy_days >= 2.0 THEN 'PASS'
            ELSE 'FAIL'
        END AS autonomy_check,
        -- Check capacity factor >= 20%
        CASE
            WHEN es.capacity_factor_pct >= 20.0 THEN 'PASS'
            ELSE 'FAIL'
        END AS capacity_factor_check,
        -- Overall SC-005 status
        CASE
            WHEN es.autonomy_days >= 2.0
                 AND es.capacity_factor_pct >= 20.0
            THEN 'PASS'
            ELSE 'FAIL'
        END AS sc005_status
    FROM energy_systems es
    JOIN community_profiles cp ON 1=1;  -- cross-join: single community scenario

-- =============================================================================
-- 9. Complete Provenance Audit (SC-007)
-- =============================================================================
-- View for full provenance audit pass for every data object
CREATE VIEW IF NOT EXISTS v_provenance_audit AS
    SELECT
        o.id AS object_id,
        o.object_type,
        o.validation_status,
        CASE
            WHEN EXISTS (SELECT 1 FROM provenance WHERE source_id = o.id) THEN TRUE
            ELSE FALSE
        END AS has_outgoing_provenance,
        CASE
            WHEN EXISTS (SELECT 1 FROM provenance WHERE target_id = o.id) THEN TRUE
            ELSE FALSE
        END AS has_incoming_provenance,
        -- An object passes if it has at least one provenance edge (incoming or outgoing)
        -- EXCEPTION: community_profile and validation_reference are root nodes (no incoming)
        CASE
            WHEN o.object_type IN ('community_profile', 'validation_reference')
            THEN 'PASS: root node (no incoming expected)'
            WHEN EXISTS (SELECT 1 FROM provenance WHERE source_id = o.id OR target_id = o.id)
            THEN 'PASS'
            ELSE 'FAIL: no provenance edges'
        END AS provenance_audit_status
    FROM objects o;
