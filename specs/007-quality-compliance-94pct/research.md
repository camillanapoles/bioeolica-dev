# Research: Quality & Compliance Optimization — 94% Target

## T001 — Benchmark Analytic Solutions

### Cantilever Beam: PL³/(3EI)
- **Formula**: δ = PL³/(3EI) where P = point load, L = length, E = Young's modulus, I = moment of inertia
- **Domain**: Mecânica (structural)
- **FEM Method**: CalculiX beam/hex elements, static analysis
- **Tolerance**: < 5% relative error (mesh ≥ 1000 hex elements), < 10% (coarse mesh ≥ 100)
- **Reference**: Euler-Bernoulli beam theory

### Plate with Hole: Kirsch Kt = 3.0
- **Formula**: σ_max = Kt × σ_nominal where Kt → 3.0 for infinite plate with circular hole under uniaxial tension
- **Domain**: Mecânica (stress concentration)
- **FEM Method**: CalculiX plane stress, quadratic elements
- **Tolerance**: < 10% for mesh with 8+ elements around hole circumference
- **Reference**: Kirsch 1898 solution, Peterson's Stress Concentration Factors

### Wind Pressure: NBR 6123
- **Formula**: q = 0.613 × Vk² (dynamic pressure), Cp values per geometry
- **Domain**: Fluidos (wind loading)
- **Method**: Analytical per NBR 6123 tables
- **Tolerance**: < 10% for standard geometries (rectangular, cylindrical)
- **Reference**: ABNT NBR 6123:1988

## T002 — Cross-Workspace Packaging

**Decision**: `pyproject.toml` per workspace with editable installs (`pip install -e .`)

**Rationale**: 
- Standard Python packaging, no importlib hacks
- Each workspace gets its own `[project]` section with `name`, `dependencies`, `version`
- Root `pyproject.toml` defines workspace dependencies via `[tool.uv.workspace]` or manual editable installs
- CI can run `pip install -e instruments/physics-m3 -e instruments/cad-cae -e instruments/kdi-m3`

**Alternatives considered**:
- Namespace packages: complex, requires `__init__.py` changes in all modules
- Symlinks: fragile, not version-controlled properly
- Monorepo single package: too coupled, defeats workspace separation

## T003 — VVV Certification Criteria

Based on INSTRUCTIONS.md M3 VVV section:
1. **Convergence de Malha**: < 5% variation between 3 refinement levels
2. **Estabilidade Temporal**: residual < 1e-4, CFL condition satisfied
3. **Conservação**: mass/energy balance error < 1%
4. **Benchmark**: correlation with known solution > 90%
5. **Cross-code**: 2+ independent implementations agree within tolerance
6. **Unidades**: SI dimensional consistency verified

PASS = all 6 criteria met. FAIL = any criterion not met → return_phase suggestion.

## T004 — CI/CD Patterns

**Decision**: GitHub Actions with matrix strategy (CPU only, no sudo)

**Pattern**:
- Trigger: push to main, PR to main
- Runner: ubuntu-22.04
- Setup: `pip install -e instruments/*` (no sudo, no PYTHONUTF8)
- GPU modules: skipped with warning when CUDA unavailable
- Steps: lint → unit → integration → coverage (parallel where possible)
- Timeout: 15 min target
