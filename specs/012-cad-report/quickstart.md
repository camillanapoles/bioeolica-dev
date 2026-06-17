# Quickstart — CAD+REPORT Pipeline

## Prerequisites

```bash
# C2 and C3 already implemented
PYTHONPATH=src:. pytest tests/test_cad_pipeline.py tests/test_engine.py -v
# Expected: 19/19 PASS
```

## Validation Scenarios

### Scenario 1: Full Pipeline (Hero)

```bash
PYTHONPATH=src:. python -m src.cadreport.pipeline \
  --params tests/fixtures/cube_params.json \
  --output-dir /tmp/package
```

**Expected:**
- `/tmp/package/model.step` exists
- `/tmp/package/report.md` exists  
- `/tmp/package/metadata.json` exists
- `/tmp/package/checksums.sha256` exists

### Scenario 2: Deterministic CAD

```bash
PYTHONPATH=src:. python -m src.cadreport.pipeline \
  --params tests/fixtures/cube_params.json \
  --output-dir /tmp/package2

diff /tmp/package/model.step /tmp/package2/model.step || echo "Different (expected if UUIDs)"
```

### Scenario 3: CRSLR Contains CAD Metadata

```bash
grep "model.step" /tmp/package/report.md && echo "✅ CAD referenced in report"
grep "steel" /tmp/package/report.md && echo "✅ Material in report"
```

## Unit Tests

```bash
pytest tests/test_cadreport.py -v --tb=short
# Expected: 5/5 PASS
```
