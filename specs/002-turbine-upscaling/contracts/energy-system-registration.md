# Interface Contract: EnergySystemRegistration

**Purpose**: Register a validated turbine+storage configuration in the `energy_systems` table.

## Function: `register_energy_system`

```
Input:
  lcoe_usd_per_kwh: float        # MUST be < 0.15
  cost_per_kw_usd: float         # MUST be < 3000
  autonomy_days: float           # MUST be >= 2.0
  capacity_factor_pct: float     # MUST be >= 20.0
  demand_coverage_pct: float     # MUST be >= 100
  source_config_id: int          # FK to turbine_configurations

Output:
  system_id: int                 # new PK
  check_results: {
    sc004a: bool,                # LCOE check
    sc004b: bool,                # cost/kW check
    sc005a: bool,                # demand coverage
    sc005b: bool,                # autonomy
    sc005c: bool                 # capacity factor
  }
  insert_success: bool

Errors:
  CHECK_CONSTRAINT_VIOLATION    # if any SC check fails
  DUPLICATE_CONFIG              # config already registered
```

## Function: `run_validation_checks`

```
Input:
  system_id: int

Output:
  sc004_pass: bool
  sc005_pass: bool
  all_28_pass: bool
  check_details: list[dict]     # each check with name, status, detail
```
