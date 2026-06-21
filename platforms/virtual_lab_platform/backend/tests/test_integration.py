"""
Integration test skeleton for the Virtual Lab Platform.
These tests demonstrate how to test the full workflow with authentication.
Note: They require a running test database and may require mocking of external services (Docker, Celery worker).
"""
import os
import json
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

# Set test environment variables before importing the app
os.environ["DATABASE_URL"] = "sqlite:///./test_integration.db"
os.environ["WORKDIR_BASE"] = "/tmp/virtuallab_test_workdir"
os.environ["STORAGE_BASE"] = "/tmp/virtuallab_test_storage"
os.environ["SECRET_KEY"] = "testsecretkey"
os.environ["OPENFOAM_IMAGE"] = "openfoam/openfoam2312"
os.environ["CALCULIX_IMAGE"] = "calculix:latest"
os.environ["MFEM_IMAGE"] = "mfem:latest"

# Now import the app
from platforms.virtual_lab_platform.backend.src.api.main import app
from platforms.virtual_lab_platform.backend.src.db.session import engine, Base, SessionLocal
from platforms.virtual_lab_platform.backend.src.db.models import Simulation, Material

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    """Create tables before each test and drop after."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_register_and_login():
    # Register a user (in a real system, we would have a registration endpoint;
    # for now we rely on the fake users in auth module)
    # We'll test login with the fake admin user.
    login_data = {
        "username": "admin",
        "password": "adminpass",
    }
    response = client.post("/token", data=login_data)
    assert response.status_code == 200
    token = response.json()["access_token"]
    assert token is not None
    return token

def test_create_material_and_simulation(auth_token):
    # Create a material
    material_data = {
        "name": "Ti-6Al-4V",
        "formula": "Ti6Al4V",
        "density": 4.43,
        "youngs_modulus": 114e9,
        "poisson_ratio": 0.34,
        "thermal_conductivity": 6.7,
        "specific_heat": 520,
        "melting_point": 1923,
    }
    headers = {"Authorization": f"Bearer {auth_token}"}
    resp = client.post("/materials/", json=material_data, headers=headers)
    assert resp.status_code == 200
    material = resp.json()
    material_id = material["id"]
    assert material["name"] == "Ti-6Al-4V"

    # Create a simulation using the material
    sim_data = {
        "name": "Ti-6Al-4V Tensile Test",
        "description": "Validation example coupon",
        "parameters": {
            "solvers": ["openfoam"],  # using openfoam as placeholder
            "openfoam_params": {
                "velocity": 10.0,
                "viscosity": 1.5e-5,
                "length": 10.0,
                "width": 5.0,
                "height": 2.0,
            }
        },
        "material_id": material_id,
    }
    resp = client.post("/simulations/", json=sim_data, headers=headers)
    assert resp.status_code == 200
    simulation = resp.json()
    sim_id = simulation["id"]
    assert simulation["name"] == "Ti-6Al-4V Tensile Test"
    assert simulation["material_id"] == material_id
    assert simulation["status"] == "created"

    # Try to run the simulation (this will trigger the Celery task; in a test environment without a worker, it will stay pending)
    resp = client.post(f"/simulations/{sim_id}/run", headers=headers)
    # The endpoint returns 200 immediately because it just sends the task to the broker.
    assert resp.status_code == 200
    data = resp.json()
    assert "task_id" in data

    # Check status (should still be created or running depending on worker)
    resp = client.get(f"/simulations/{sim_id}/status", headers=headers)
    assert resp.status_code == 200
    status_data = resp.json()
    assert status_data["simulation_id"] == sim_id
    # In a real test with a worker, we would expect the status to eventually become completed.
    # For now, we accept any status.
    assert "status" in status_data

    # TODO: Add more steps to check that results are stored, etc.

if __name__ == "__main__":
    # Simple manual test execution
    token = test_register_and_login()
    print("Login successful, token:", token[:10] + "...")
    test_create_material_and_simulation(token)
    print("Integration test passed.")
