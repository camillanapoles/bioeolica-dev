import pytest
import os
from ai_assist_cad.cad_generator import CADGenerator
from ai_assist_cad.knowledge_engine import KnowledgeEngine


@pytest.fixture
def cg():
    return CADGenerator()


@pytest.fixture
def cg_with_ke():
    ke = KnowledgeEngine("data")
    return CADGenerator(knowledge_engine=ke)


def test_generate_generator(cg):
    result = cg.generate({"machine_type": "generator", "materials": ["steel"], "power_kW": 3000})
    assert result["total_parts"] == 3
    names = [c["name"] for c in result["components"]]
    assert "stator" in names and "rotor" in names and "shaft" in names


def test_generate_turbine(cg):
    result = cg.generate({"machine_type": "turbine", "materials": ["composite"]})
    assert result["total_parts"] == 3
    names = [c["name"] for c in result["components"]]
    assert "blade" in names and "hub" in names and "tower" in names


def test_generate_unknown_fallback(cg):
    result = cg.generate({"machine_type": "unknown_machine", "materials": ["steel"]})
    assert result["total_parts"] == 3  # falls back to generator


def test_generate_with_knowledge_engine(cg_with_ke):
    result = cg_with_ke.generate({
        "machine_type": "generator", "materials": ["steel_4340"],
        "power_kW": 3000, "rpm": 1500
    })
    assert result["total_parts"] == 3
    shaft = [c for c in result["components"] if c["name"] == "shaft"][0]
    assert shaft["params"]["diameter_mm"] > 30  # dimensionado


def test_generate_step(cg):
    cg.generate({"machine_type": "generator", "materials": ["steel"]})
    exported = cg.generate_step("/tmp/test_cad_gen")
    assert len(exported) == 3
    assert all(os.path.exists(p) for p in exported)


def test_materials_used(cg):
    result = cg.generate({"machine_type": "motor", "materials": ["copper", "steel"]})
    assert "copper" in result["materials_used"]
