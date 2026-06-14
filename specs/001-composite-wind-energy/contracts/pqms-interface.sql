-- =============================================================================
-- PQMS Computation Interface: Functions and API Views
-- Part of contracts/ — Phase 1 Design Artifacts
-- Reference: research.md R6, data-model.md PQMS Computation section
-- =============================================================================
-- This file provides the computation layer for PQMS:
--   1. pqms_compute() — Stored procedure to compute quality scores for an object
--   2. v_pqms_summary — Consolidated view with per-dimension breakdown
--   3. pqms_validate_object() — Validates a single object's compliance
-- =============================================================================

-- =============================================================================
-- 1. Temporary table for PQMS dimension weights (canonical reference)
-- =============================================================================
CREATE TABLE IF NOT EXISTS pqms_dimension_weights (
    dimension       TEXT PRIMARY KEY,
    dimension_name  TEXT NOT NULL,           -- Human-readable name
    weight          REAL NOT NULL,           -- 0-1, sum = 1.0 across all 13 dimensions
    target          REAL NOT NULL,           -- Minimum acceptable score for this dimension
    measurement_method TEXT NOT NULL,        -- How to compute/measure this dimension
    description     TEXT NOT NULL,           -- What this dimension evaluates
    critical_domains TEXT,                   -- JSON array of domains this is critical for

    -- Validation
    CONSTRAINT ck_pqms_weight CHECK (weight > 0 AND weight <= 1),
    CONSTRAINT ck_pqms_target CHECK (target >= 0 AND target <= 10)
);

-- Seed the weight table (from research.md R6)
INSERT OR REPLACE INTO pqms_dimension_weights VALUES
    ('D1_completude', 'Material characterization completeness', 0.12, 9.0,
     '% of test types completed (tensile/flexural/compressive/hardness/fatigue)',
     'Cobertura of domains mapeados vs. verificados',
     '["materiais", "mecanica", "fluidos", "eletricidade"]'),
    ('D2_profundidade', 'Multi-scale model depth', 0.10, 9.0,
     'Macro + Meso + Micro all completed',
     'Profundidade M³ — macro, meso, micro por dominio',
     '["mecanica", "fluidos", "materiais", "energia"]'),
    ('D3_rigor', 'VVV rigor', 0.15, 9.5,
     'Cross-code validation, mesh convergence, experimental correlation',
     'VVV aplicado em cada etapa: Verificação, Validação, Certificação',
     '["eletricidade", "construcao", "normativo"]'),
    ('D4_rastreabilidade', 'Data traceability', 0.10, 9.5,
     '% of objects with complete provenance chains',
     'Cada ação tem log 5W1H rastreável',
     '["todos"]'),
    ('D5_conhecimento', 'Knowledge base coverage', 0.08, 9.0,
     'Sources per domain, quality_score >= 7',
     'Fontes coletadas, validadas e indexadas no RAG',
     '["fluidos", "materiais", "termo"]'),
    ('D6_integracao', 'Multi-physics integration', 0.08, 9.0,
     'Coupling between material model and structural model',
     'Análises conectadas via matriz de acoplamento',
     '["todos com acoplamento forte"]'),
    ('D7_qualidade_numerica', 'Numerical accuracy', 0.15, 9.5,
     '< 5% error linear, < 10% nonlinear',
     'Precisão, convergência, fidelidade, robustez',
     '["mecanica", "fluidos", "eletricidade"]'),
    ('D8_impacto', 'Economic impact', 0.05, 8.5,
     'LCOE, installed cost targets met',
     'Custo estimado de falha por fase usando LCC + FMEA',
     '["normativo", "economico"]'),
    ('D9_vies', 'Bias detection', 0.05, 9.0,
     'Independent validation for all S1/S2 domains',
     'Viés não reconhecido identificado e mitigado',
     '["todos"]'),
    ('D10_ensino', 'Method reproducibility', 0.05, 9.5,
     '3 independent results reproducible from stored data',
     'Método claro e reproduzível por terceiro',
     '["todos"]'),
    ('D11_velocidade', 'Environmental validation', 0.02, 9.0,
     'LCA confirms carbon targets',
     'Ciclo concluído em tempo aceitável',
     '["construcao", "economico"]'),
    ('D12_satisfacao', 'Documentation quality', 0.03, 8.5,
     'All artifacts complete, readable',
     'Satisfação do usuário/revisor',
     '["todos"]'),
    ('D13_inovacao', 'Innovation', 0.02, 9.0,
     'Novel contribution beyond state of the art',
     'Contribuição original relevante',
     '["materiais", "construcao"]');

-- =============================================================================
-- 2. PQMS Summary View (consolidated per-object scores)
-- =============================================================================
CREATE VIEW IF NOT EXISTS v_pqms_summary AS
    SELECT
        o.id AS object_id,
        o.object_type,
        o.quality_score AS stored_quality_score,
        agg.aggregate_pqms AS computed_pqms,
        agg.dimensions_scored,
        agg.dimensions_meeting_minimum,
        agg.pqms_status,
        mv.methodology_validation_subscore,
        CASE
            WHEN agg.pqms_status = 'PASS'
                 AND (mv.methodology_validation_subscore IS NULL
                      OR mv.methodology_validation_subscore >= 1.0)
            THEN 'PASS: PQMS >= 9.5 and methodology validated'
            WHEN agg.pqms_status != 'PASS'
            THEN agg.pqms_status
            WHEN mv.methodology_validation_subscore IS NOT NULL
                 AND mv.methodology_validation_subscore < 1.0
            THEN 'FAIL: methodology validation sub-score < 1.0'
            ELSE 'PENDING: insufficient data'
        END AS sc008_combined_status
    FROM objects o
    LEFT JOIN v_pqms_aggregate agg ON o.id = agg.object_id
    LEFT JOIN v_methodology_validation mv ON 1=1;  -- cross-join: single-row view

-- =============================================================================
-- 3. PQMS Per-Dimension Breakdown View
-- =============================================================================
CREATE VIEW IF NOT EXISTS v_pqms_breakdown AS
    SELECT
        qs.object_id,
        qs.dimension,
        qs.score,
        qs.weight,
        qs.evidence,
        qs.computed_at,
        dw.target,
        dw.measurement_method,
        CASE
            WHEN qs.score >= dw.target THEN 'PASS'
            ELSE 'FAIL'
        END AS dimension_status,
        -- Normalized contribution to aggregate
        ROUND(qs.score * qs.weight * 10, 2) AS contribution_pct
    FROM quality_scores qs
    JOIN pqms_dimension_weights dw ON qs.dimension = dw.dimension
    ORDER BY qs.object_id, qs.dimension;

-- =============================================================================
-- 4. PQMS Compute Procedure (update quality_scores for an object)
-- =============================================================================
-- This is a template for the application-layer computation.
-- The actual scoring logic is domain-specific and implemented in Python.
--
-- Algorithm:
--   1. For each dimension D1-D13, compute score based on measurement_method
--   2. Store each (object_id, dimension, score, weight, evidence) in quality_scores
--   3. Compute aggregate = SUM(score * weight) / SUM(weights)
--   4. Update objects.quality_score with aggregate
--   5. If any dimension < 8.5, flag as FAIL (SC-008 constraint)
--
-- Expected calling convention:
--   INSERT INTO quality_scores (id, object_id, dimension, score, weight, evidence, computed_at)
--   VALUES (?, ?, ?, ?, ?, ?, ?);
--   Then refresh objects.quality_score via v_pqms_aggregate.

-- View to identify objects needing PQMS recomputation
CREATE VIEW IF NOT EXISTS v_pqms_pending AS
    SELECT
        o.id AS object_id,
        o.object_type,
        o.created_at,
        o.updated_at,
        CASE
            WHEN o.quality_score IS NULL THEN 'never_computed'
            WHEN EXISTS (
                SELECT 1 FROM quality_scores qs
                WHERE qs.object_id = o.id
                  AND qs.computed_at < o.updated_at
            ) THEN 'stale: object updated after last computation'
            ELSE 'current'
        END AS computation_status
    FROM objects o
    LEFT JOIN quality_scores qs ON o.id = qs.object_id
    GROUP BY o.id
    HAVING computation_status != 'current';

-- =============================================================================
-- 5. Full SC-001 through SC-010 Status View
-- =============================================================================
CREATE VIEW IF NOT EXISTS v_success_criteria_status AS
    SELECT 'SC-001' AS criterion,
           'Hardness +40%, flexural modulus +25%' AS description,
           mc.characterization_status AS status
    FROM v_material_characterization mc
    UNION ALL
    SELECT 'SC-002', 'Model vs experiment < 10% error',
           CASE WHEN (SELECT COUNT(*) FROM computational_models WHERE calibration_error_pct < 10.0)
                     = (SELECT COUNT(*) FROM computational_models WHERE calibration_status != 'uncalibrated')
                THEN 'PASS' ELSE 'PENDING' END
    UNION ALL
    SELECT 'SC-003', 'Blade safety factor >= 2.0 (IEC 61400-2)',
           sc3.sc003_status
    FROM v_safety_factor_check sc3
    UNION ALL
    SELECT 'SC-004', 'LCOE < $0.15/kWh, installed cost < $3,000/kW',
           et.sc004_status
    FROM v_economic_targets et
    UNION ALL
    SELECT 'SC-005', '100% demand met, 2-day autonomy, capacity factor >= 20%',
           es.sc005_status
    FROM v_energy_sizing es
    UNION ALL
    SELECT 'SC-007', 'Full provenance audit pass for every data object',
           CASE WHEN (SELECT COUNT(*) FROM v_provenance_audit WHERE provenance_audit_status = 'FAIL') = 0
                THEN 'PASS' ELSE 'FAIL: orphan objects exist' END
    UNION ALL
    SELECT 'SC-008', 'PQMS >= 9.5, methodology validation sub-score = 1.0',
           COALESCE((SELECT sc008_combined_status FROM v_pqms_summary LIMIT 1), 'PENDING')
    UNION ALL
    SELECT 'SC-009', '3 independent results reproducible',
           'PENDING: requires reproducibility test execution'
    UNION ALL
    SELECT 'SC-010', 'LCA confirms 60% lower carbon vs fiberglass; 80% biodegradable',
           'PENDING: requires LCA study execution';
