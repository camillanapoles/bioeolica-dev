"""MFEM JSON input preparation."""
import os
import json

def prepare_mfem_case(params: dict, workdir: str) -> None:
    """
    Prepare MFEM input JSON file in the given workdir.
    Expected params:
        - mesh_type: e.g., "square", "cube"
        - nx, ny, nz: number of elements in each direction
        - order: finite element order (default 1)
        - alpha, beta: coefficients for Poisson -div(alpha grad u) + beta u = f
        - source: function or value for f
        - dirichlet_bc: dict marking Dirichlet boundaries (simple)
    We produce a simple JSON that MFEM examples can consume.
    """
    data = {
        "mesh": {
            "type": params.get("mesh_type", "square"),
            "nx": params.get("nx", 4),
            "ny": params.get("ny", 4),
            "nz": params.get("nz", 4),
            "elem_type": "hex"
        },
        "fem_order": params.get("order", 1),
        "coefficients": {
            "alpha": params.get("alpha", 1.0),
            "beta": params.get("beta", 0.0)
        },
        "source": {
            "type": "constant",
            "value": params.get("source_value", 0.0)
        },
        "dirichlet_boundaries": params.get("dirichlet_bc", {
            "xmin": True,
            "xmax": False,
            "ymin": True,
            "ymax": False,
            "zmin": True,
            "zmax": False
        })
    }
    out_path = os.path.join(workdir, "input.json")
    with open(out_path, "w") as f:
        json.dump(data, f, indent=2)
