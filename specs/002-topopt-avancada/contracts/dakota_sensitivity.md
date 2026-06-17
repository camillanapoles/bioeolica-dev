# Contract: Dakota Sensitivity Analysis

## Interface

Dakota performed via subprocess on converged TopOpt results.

### Input Parameters
- Load magnitude: ±10% of nominal
- Material properties (E, nu): ±5%
- Volume fraction: ±2%

### Output Metrics
- Sensitivity index (0-1) per parameter
- Ranked list of top drivers
- Pareto plot data

### Dakota Method
- Morris One-At-a-Time (OAT) screening
- Sobol variance-based sensitivity
- Latin Hypercube sampling, N=1000
