import pytest
from ai_assist_cad.knowledge_engine import KnowledgeEngine


@pytest.fixture
def ke():
    return KnowledgeEngine("data")


def test_load_materials(ke):
    assert len(ke.materials) >= 5
    mat = ke.get_material("steel_4340")
    assert mat["E_GPa"] == 205
    assert mat["sigma_y_MPa"] == 710


def test_get_material_not_found(ke):
    assert ke.get_material("unknown_material") is None


def test_list_materials(ke):
    mats = ke.list_materials()
    assert isinstance(mats, list)
    assert len(mats) > 0


def test_dimension_shaft(ke):
    shaft = ke.dimension_shaft(torque_Nm=20000)
    assert shaft["diameter_mm"] > 30
    assert shaft["diameter_mm"] < 200
    assert shaft["torque_Nm"] == 20000


def test_dimension_stator(ke):
    stator = ke.dimension_stator_outer(power_kW=3000, rpm=1500, poles=4)
    assert stator["diameter_mm"] > 200
    assert stator["diameter_mm"] < 1000
    assert stator["frequency_Hz"] == 50.0


def test_estimate_mass(ke):
    mass = ke.estimate_mass(volume_m3=1.0, material_key="steel_4340")
    assert mass == 7850.0  # density of 4340 steel
    mass_unknown = ke.estimate_mass(volume_m3=1.0, material_key="unknown")
    assert mass_unknown is None
