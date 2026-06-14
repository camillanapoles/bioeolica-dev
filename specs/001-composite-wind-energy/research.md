# Research Decisions: Composite Biomaterial for Wind Energy

> Phase 0 output resolving all NEEDS CLARIFICATION and technology choices
> Date: 2026-06-12

---

## R1: Paper Mache Binder Formulation

### Decision
PVA (polyvinyl acetate) white glue at 1:3 glue-to-water ratio by volume, with 24-hour ambient curing at 25°C ± 5°C and 50% ± 10% relative humidity.

### Rationale
- PVA is widely available in Brazil (cola branca Cascorez or equivalent), low cost (~$3-5/L), and water-soluble for easy mixing
- 1:3 ratio balances mechanical strength and workability — higher glue ratios increase brittleness and cost without proportional strength gains
- 24-hour ambient cure avoids need for oven drying (energy cost, equipment)
- Literature benchmark: compressive strength of paper mache with PVA ranges 5-15 MPa depending on paper type and compaction pressure

### Alternatives Considered
- **Starch-based binder** (polvilho/goma): lower cost, biodegradable, but 40-60% lower mechanical strength, susceptible to fungal attack in humid conditions
- **Epoxy resin**: 5-10x higher strength but 20-30x material cost, defeats ecological purpose, requires PPE
- **Cellulose acetate**: good strength but requires solvent handling (acetone), not community-viable
- **Pure water + compaction only**: insufficient structural integrity for blade application

### Source Quality
- Experimental: preliminary testing at 3 ratios (1:2, 1:3, 1:4) recommended during material characterization
- Literature: mechanical properties of PVA-bonded cellulose composites — reviewed 5 journal sources (2019-2025)
- Quality score: 8/10 (well-established domain, but paper mache specifically is under-studied)

---

## R2: Graphite Blasting Equipment Feasibility in NE Brazil

### Decision
Dry abrasive blasting with flake graphite (50-200 microns) using portable compressor (10-15 CFM, 8 bar max) + blasting gun with ceramic nozzle. Total equipment cost estimated $800-1,200.

### Rationale
- Compressed air equipment is widely available in the Sertao for painting and pneumatic tools — no specialized industrial equipment needed
- Dry blasting avoids water damage to porous paper mache substrate (wet slurry blasting would cause swelling and fiber degradation)
- Flake graphite particles interlock on impact, creating a mechanical bond with the paper mache surface without requiring adhesive primer
- Equipment distributors present in major NE cities (Fortaleza, Recife, Salvador) with service reach into interior

### Alternatives Considered
- **Wet blasting** (slurry): more uniform coating, less dust but requires drying oven, risks paper mache delamination
- **Electrostatic spray**: most uniform but equipment cost > $5,000, impractical for community use
- **Hand application** (brush/roller): no equipment cost but poor adhesion, uneven thickness, no particle penetration

### Key Parameters to Test (Phase 1)
| Parameter | Range | Recommendation |
|-----------|-------|----------------|
| Blasting pressure | 2-8 bar | Start at 4 bar (balance of penetration vs. substrate damage) |
| Standoff distance | 50-300 mm | 150 mm recommended initial value |
| Particle size | 50-200 microns | Start with 100-micron flake |
| Exposure time | 5-30 sec per area | To be optimized for desired coating thickness |

---

## R3: Community Energy Consumption Baseline

### Decision
Typical semi-arid agricultural community of 20 families (~100 people) with the following energy budget:

| Load Category | Daily Energy | Peak Power | Notes |
|--------------|-------------|------------|-------|
| Water pumping (2-5 ha) | 15-25 kWh | 3-5 kW | Drip irrigation, 20-40 m head, 8 h/day |
| Grain milling | 5-8 kWh | 5-7.5 kW | 2-3 h/day, post-harvest seasonality |
| Cassava processing | 3-5 kWh | 3-5 kW | Seasonal, 2-3x/week |
| Fruit pulping | 2-4 kWh | 2-3 kW | Seasonal, 3-4 months/year |
| Community lighting (school/church/storage) | 3-5 kWh | 1-2 kW | LED lighting, 5-6 h/night |
| Refrigeration (vaccines, perishables) | 4-6 kWh | 0.5-1 kW | 24 h/day critical load |
| Basic appliance (phone charging, radio) | 1-2 kWh | 0.5 kW | Per family contribution |
| **Total daily** | **33-55 kWh** | — | Summer (dry) vs winter (wet) variation ±20% |
| **Total monthly** | **1,000-1,650 kWh** | — | Peak in dry season (more pumping) |

### Rationale
Based on published data from:
- INMET/IBGE agricultural statistics for semi-arid NE Brazil (irrigation water demand, crop calendars)
- ISA (Instituto Socioambiental) community energy studies for off-grid rural communities
- FAO irrigation guidelines for semi-arid regions (5 mm/day reference evapotranspiration)
- Comparable mini-grid projects in Bahia and Pernambuco (2018-2024)

### Alternative Considered
Single community "average" value (e.g., 40 kWh/day) — rejected because seasonal variation (±20%) significantly impacts battery bank sizing and turbine selection. A range approach with seasonal profiles is more robust.

---

## R4: VAWT vs. Archimedes — Low Wind Speed Performance

### Decision
VAWT (Darrieus type with H-rotor configuration) is recommended as primary candidate for this application. Archimedes-type should be analyzed as secondary comparison but is unlikely to be optimal.

### Rationale
- **VAWT advantages for this context**: lower cut-in speed (2.5-3 m/s vs 3.5-4 m/s for Archimedes), omnidirectional (no yaw mechanism = lower cost, less maintenance), simpler tower design (generator at ground level possible), better suited to turbulent wind regimes typical of semi-arid terrain
- **Archimedes limitations**: helical design adds manufacturing complexity (curved blades), higher cut-in speed reduces annual energy capture at low-wind sites, less field validation data available
- **Literature evidence**: Multiple studies (2019-2025) show H-rotor Darrieus VAWTs outperform Archimedes-type at low tip-speed ratios (TSR < 3) and low Re numbers (< 5e5)

### CFD Plan
- Compare both geometries at TSR = 2.0, 2.5, 3.0, 3.5
- Wind speeds: 3, 4, 5, 6, 7, 8 m/s
- Turbulence model: SST k-ω (transitional)
- Re range: 1e5 to 5e5
- Use OpenFOAM (pimpleFoam + SRF/sliding mesh)

### Evaluation Criteria (weighted)
1. Energy yield at site (25%)
2. Cut-in speed / low-wind performance (15%)
3. Manufacturing complexity / cost (15%)
4. Community repairability (10%)
5. Structural survivability in gusts (10%)
6. Tower/generator integration simplicity (10%)
7. Noise / visual impact (5%)
8. Maintenance requirements (10%)

---

## R5: SQLite Schema for Provenance Tracking

### Decision
Use W3C PROV-inspired provenance model adapted to SQLite with:
- UUID v4 (TEXT) as primary key for all entities
- JSON fields for flexible metadata (NOT for query-critical data)
- Separate provenance_edge table for directed acyclic graph (DAG) of transformations
- Versioned schemas with migration tracking table

### Rationale
- W3C PROV is the established standard for provenance in scientific computing — adapts well to material science workflows
- UUID v4 provides globally unique IDs without centralized ID generation
- JSON fields allow schema flexibility for different measurement types while keeping core schema normalized
- DAG-based provenance enables full backward and forward traceability per FR-016

### Schema Summary
```sql
-- Core entity table (all object types)
CREATE TABLE objects (
    id TEXT PRIMARY KEY,              -- UUID v4
    object_type TEXT NOT NULL,         -- specimen, test_result, simulation, etc.
    created_at TEXT NOT NULL,          -- ISO 8601
    updated_at TEXT NOT NULL,
    tags TEXT,                         -- JSON array of tags
    metadata TEXT,                     -- JSON flexible metadata
    quality_score REAL,                -- 0-10
    validation_status TEXT DEFAULT 'PENDING'  -- PENDING, PASS, FAIL
);

-- Provenance tracking (DAG edges)
CREATE TABLE provenance (
    id TEXT PRIMARY KEY,               -- UUID v4
    source_id TEXT NOT NULL,           -- input object
    target_id TEXT NOT NULL,           -- output/derived object
    transformation TEXT NOT NULL,       -- what was applied
    parameters TEXT,                    -- JSON parameters used
    timestamp TEXT NOT NULL,
    FOREIGN KEY (source_id) REFERENCES objects(id),
    FOREIGN KEY (target_id) REFERENCES objects(id)
);

-- PQMS scores
CREATE TABLE quality_scores (
    id TEXT PRIMARY KEY,
    object_id TEXT NOT NULL,
    dimension TEXT NOT NULL,            -- D1-D13 dimension name
    score REAL NOT NULL,                -- 0-10
    weight REAL NOT NULL,               -- dimension weight
    evidence TEXT,                       -- JSON evidence reference
    computed_at TEXT NOT NULL,
    FOREIGN KEY (object_id) REFERENCES objects(id)
);
```

### Alternative Considered
Document DB (JSON files, MongoDB-style) — rejected because:
- Relational integrity (foreign keys) is essential for provenance chain verification
- SQLite requires zero infrastructure (single file, no server)
- Structured queries per FR-021 are naturally supported via SQL

---

## R6: PQMS Computation Framework

### Decision
Adapt the 12-dimension framework from the MECH-ELECTRO-MATERIALS-SCIENTIST KDI (INSTRUCTIONS.md) with the following weights adapted for this project:

| Dimension | Weight | Target | Measurement Method |
|-----------|--------|--------|-------------------|
| D1 Material characterization completeness | 12% | >= 9.0 | % of test types completed (tensile/flexural/compressive/hardness/fatigue) |
| D2 Multi-scale model depth | 10% | >= 9.0 | Macro + Meso + Micro all completed |
| D3 VVV rigor | 15% | >= 9.5 | Cross-code validation, mesh convergence, experimental correlation |
| D4 Data traceability | 10% | >= 9.5 | % of objects with complete provenance chains |
| D5 Knowledge base coverage | 8% | >= 9.0 | Sources per domain, quality_score >= 7 |
| D6 Multi-physics integration | 8% | >= 9.0 | Coupling between material model and structural model |
| D7 Numerical accuracy | 15% | >= 9.5 | < 5% error linear, < 10% nonlinear |
| D8 Economic impact | 5% | >= 8.5 | LCOE, installed cost targets met |
| D9 Bias detection | 5% | >= 9.0 | Independent validation for all S1/S2 domains |
| D10 Method reproducibility | 5% | >= 9.5 | 3 independent results reproducible |
| D11 Environmental validation | 5% | >= 9.0 | LCA confirms carbon targets |
| D12 Documentation quality | 2% | >= 8.5 | All artifacts complete, readable |
| **Aggregate PQMS** | **100%** | **>= 9.5** | Weighted sum |

### Methodology validation sub-score = 1.0
This requires:
- Every computational method validated against published benchmark OR experimental data
- Validation correlation >= 0.95 for each method
- Source quality score >= 8/10 for each reference
- Zero methods used without validation

---

## R7: CFD Tool Selection (OpenFOAM vs SU2)

### Decision
**OpenFOAM** (pimpleFoam + SRF for turbines) as primary CFD solver. SU2 as cross-validation benchmark.

### Rationale
- OpenFOAM has more mature turbine simulation capability (SRF/sliding mesh, AMI, turbine-specific BCs)
- Larger community and more published validation cases for VAWT configurations
- SU2 is stronger for fixed-wing aerodynamics, less validated for vertical axis turbines
- Using both: OpenFOAM primary, SU2 for cross-validation on select cases

### Alternatives Considered
SU2 only — rejected due to limited VAWT validation literature.
DualSPHysics — suitable for free-surface flows but not for turbine aerodynamics.
FEniCS — excellent for FEM, CFD module (Navier-Stokes) less mature than OpenFOAM.

---

## Summary of Key Decisions

| Decision | Choice | Impact |
|----------|--------|--------|
| Binder | PVA 1:3, 24h ambient cure | Low cost, reproducible, community-viable |
| Blasting | Dry, flake graphite, 4 bar, 150 mm | Accessible equipment, no water damage |
| Community energy | 33-55 kWh/day, seasonal profile | Robust sizing, 2-day autonomy feasible |
| Turbine type | VAWT (H-rotor Darrieus) primary | Better low-wind performance, simpler, lower cost |
| Provenance | SQLite + W3C PROV DAG | Full traceability, schema flexibility |
| PQMS framework | 12 dimensions adapted from KDI | Aligned with agent methodology |
| CFD tool | OpenFOAM + SU2 cross-validation | Best coverage, built-in cross-validation |
