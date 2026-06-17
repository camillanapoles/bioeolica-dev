# Contract: Thermal Solver Interface

## Input

```python
class ThermalSolverConfig:
    mesh_path: str           # Path to .msh
    conductivity: float      # W/mK
    bc_temperature: dict     # {node_id: temp_K}
    bc_flux: dict            # {node_id: flux_Wm2}
    bc_convection: list      # [(node_ids, h_Wm2K, T_inf_K)]
    solver: str = "direct"   # "direct" or "iterative"
```

## Output

```python
class ThermalResult:
    temperatures: np.ndarray   # (n_nodes,) temperature in K
    min_temp: float
    max_temp: float
    gradient: np.ndarray       # (n_elem,) thermal gradient magnitude
    converged: bool
    iterations: int
```

## CLI

```
python -m src.termo.solver --mesh model.msh --k 50 --bc-temp "0:300,100:400" --output temp.npy
```
