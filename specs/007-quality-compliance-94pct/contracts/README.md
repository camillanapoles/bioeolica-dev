# Contracts: Quality & Compliance Optimization

## Architecture Decision Record

### ADR-001: Cross-Workspace Packaging
- **Decision**: pyproject.toml per workspace with `pip install -e .`
- **Rationale**: Standard Python packaging, no importlib hacks
- **Alternatives considered**: namespace packages, symlinks, single monorepo

### ADR-002: VVV Certification Criteria
- **Decision**: 6 binary criteria (convergence, stability, conservation, benchmark, cross-code, units)
- **Rationale**: Aligned with INSTRUCTIONS.md M3 VVV section

### ADR-003: CuPy CPU Fallback
- **Decision**: try/except ImportError with numpy fallback + warning
- **Rationale**: CI/CD compatibility without GPU requirement
