"""Integration test — NLP → CAD → Analysis → Mesh → VVV."""
import pytest
from ai_assist_cad.nlp_parser import parse_project_parameters
from ai_assist_cad.knowledge_engine import KnowledgeEngine
from ai_assist_cad.cad_generator import CADGenerator
from ai_assist_cad.analysis_orchestrator import AnalysisOrchestrator
from ai_assist_cad.mesh_adaptive import AdaptiveMesh
from ai_assist_cad.layer_designer import LayerPattern, CompositeStack


def test_full_pipeline_generator():
    # 1. NLP
    params = parse_project_parameters("Projete gerador 3MW aço silício")
    assert params["machine_type"] == "generator"
    assert params["power_kW"] == 3000
    # 2. Knowledge
    ke = KnowledgeEngine()
    mat = ke.get_material("steel_4340")
    assert mat is not None
    # 3. CAD
    cg = CADGenerator(ke)
    design = cg.generate({**params, "rpm": 1500, "materials": ["steel_4340"]})
    assert design["total_parts"] >= 2
    # 4. Mesh
    mesh = AdaptiveMesh()
    m = mesh.generate("medium")
    assert m["level"] == "medium"
    # 5. Analysis
    ao = AnalysisOrchestrator()
    result = ao.run(["structural", "thermal"],
                    loads={"stress_1": 100e6, "stress_2": 50e6, "stress_12": 20e6,
                           "k": 50, "area": 2.0, "dT": 50, "dx": 0.02})
    assert "structural" in result
    assert "thermal" in result


def test_full_pipeline_turbine():
    params = parse_project_parameters("turbina eólica 5MW pás compósito")
    assert params["machine_type"] == "turbine"
    ke = KnowledgeEngine()
    cg = CADGenerator(ke)
    design = cg.generate(params)
    assert "blade" in [c["name"] for c in design["components"]]


def test_vvv_certification_in_pipeline():
    ao = AnalysisOrchestrator()
    ao.run(["structural"], loads={"stress_1": 50e6, "stress_2": 25e6, "stress_12": 10e6})
    cert = ao.certify()
    assert "overall_status" in cert
    assert "criteria" in cert


def test_material_layer_connection():
    ke = KnowledgeEngine()
    al = ke.get_material("aluminum_6061")
    pattern = LayerPattern(
        materials=[{"name":"aluminum","E_GPa":al["E_GPa"],"nu":al["nu"],
                     "fraction":0.97,"density":al["density"]},
                   {"name":"graphite","E_GPa":10,"nu":0.23,"fraction":0.03,"density":2250}],
        thickness_mm=2.0, process="shot_blasting")
    stack = CompositeStack(pattern, repetitions=3)
    assert stack.effective_properties["total_thickness_mm"] == 6.0
    assert stack.effective_properties["E1_GPa"] == pytest.approx(0.97*70+0.03*10, rel=0.1)
