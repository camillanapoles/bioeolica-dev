# Interface Contract: WindResourceAPI

**Purpose**: Compute wind resource statistics and turbine power output.

## Function: `weibull_distribution`

```
Input:
  v_mean: float                  # mean wind speed (m/s)
  k: float                       # Weibull shape parameter
  v_bins: int                    # default 100

Output:
  v_array: list[float]           # wind speed bins (m/s)
  f_array: list[float]           # probability density
  F_array: list[float]           # cumulative distribution
  c: float                       # Weibull scale parameter
```

## Function: `power_curve_output`

```
Input:
  rated_power_kw: float
  rotor_diameter_m: float
  cp_vs_tsr: list[tuple]         # [(tsr, cp), ...] for topology
  air_density_kgm3: float        # default 1.15

Output:
  power_curve: list[tuple]       # [(v_ms, power_kw), ...]
  cut_in_ms: float
  rated_v_ms: float
  cp_max: float
```

## Function: `energy_pattern_factor`

```
Input:
  v_mean: float
  k: float
  cp_curve_func: callable        # cp(v) function

Output:
  epf: float                     # energy pattern factor
  energy_density_kwh_m2: float   # annual energy per swept area
```
