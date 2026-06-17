# Installation Guide — Bioeólica Dev Platform

## Quick Start (no system deps required)

```bash
# Python packages only — works without CUDA, CalculiX, or Gmsh
pip install -e workspaces/physics-m3 -e workspaces/cad-cae-platform -e workspaces/kdi-m3-bridge
python -m pytest workspaces/physics-m3/tests/test_benchmarks/ -v
```

## System Dependencies (optional, for FEM/CFD solvers)

| Dependency | Purpose | Install (Ubuntu/Debian) |
|------------|---------|------------------------|
| **CalculiX (ccx)** | Finite Element solver | `sudo apt-get install calculix-ccx` |
| **Gmsh** | Mesh generation | `sudo apt-get install gmsh` |
| **libGLU** | OpenGL utility (ParaView) | `sudo apt-get install libglu1-mesa` |

> **Note**: If CalculiX or Gmsh are not installed, the relevant tests auto-skip with a warning.

## GPU Acceleration (optional)

```bash
# Install CuPy for GPU-accelerated linear algebra
pip install cupy-cuda12x  # must match your CUDA toolkit version
```

When CuPy is **not** installed, all modules fall back to NumPy/SciPy automatically
with a warning. No CUDA toolkit is required for basic operation.

## Environment Variables

No special environment variables required. The platform works with the
system default encoding (UTF-8) without PYTHONUTF8 or PYTHONIOENCODING.

## Verification

```bash
make setup
make test-quick     # benchmarks + VVV (~30s)
make test           # full suite (~2min)
make test-kdi       # KDI bridge tests (~2min)
```

## CI Pipeline

See `.github/workflows/ci.yml` for the automated CI configuration.
The CI runs on `ubuntu-22.04` with no system dependencies and no GPU.
