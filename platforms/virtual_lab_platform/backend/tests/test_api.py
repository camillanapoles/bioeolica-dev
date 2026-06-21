"""
Integration tests for the Virtual Lab Platform API using TestClient and SQLite.
"""
import os
import tempfile
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Set test database before importing app
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
os.environ["DATABASE_URL"] = SQLALCHEMY_DATABASE_URL

# Now import app and dependencies
from platforms.virtual_lab_platform.backend.src.api.main import app
from platforms.virtual_lab_platform.backend.src.db.session import engine, SessionLocal, Base
from platforms.virtual_lab_platform.backend.src.db.repository import (
    SimulationRepository,
    MaterialRepository,
    SolverExecutionRepository,
    PublicationRepository,
)

@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database for each test."""
    # Drop and recreate tables
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Clean up
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(db_session):
    """Override the get_db dependency to use test session."""
    def get_test_db():
        try:
            yield db_session
        finally:
            pass
    app.dependency_overrides[app.dependency_overrides.get('get_db', None)] = get_test_db
    # Actually FastAPI's dependency override is done via app.dependency_overrides[get_db] = ...
    # We need to import get_db from main
    from platforms.virtual_lab_platform.backend.src.api.main import get_db
    app.dependency_overrides[get_db] = get_test_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

def test_create_material(client):
    response = client.post(
        "/materials/",
        json={"name": "Ti-6Al-4V", "density": 4.43, "youngs_modulus": 110e9},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Ti-6Al-4V"
    assert data["density"] == 4.43
    assert "id" in data

def test_create_simulation(client):
    # First create a material
    mat_resp = client.post(
        "/materials/",
        json={"name": "Aluminum", "density": 2.7, "youngs_modulus": 69e9},
    )
    material_id = mat_resp.json()["id"]
    # Create simulation
    sim_resp = client.post(
        "/simulations/",
        json={
            "name": "Tensile Test",
            "description": "Uniaxial tension",
            "parameters": {"solvers": ["calculix"], "calculix_params": {}},
            "material_id": material_id,
        },
    )
    assert sim_resp.status_code == 200
    sim_data = sim_resp.json()
    assert sim_data["name"] == "Tensile Test"
    assert sim_data["material_id"] == material_id
    assert sim_data["status"] == "created"

def test_run_simulation_endpoint(client):
    # Create material and simulation
    mat_resp = client.post(
        "/materials/",
        json={"name": "Copper", "density": 8.96, "youngs_modulus": 110e9},
    )
    material_id = mat_resp.json()["id"]
    sim_resp = client.post(
        "/simulations/",
        json={
            "name": "Thermal Test",
            "parameters": {"solvers": ["mfem"], "mfem_params": {}},
            "material_id": material_id,
        },
    )
    sim_id = sim_resp.json()["id"]
    # Trigger run
    run_resp = client.post(f"/simulations/{sim_id}/run")
    assert run_resp.status_code == 200
    run_data = run_resp.json()
    assert "task_id" in run_data
    # Check status endpoint
    status_resp = client.get(f"/simulations/{sim_id}/status")
    assert status_resp.status_code == 200
    status_data = status_resp.json()
    # Since we are not actually running celery worker, status will still be 'created' or 'running'? 
    # The task is sent but without worker it stays pending. However our endpoint returns immediately.
    # We'll accept any status.
    assert "status" in status_data

def test_list_materials(client):
    # Create two materials
    client.post("/materials/", json={"name": "Mat1", "density": 1.0})
    client.post("/materials/", json={"name": "Mat2", "density": 2.0})
    resp = client.get("/materials/")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 2

def test_publication_flow(client):
    mat_resp = client.post(
        "/materials/",
        json={"name": "Nickel", "density": 8.9},
    )
    material_id = mat_resp.json()["id"]
    sim_resp = client.post(
        "/simulations/",
        json={
            "name": "Fatigue Test",
            "parameters": {},
            "material_id": material_id,
        },
    )
    sim_id = sim_resp.json()["id"]
    pub_resp = client.post(
        "/publications/",
        json={
            "simulation_id": str(sim_id),
            "title": "Fatigue of Nickel",
            "authors": [{"name": "Alice"}],
            "abstract": "Study.",
            "doi": "10.1234/fatigue.2024",
        },
    )
    assert pub_resp.status_code == 200
    pub_data = pub_resp.json()
    assert pub_data["title"] == "Fatigue of Nickel"
    assert pub_data["simulation_id"] == str(sim_id)
