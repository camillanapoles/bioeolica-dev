# Quickstart: Turbine Upscaling Validation

**Feature**: specs/002-turbine-upscaling
**Date**: 2026-06-13

## Prerequisites

- Python 3.11+ with NumPy, SciPy, Matplotlib
- SQLite3 (stdlib)
- `data/bioeolica.db` (existing database)
- All scripts in `src/02-wind-energy/`

## Step 1: Diagnose Python Environment

```bash
# Check if Python is executable
python3 --version
which python3

# If exit code 127 on any .py script, check PATH
echo $PATH
# Expected: /usr/bin/python3 or similar in PATH
```

## Step 2: Verify Current DB State

```bash
sqlite3 data/bioeolica.db "
SELECT 'wind_turbine_systems:', COUNT(*) FROM wind_turbine_systems;
SELECT 'energy_systems:', COUNT(*) FROM energy_systems;
SELECT 'community_profiles:', COUNT(*) FROM community_profiles;
SELECT 'SC-004 LCOE target:', COUNT(*) FROM energy_systems WHERE lcoe_usd_per_kwh < 0.15;
SELECT 'SC-005 demand coverage:', COUNT(*) FROM energy_systems WHERE demand_coverage_pct >= 100;
"
```

Expected: wind_turbine_systems=1, energy_systems=0, community_profiles=1

## Step 3: Run Cost Scaling Model

```bash
python3 src/02-wind-energy/energy-system/sizing_lcoe.py
```

Expected output: Cost breakdown table for multiple turbine sizes (5-20 kW).

If exit code 127: diagnose Python PATH issue. If missing dependencies: `pip install numpy scipy matplotlib`.

## Step 4: Compute AEP for Candidate Sizes

```bash
# Compute wind resource and AEP for VAWT at multiple sizes
python3 src/02-wind-energy/aerodynamics/wind_resource.py \
  --mean-wind 5.5 --weibull-k 2.0 --air-density 1.15 \
  --sizes 5,10,12,15,20 --topology vawt
```

Expected output: AEP (kWh/yr), CF (%), demand coverage (%) per size.

## Step 5: Register Energy System

```bash
python3 src/02-wind-energy/energy-system/register_energy_system.py \
  --lcoe 0.24 --cost-per-kw 6855 --autonomy 2.5 \
  --capacity-factor 20 --demand-coverage 119 \
  --config-id 2
```

Expected behavior: INSERT succeeds if all CHECK constraints pass, OR fails with CHECK_CONSTRAINT_VIOLATION.

## Step 6: Run Validation Suite

```bash
bash tests/validation/run_all_checks.sh
```

Expected: Report showing all 28 checks with PASS/FAIL status, including SC-004 and SC-005 rows.

**Note**: If SC-004/SC-005 checks are MISSING from output (not shown at all), the validation view has a zero-row bug — see research.md Section 7. Fix: `LEFT JOIN` or `COALESCE` in validation views.

## Step 7: Verify PQMS Scores

```bash
python3 src/03-data-management/pqms_report.py
```

Expected: PQMS report with per-object scores. Compare against target 9.5.

## Validation Checklist

- [ ] Python scripts execute without exit code 127
- [ ] cost projection table generated (5, 10, 12, 15, 20 kW)
- [ ] AEP computed for all candidate sizes
- [ ] Battery sizing computed (2-day autonomy at design demand)
- [ ] Energy system registration attempted
- [ ] `run_all_checks.sh` reports SC-004/SC-005 visible (not missing)
- [ ] LCOE and cost/kW values documented for final report
- [ ] Topology recommendation (VAWT vs HAWT) with quantitative rationale

## Acceptance Criteria

Per spec.md User Story 1:

1. **FR-001/FR-002**: LCOE and cost/kW computed for each turbine configuration → document best values
2. **FR-003/FR-004**: AEP and demand coverage computed → ≥100% coverage target
3. **FR-005**: Battery sized for ≥2 days autonomy
4. **FR-006**: VAWT vs HAWT comparison at ≥3 sizes (5, 10, 15 kW)
5. **FR-007**: Registered in energy_systems table → run_all_checks.sh shows SC-004/SC-005 PASS/FAIL correctly
6. **FR-008**: All assumptions documented in knowledge/ directory
