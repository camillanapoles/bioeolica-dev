# Interface Contract: CostScalingModel

**Purpose**: Decompose turbine cost into scaling vs fixed components and project cost at any rating.

## Function: `compute_cost_breakdown`

```
Input:
  rated_power_kw: float          # 0.5 to 50 kW
  topology: "VAWT" | "HAWT"
  model_params: CostModelParams  # scaling coefficients

Output:
  cost_breakdown: {
    rotor_cost_usd: float,
    generator_cost_usd: float,
    tower_cost_usd: float,
    battery_cost_usd: float,
    fixed_costs_usd: float,      # controller + inverter + transport + installation
    total_cost_usd: float,
    cost_per_kw_usd: float
  }
```

## Function: `compute_lcoe`

```
Input:
  total_installed_cost_usd: float
  annual_energy_production_kwh: float
  discount_rate: float           # default 0.08
  lifetime_years: int            # default 20
  om_annual_pct: float           # default 0.02
  om_fixed_usd: float | None     # optional override

Output:
  lcoe_usd_per_kwh: float
  crf: float                     # capital recovery factor
  annual_om_cost: float
```

## Function: `compute_aep`

```
Input:
  rated_power_kw: float
  mean_wind_speed_ms: float      # at hub height
  weibull_k: float               # shape parameter
  air_density_kgm3: float        # default 1.15
  power_curve: list[tuple]       # [(v_ms, cp), ...] or None → Rayleigh analytical

Output:
  annual_energy_production_kwh: float
  capacity_factor_pct: float
  full_load_hours: float
```

## Function: `size_battery`

```
Input:
  daily_demand_kwh: float
  autonomy_days: float           # default 2.0
  battery_dod: float             # default 0.8
  battery_rte: float             # default 0.85
  battery_cost_per_kwh: float    # default 200

Output:
  battery_kwh_nominal: float
  battery_cost_usd: float
  autonomy_days_actual: float
```
