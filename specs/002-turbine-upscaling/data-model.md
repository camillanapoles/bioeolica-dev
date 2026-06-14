# Data Model: Turbine Upscaling

**Feature**: specs/002-turbine-upscaling
**Date**: 2026-06-13
**Source**: [spec.md](../spec.md), [research.md](./research.md)

---

## 1. Entity Relationship Diagram (Textual)

```
CostScalingModel ──┐
                   ├──→ TurbineConfiguration ──→ EnergySystem
WindResourceProfile ┘
                        ↑
                   CommunityProfile
```

## 2. Entities

### TurbineConfiguration

Represents a candidate turbine design with all parameters needed for economic and energy computation.

| Field | Type | Description | Source |
|-------|------|-------------|--------|
| config_id | INTEGER PK | Unique identifier | Auto-generated |
| topology | TEXT | 'VAWT' or 'HAWT' | Design choice |
| rated_power_kw | REAL | Rated power in kW | Design parameter |
| rotor_diameter_m | REAL | Rotor diameter (width for VAWT) | Design calculation |
| hub_height_m | REAL | Hub/top height | Design calculation |
| blade_count | INTEGER | Number of blades | Topology-specific |
| airfoil | TEXT | Airfoil profile (e.g., NACA 0018) | Topology-specific |
| solidity | REAL | Rotor solidity | Topology-specific |
| tip_speed_ratio_nominal | REAL | Design TSR | Topology-specific |
| est_material_cost_usd | REAL | Estimated material cost ($) | Cost model |
| est_manufacturing_cost_usd | REAL | Manufacturing cost ($) | Cost model |
| est_bos_cost_usd | REAL | Balance-of-system cost ($) | Cost model |
| total_installed_cost_usd | REAL | Sum of all costs ($) | Computed |
| cost_per_kw_usd | REAL | Total / rated power | Computed |
| annual_energy_production_kwh | REAL | AEP from wind resource | Computed |
| capacity_factor_pct | REAL | CF = AEP / (P_rated × 8760) | Computed |
| lcoe_usd_per_kwh | REAL | Levelized cost of energy | Computed |
| demand_coverage_pct | REAL | % of daily demand covered | Computed |
| battery_kwh_nominal | REAL | Battery capacity (kWh) | Storage sizing |
| battery_dod_pct | REAL | Depth of discharge | Storage sizing |
| autonomy_days | REAL | Days of autonomy | Computed |
| created_at | TEXT | Timestamp | Auto-generated |

**CHECK constraints** (matching SC-004/SC-005):
- `lcoe_usd_per_kwh < 0.15`
- `cost_per_kw_usd < 3000`
- `demand_coverage_pct >= 100`
- `autonomy_days >= 2.0`
- `capacity_factor_pct >= 20.0`

### CostScalingModel

Mathematical model decomposing total cost into scaling and fixed components.

| Field | Type | Description |
|-------|------|-------------|
| model_id | INTEGER PK | Unique identifier |
| rotor_mass_cost_rate | REAL | $/kg for composite blades |
| generator_cost_exponent | REAL | Scaling exponent (default 0.75) |
| generator_base_cost | REAL | Base generator cost ($) |
| tower_cost_per_m | REAL | $/m for tower |
| controller_fixed_cost | REAL | Fixed controller cost ($) |
| inverter_fixed_cost | REAL | Fixed inverter cost ($) |
| transport_base_cost | REAL | Fixed transport ($) |
| transport_rate_per_kg_km | REAL | $/kg/km variable transport |
| installation_fixed_cost | REAL | Fixed installation ($) |
| battery_cost_per_kwh | REAL | $/kWh at system level |
| battery_dod | REAL | Depth of discharge (fraction) |
| battery_rte | REAL | Round-trip efficiency (fraction) |
| discount_rate | REAL | Economic discount rate |
| project_lifetime_years | INTEGER | Project lifetime |
| om_annual_pct | REAL | O&M as % of installed cost |
| validation_error_pct | REAL | Model error vs real costs |

### WindResourceProfile

Site-specific wind parameters.

| Field | Type | Description |
|-------|------|-------------|
| profile_id | INTEGER PK | Unique identifier |
| location | TEXT | Site name |
| mean_wind_speed_ms | REAL | Mean at hub height |
| weibull_k | REAL | Weibull shape parameter |
| air_density_kgm3 | REAL | Annual mean air density |
| hub_height_m | REAL | Measurement height |
| turbulence_intensity | REAL | TI (fraction) |
| temperature_c | REAL | Annual mean temperature |
| source | TEXT | Data source reference |

### CommunityProfile

Energy demand profile for the target community.

| Field | Type | Description |
|-------|------|-------------|
| community_id | INTEGER PK | Unique identifier |
| name | TEXT | Community name |
| families | INTEGER | Number of families |
| population | INTEGER | Total population |
| irrigated_area_ha | REAL | Irrigated agriculture area |
| daily_demand_kwh | REAL | Baseline daily demand |
| design_daily_demand_kwh | REAL | With growth margin |
| monthly_profile_json | TEXT | JSON array of 12 monthly kWh values |
| seasonal_amplitude_pct | REAL | ±% seasonal variation |
| water_daily_liters | INTEGER | Daily water consumption |
| source | TEXT | Data source |

### EnergySystem (existing `energy_systems` table)

The registered row that must pass SC-004/SC-005 CHECK constraints. Mapped directly from `TurbineConfiguration` computed fields.

| Field | Type | Constraint |
|-------|------|-----------|
| system_id | INTEGER PK | |
| lcoe_usd_per_kwh | REAL | CHECK < 0.15 |
| cost_per_kw_usd | REAL | CHECK < 3000 |
| autonomy_days | REAL | CHECK >= 2.0 |
| capacity_factor_pct | REAL | CHECK >= 20.0 |
| demand_coverage_pct | REAL | CHECK >= 100 |

## 3. Key Relationships

```
TurbineConfiguration 1──1 EnergySystem  (via registration)
TurbineConfiguration *──1 CostScalingModel (each config evaluated against model)
TurbineConfiguration *──1 WindResourceProfile (same site, different configs)
WindResourceProfile 1──1 CommunityProfile (one site per community)
```

## 4. Existing DB Tables Referenced

- `wind_turbine_systems` — 1 row (0.82 kW VAWT prototype)
- `blade_designs` — 1 row (3.5m NACA 0018 blade)
- `energy_systems` — 0 rows (target for registration)
- `community_profiles` — 1 row (Assentamento Sertao Sustentavel)
- `quality_scores` — 3835 rows (PQMS data)
