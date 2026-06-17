"""tests/test_analysis_orchestrator.py"""
import pytest
from ai_assist_cad.analysis_orchestrator import AnalysisOrchestrator


def test_run_structural():
    ao = AnalysisOrchestrator()
    result = ao.run(
        domains=["structural"],
        loads={"stress_1": 100e6, "stress_2": 50e6, "stress_12": 20e6},
    )
    assert "structural" in result
    assert result["structural"]["von_mises_MPa"] > 0


def test_run_multi_domain():
    ao = AnalysisOrchestrator()
    result = ao.run(
        domains=["structural", "thermal"],
        loads={"stress_1": 100e6, "stress_2": 50e6, "stress_12": 20e6,
               "k": 0.5, "area": 2.0, "dT": 50, "dx": 0.02},
    )
    assert "structural" in result
    assert "thermal" in result


def test_run_all_four_domains():
    ao = AnalysisOrchestrator()
    result = ao.run(
        domains=["structural", "thermal", "fluid", "electromagnetic"],
        loads={"stress_1": 100e6, "stress_2": 50e6, "stress_12": 20e6,
               "k": 0.5, "area": 2.0, "dT": 50, "dx": 0.02,
               "density": 1.2, "velocity": 10, "length": 1.0,
               "rpm": 1500, "poles": 4},
    )
    assert "structural" in result
    assert "thermal" in result
    assert "fluid" in result
    assert "electromagnetic" in result
    assert result["electromagnetic"]["frequency_Hz"] == 50.0


def test_status_present():
    ao = AnalysisOrchestrator()
    result = ao.run(domains=["structural"],
                    loads={"stress_1": 1e6, "stress_2": 0, "stress_12": 0})
    assert "status" in result
    assert result["status"]["structural"] == "PASS"


def test_certify():
    ao = AnalysisOrchestrator()
    ao.run(domains=["structural"],
           loads={"stress_1": 100e6, "stress_2": 50e6, "stress_12": 20e6})
    cert = ao.certify()
    assert "overall_status" in cert
    assert "criteria" in cert


def test_portuguese_domain_names():
    ao = AnalysisOrchestrator()
    result = ao.run(
        domains=["estrutural", "térmico"],
        loads={"stress_1": 100e6, "stress_2": 50e6, "stress_12": 20e6,
               "k": 0.5, "area": 2.0, "dT": 50, "dx": 0.02},
    )
    assert "structural" in result
    assert "thermal" in result
