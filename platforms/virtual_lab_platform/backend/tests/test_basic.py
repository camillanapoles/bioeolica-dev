"""
Basic tests for the Virtual Lab Platform backend.
"""
def test_models_import():
    from platforms.virtual_lab_platform.backend.src.db.models import Base, Simulation, Material
    assert Base is not None
    assert Simulation is not None
    assert Material is not None

def test_repository_import():
    from platforms.virtual_lab_platform.backend.src.db.repository import SimulationRepository
    assert SimulationRepository is not None

def test_workflow_import():
    from platforms.virtual_lab_platform.backend.src.workflow.celery_app import celery_app
    assert celery_app is not None

def test_api_import():
    from platforms.virtual_lab_platform.backend.src.api.main import app
    assert app is not None
