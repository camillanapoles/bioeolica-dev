# Config Manager — Single Source of Truth

**Feature:** All calculation parameters across all modules read from a single `config.json` file. Zero hardcoded defaults. Any value can be overridden per scenario.

**Motivation:** The user needs to set parameters once (e.g., altitude=500) and have it persist across ALL calculations — macro, meso, micro, FEM, etc. Changing to scenario 2 means loading a different config.json. Frontend will produce/consume this same file.

## Architecture

```
config.json  →  ConfigManager  →  kdi_macro (reads env.altitude)
   ↑                                  kdi_meso (reads fem.loads)
   │                                  kdi_micro (reads material.E)
   │                                  cad_bridge (reads cad.dimensions)
   │                                  gmsh_mesher (reads mesh.size)
   │                                  calculix_solver (reads solver.E, solver.nu)
   │                                  design_optimizer (reads doe.levels)
   └────────────────────────────────── Frontend writes/reads
```

## Config File Format

```json
{
  "project": {
    "name": "wind_blade_v2",
    "description": "Turbine blade analysis",
    "author": "user"
  },
  "environment": {
    "altitude_m": 100,
    "wind_class": "II",
    "wind_speed_ref_ms": 30.0,
    "exposure": "rural",
    "safety_class": "CC2"
  },
  "geometry": {
    "length_mm": 100,
    "width_mm": 20,
    "height_mm": 20,
    "primitive": "box"
  },
  "mesh": {
    "element_size": 3.0,
    "element_order": 1,
    "algorithm": 6
  },
  "material": {
    "name": "STEEL",
    "E_GPa": 210,
    "nu": 0.3,
    "rho_kgm3": 7850
  },
  "solver": {
    "type": "static",
    "force_N": {"x": 0, "y": 0, "z": -100},
    "max_iterations": 100
  },
  "kdi": {
    "macro": {"enabled": true},
    "meso": {"enabled": true},
    "micro": {"enabled": false}
  },
  "output": {
    "format": "json",
    "export_vtk": false
  }
}
```
