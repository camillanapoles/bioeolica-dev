# Contract: pyproject.toml Dependency Audit

> Script to extract and consolidate all Python dependencies into pyproject.toml.

## Interface

```
usage: scripts/audit_deps.py [-h] [--check] [--freeze]

Audit and consolidate Python dependencies.

options:
  -h, --help    show this help message and exit
  --check       Check declared deps vs actual imports (default: False)
  --freeze      Output pip-freeze style list for manual review (default: False)
```

## Behavior

1. Scan all `.py` files under `src/`, `cad/`, `scripts/`, `tests/` for import statements
2. Parse `requirements*.txt` files
3. Cross-reference: declared vs actual imports
4. `--check` mode: report missing deps and unused deps
5. `--freeze` mode: output version-pinned list from current environment
6. Generate `[project.dependencies]` and `[project.optional-dependencies]` blocks

## Sections to Populate

```toml
[project]
dependencies = [
    # extracted from audit
]

[project.optional-dependencies]
dev = ["pytest", "pytest-cov", "pytest-xdist", "ruff", "mypy"]
test = ["pytest", "pytest-cov"]
doc = ["mkdocs", "mkdocs-material"]
```

## Validation

- `pip install -e .` must succeed
- `pytest` must discover and run all tests after install
- Zero `ModuleNotFoundError` from declared dependencies
