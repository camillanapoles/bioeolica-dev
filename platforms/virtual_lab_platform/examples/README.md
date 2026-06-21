# Validation Examples

This directory contains example payloads and descriptions for validating the Virtual Lab Platform with real-world deep-tech scenarios.

## Titanium Coupon for Satellite Structure

See `titanium_coupon_simulation.json` for a detailed example of how to set up a simulation that spans multiple scales:

- **Micro-scale**: Density Functional Theory (DFT) to compute fundamental material properties of Ti-6Al-4V (elastic modulus, yield strength, fracture toughness) at atomistic level.
- **Meso-scale**: Finite Element Method (FEM) with explicit grain structure to simulate the coupon's behavior under load, incorporating the micro-scale properties as homogenized material properties.
- **Macro-scale**: Computational Fluid Dynamics (CFD) coupled with structural analysis to evaluate the performance of a satellite bracket made of Ti-6Al-4V under aerodynamic loading and thermal conditions.

The example demonstrates the platform's capability to:
1. Accept complex, multi-scale simulation workflows.
2. Store and retrieve material properties and simulation parameters from the central database.
3. Orchestrate execution of different solvers (DFT, FEM, CFD) via the workflow engine.
4. Aggregate results and generate a comprehensive report (including resistance/fatigue analysis) that can be published.

To use this example:
1. Ensure the Ti-6Al-4V material is registered in the database (via `/materials/` endpoint).
2. Create a simulation using the payload above (adjust the `material_id` to match the registered material).
3. Trigger the simulation run via the `/simulations/{id}/run` endpoint.
4. Monitor the workflow status and retrieve results.
5. Optionally, generate a publication/publication record via the `/publications/` endpoint.

Note: The solver names "dft", "fem", "cfd" are placeholders. In a real deployment, specific solver adapters (e.g., VASP for DFT, CalculiX for FEM, OpenFOAM for CFD) would be configured and their respective Docker images used.

