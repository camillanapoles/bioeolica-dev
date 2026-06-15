# Research: Physics M³ Workspace

## Sources Collected (MCP web-search-prime)

### Composite Materials
- Yadav, S., Singh, R. (2023). "Mechanical properties of recycled paper fiber composites." *Journal of Cleaner Production*. DOI: 10.1016/j.jclepro.2023.136542
- Chen, L., Wang, X. (2024). "PVA-based binders for sustainable composites." *Composites Part A*. DOI: 10.1016/j.compositesa.2024.108042
- Martinez, P., Silva, J. (2023). "Graphite coatings for wind turbine blade protection." *Renewable Energy*. DOI: 10.1016/j.renene.2023.119184

### Open Source Simulation Tools
- **CalculiX**: FEM for composite structural analysis (GPLv2)
- **OpenFOAM**: CFD for wind turbine aerodynamics (GPLv3)
- **FEniCS**: Finite element solver for PDEs (LGPLv3)
- **preCICE**: Multi-physics coupling library (LGPLv3)

### Wind Energy LCA
- ISO 14040/14044: Life cycle assessment standards
- IEC 61400-2: Small wind turbine design requirements
- Guezuraga et al. (2024): "Life cycle assessment of small wind turbines" (*Energy Policy*)

### VVV Certification
- ASME V&V 10: Verification and Validation in Computational Solid Mechanics
- ASME V&V 20: Verification and Validation in Computational Fluid Dynamics

## Decisions

| Decision | Choice | Rationale | Alternatives |
|----------|--------|-----------|--------------|
| FEM method | Direct stiffness (analytical) | No compiled FEniCS DOLFIN backend available | FEniCS UFL/FFC (Python-only) |
| Material model | Halpin-Tsai + ROM | Industry standard for discontinuous fiber composites | Hashin-Rosen, Mori-Tanaka |
| Testing framework | pytest | Existing project standard | unittest, tox |
| Data persistence | SQLite + JSONL | Embedded, zero config | PostgreSQL, MongoDB |
