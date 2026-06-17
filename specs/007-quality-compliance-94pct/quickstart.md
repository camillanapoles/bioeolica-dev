# Quickstart: Quality & Compliance Optimization

## Prerequisites

- Python 3.11+
- Repository cloned with `--recurse-submodules`
- GitNexus indexed: `node .gitnexus/run.cjs analyze`

## Setup

```bash
# Install workspaces as editable packages
pip install -e workspaces/physics-m3 -e workspaces/cad-cae -e workspaces/kdi-m3

# No sudo required, no PYTHONUTF8 required
```

## Validation Scenarios

### Scenario 1: Cross-Workspace Import
```bash
python -c "
from physics_m3.composite import CompositeMaterial
from cad_cae.geometry import WindTurbineBlade
from kdi_m3.config import ConfigManager
print('Cross-workspace imports: ✅')
"
```
**Expected**: No importlib workaround, no sys.path manipulation, clean import.

### Scenario 2: Benchmark Validation
```bash
cd workspaces/physics-m3
python -m pytest tests/test_benchmarks/ -v
```
**Expected**: All analytic benchmarks PASS with error < 5% (fine mesh).

### Scenario 3: VVV C11 Certification
```bash
cd workspaces/physics-m3
python -m pytest tests/test_vvv_multiscale/ -v
```
**Expected**: 6 criteria all PASS, overall PASS, metrics quantified.

### Scenario 4: CI Pipeline (local dry-run)
```bash
pip install -e workspaces/*
python -m pytest --tb=short --cov
```
**Expected**: No PYTHONUTF8 warnings, no sudo calls, no importlib hacks.

### Scenario 5: Full Compliance Report
```bash
python scripts/compliance/report.py
```
**Expected**: PQMS ≥ 94%, all 8 non-conformances closed, FDC-U scores per objective.

## Git Workflow

```bash
# Per task cycle:
git checkout -b 007-quality-task-N
# ... implement ...
git add -A && git commit -m "T00N: task description"
git push origin 007-quality-task-N
# After all tasks in phase:
git checkout main && git merge 007-quality-task-N
```
