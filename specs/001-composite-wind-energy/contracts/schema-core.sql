-- =============================================================================
-- Core Schema: Composite Biomaterial for Wind Energy
-- Part of contracts/ — Phase 1 Design Artifacts
-- Reference: data-model.md, research.md R5
-- =============================================================================
-- This file defines the core infrastructure tables shared by all entities:
--   1. objects         — Universal registry (UUID v4 PK, object_type, quality_score)
--   2. provenance      — DAG edges for W3C PROV-inspired provenance tracking
--   3. quality_scores  — Per-dimension PQMS scores for any object
--   4. schema_migrations — Versioned schema tracking
-- =============================================================================

-- Enable WAL mode for concurrent read/write during long simulation runs
PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;
PRAGMA busy_timeout = 5000;

-- =============================================================================
-- 1. Core object registry (universal identifier for all entities)
-- =============================================================================
CREATE TABLE IF NOT EXISTS objects (
    id              TEXT PRIMARY KEY,            -- UUID v4
    object_type     TEXT NOT NULL,               -- specimen, test_result, microstructure_image,
                                                 -- computational_model, simulation_result,
                                                 -- blade_design, wind_turbine_system,
                                                 -- energy_system, community_profile,
                                                 -- validation_reference
    created_at      TEXT NOT NULL,               -- ISO 8601
    updated_at      TEXT NOT NULL,               -- ISO 8601
    tags            TEXT,                        -- JSON array of search/filter tags
    metadata        TEXT,                        -- JSON flexible metadata (extensible)
    quality_score   REAL,                        -- 0-10 aggregate PQMS for this object
    validation_status TEXT DEFAULT 'PENDING',    -- PENDING, PASS, FAIL

    -- Ensure quality_score is in valid range
    CONSTRAINT ck_quality_score_range CHECK (
        quality_score IS NULL OR (quality_score >= 0 AND quality_score <= 10)
    ),
    -- Ensure validation_status is one of the allowed values
    CONSTRAINT ck_validation_status CHECK (
        validation_status IN ('PENDING', 'PASS', 'FAIL')
    ),
    -- Ensure object_type is a known type
    CONSTRAINT ck_object_type CHECK (
        object_type IN (
            'specimen', 'test_result', 'microstructure_image',
            'computational_model', 'simulation_result',
            'blade_design', 'wind_turbine_system',
            'energy_system', 'community_profile',
            'validation_reference'
        )
    )
);

CREATE INDEX idx_objects_type ON objects(object_type);
CREATE INDEX idx_objects_validation ON objects(validation_status);
CREATE INDEX idx_objects_quality ON objects(quality_score);
CREATE INDEX idx_objects_created ON objects(created_at);

-- =============================================================================
-- 2. Provenance tracking (W3C PROV-inspired DAG)
-- =============================================================================
-- Records directed edges between objects, forming a Directed Acyclic Graph
-- that enables full forward and backward traceability per FR-016.
-- =============================================================================
CREATE TABLE IF NOT EXISTS provenance (
    id              TEXT PRIMARY KEY,            -- UUID v4
    source_id       TEXT NOT NULL,               -- FK → objects(id): input/upstream object
    target_id       TEXT NOT NULL,               -- FK → objects(id): output/derived object
    transformation  TEXT NOT NULL,               -- Operation applied (e.g., 'mechanical_test',
                                                 -- 'image_analysis', 'simulation_run',
                                                 -- 'calibration', 'validation')
    parameters      TEXT,                        -- JSON: parameters used in transformation
    timestamp       TEXT NOT NULL,               -- ISO 8601

    FOREIGN KEY (source_id) REFERENCES objects(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (target_id) REFERENCES objects(id)
        ON DELETE CASCADE ON UPDATE CASCADE,

    -- Prevent self-referencing edges
    CONSTRAINT ck_no_self_reference CHECK (source_id != target_id)
);

CREATE INDEX idx_provenance_source ON provenance(source_id);
CREATE INDEX idx_provenance_target ON provenance(target_id);
CREATE INDEX idx_provenance_transform ON provenance(transformation);
CREATE INDEX idx_provenance_time ON provenance(timestamp);

-- =============================================================================
-- 3. PQMS quality scores (per-dimension scoring for any object)
-- =============================================================================
-- Stores per-dimension scores (D1-D13) for PQMS computation.
-- Aggregate PQMS = SUM(score * weight) / SUM(weights).
-- Constraint: no single dimension may fall below 8.5 (per SC-008).
-- =============================================================================
CREATE TABLE IF NOT EXISTS quality_scores (
    id              TEXT PRIMARY KEY,            -- UUID v4
    object_id       TEXT NOT NULL,               -- FK → objects(id)
    dimension       TEXT NOT NULL,               -- Dimension name/ID
                                                 -- D1_completude, D2_profundidade, D3_rigor,
                                                 -- D4_rastreabilidade, D5_conhecimento,
                                                 -- D6_integracao, D7_qualidade_numerica,
                                                 -- D8_impacto, D9_vies, D10_ensino,
                                                 -- D11_velocidade, D12_satisfacao, D13_inovacao
    score           REAL NOT NULL,               -- 0-10
    weight          REAL NOT NULL,               -- Dimension weight (0-1, sum across dimensions = 1)
    evidence        TEXT,                        -- JSON evidence reference for this score
    computed_at     TEXT NOT NULL,               -- ISO 8601

    FOREIGN KEY (object_id) REFERENCES objects(id)
        ON DELETE CASCADE ON UPDATE CASCADE,

    -- Score must be in valid range
    CONSTRAINT ck_score_range CHECK (score >= 0 AND score <= 10),
    -- Weight must be positive
    CONSTRAINT ck_weight_positive CHECK (weight > 0 AND weight <= 1),
    -- Dimension must be a valid PQMS dimension
    CONSTRAINT ck_dimension CHECK (
        dimension IN (
            'D1_completude', 'D2_profundidade', 'D3_rigor',
            'D4_rastreabilidade', 'D5_conhecimento',
            'D6_integracao', 'D7_qualidade_numerica',
            'D8_impacto', 'D9_vies', 'D10_ensino',
            'D11_velocidade', 'D12_satisfacao', 'D13_inovacao'
        )
    )
);

CREATE INDEX idx_quality_object ON quality_scores(object_id);
CREATE INDEX idx_quality_dimension ON quality_scores(dimension);

-- =============================================================================
-- 4. Schema migration tracking
-- =============================================================================
CREATE TABLE IF NOT EXISTS schema_migrations (
    version         INTEGER PRIMARY KEY AUTOINCREMENT,
    description     TEXT NOT NULL,
    applied_at      TEXT NOT NULL,               -- ISO 8601
    checksum        TEXT NOT NULL,               -- SHA-256 of migration SQL
    status          TEXT DEFAULT 'PENDING'       -- PENDING, APPLIED, FAILED, ROLLED_BACK
);

-- Seed initial migration record
INSERT INTO schema_migrations (version, description, applied_at, checksum, status)
VALUES (1, 'Core schema: objects, provenance, quality_scores', strftime('%Y-%m-%dT%H:%M:%SZ', 'now'), 'seed', 'APPLIED');

-- =============================================================================
-- Key Provenance Chains (documented for reference — enforced by application layer)
-- =============================================================================
--
-- Chain 1 — Material characterization:
--   Material Specimen → Test Result → Microstructure Image
--
-- Chain 2 — Model calibration:
--   Validation Reference → Computational Model → Simulation Result
--
-- Chain 3 — Design chain:
--   Material Specimen → Computational Model → Blade Design
--   → Wind Turbine System → Energy System
--
-- Chain 4 — Sizing chain:
--   Community Profile → Energy System
