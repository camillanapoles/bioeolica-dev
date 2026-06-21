"""
Unit tests for solver preparation functions.
"""
import os
import tempfile
import json
from pathlib import Path

import pytest

# Set env vars before importing the modules that use them
os.environ["WORKDIR_BASE"] = "/tmp/virtuallab_test"
os.environ["STORAGE_BASE"] = "/tmp/virtuallab_storage_test"
os.environ["OPENFOAM_IMAGE"] = "openfoam/openfoam2312"
os.environ["CALCULIX_IMAGE"] = "calculix:latest"
os.environ["MFEM_IMAGE"] = "mfem:latest"

from platforms.virtual_lab_platform.backend.src.workflow.solvers import openfoam, calculix, mfem
from platforms.virtual_lab_platform.backend.src.workflow.tasks import _prepare_solver_input, _store_solver_output

@pytest.fixture
def clean_dirs():
    """Clean up test directories before and after."""
    workdir_base = os.getenv("WORKDIR_BASE")
    storage_base = os.getenv("STORAGE_BASE")
    # Remove if exist
    shutil = __import__('shutil')
    if os.path.exists(workdir_base):
        shutil.rmtree(workdir_base)
    if os.path.exists(storage_base):
        shutil.rmtree(storage_base)
    yield
    # Clean after
    if os.path.exists(workdir_base):
        shutil.rmtree(workdir_base)
    if os.path.exists(storage_base):
        shutil.rmtree(storage_base)

def test_prepare_openfoam_case(clean_dirs):
    workdir = tempfile.mkdtemp(dir=os.getenv("WORKDIR_BASE"))
    params = {"velocity": 10.0, "viscosity": 1.5e-5, "length": 1.0, "width": 0.5, "height": 0.2}
    openfoam.prepare_openfoam_case(params, workdir)
    # Check that expected files exist
    assert os.path.exists(os.path.join(workdir, "system", "controlDict"))
    assert os.path.exists(os.path.join(workdir, "system", "blockMeshDict"))
    assert os.path.exists(os.path.join(workdir, "constant", "transportProperties"))
    # Check content for velocity
    with open(os.path.join(workdir, "system", "controlDict"), "r") as f:
        content = f.read()
        assert "velocities    (10 0 0);" in content

def test_prepare_calculix_case(clean_dirs):
    workdir = tempfile.mkdtemp(dir=os.getenv("WORKDIR_BASE"))
    params = {"length": 10, "width": 10, "height": 10, "youngs_modulus": 210000, "poisson_ratio": 0.3, "density": 7.85e-3, "force": 1000}
    calculix.prepare_calculix_case(params, workdir)
    inp_path = os.path.join(workdir, "model.inp")
    assert os.path.exists(inp_path)
    with open(inp_path, "r") as f:
        content = f.read()
        assert "*MATERIAL, NAME=MAT1" in content
        assert "*ELASTIC" in content
        assert "210000, 0.3" in content

def test_prepare_mfem_case(clean_dirs):
    workdir = tempfile.mkdtemp(dir=os.getenv("WORKDIR_BASE"))
    params = {"mesh_type": "cube", "nx": 8, "ny": 8, "nz": 8, "order": 2, "alpha": 1.0, "beta": 0.1, "source_value": 5.0}
    mfem.prepare_mfem_case(params, workdir)
    json_path = os.path.join(workdir, "input.json")
    assert os.path.exists(json_path)
    with open(json_path, "r") as f:
        data = json.load(f)
        assert data["mesh"]["type"] == "cube"
        assert data["mesh"]["nx"] == 8
        assert data["fem_order"] == 2
        assert data["coefficients"]["alpha"] == 1.0
        assert data["source"]["value"] == 5.0

def test_prepare_solver_input_integration(clean_dirs):
    # Test that _prepare_solver_input dispatches correctly
    params_openfoam = {"velocity": 5, "viscosity": 1e-5, "length": 2, "width": 2, "height": 2}
    workdir = _prepare_solver_input("openfoam", params_openfoam)
    assert workdir.startswith(os.getenv("WORKDIR_BASE"))
    assert os.path.exists(os.path.join(workdir, "system", "controlDict"))
    # Cleanup
    shutil = __import__('shutil')
    shutil.rmtree(workdir, ignore_errors=True)

    params_calculix = {"length": 5, "width": 5, "height": 5, "youngs_modulus": 200000, "poisson_ratio": 0.25, "density": 7.8e-3, "force": 500}
    workdir2 = _prepare_solver_input("calculix", params_calculix)
    assert workdir2.startswith(os.getenv("WORKDIR_BASE"))
    assert os.path.exists(os.path.join(workdir2, "model.inp"))
    shutil.rmtree(workdir2, ignore_errors=True)

    params_mfem = {"mesh_type": "square", "nx": 4, "ny": 4, "nz": 1, "order": 1, "alpha": 1.0, "beta": 0.0, "source_value": 0.0}
    workdir3 = _prepare_solver_input("mfem", params_mfem)
    assert workdir3.startswith(os.getenv("WORKDIR_BASE"))
    assert os.path.exists(os.path.join(workdir3, "input.json"))
    shutil.rmtree(workdir3, ignore_errors=True)

def test_store_solver_output(clean_dirs):
    workdir = tempfile.mkdtemp(dir=os.getenv("WORKDIR_BASE"))
    # Create a dummy results.json
    dummy_results = {"test": 123}
    results_path = os.path.join(workdir, "results.json")
    with open(results_path, "w") as f:
        json.dump(dummy_results, f)
    # Call store
    rel_path = _store_solver_output("dummy", workdir, dummy_results)
    # Ensure the storage directory exists under STORAGE_BASE
    storage_base = os.getenv("STORAGE_BASE")
    assert rel_path.startswith("virtuallab_")
    full_path = os.path.join(storage_base, rel_path)
    assert os.path.exists(full_path)
    assert os.path.exists(os.path.join(full_path, "results.json"))
    with open(os.path.join(full_path, "results.json"), "r") as f:
        stored = json.load(f)
        assert stored == dummy_results
    # Cleanup
    shutil = __import__('shutil')
    shutil.rmtree(workdir, ignore_errors=True)
    shutil.rmtree(full_path, ignore_errors=True)
