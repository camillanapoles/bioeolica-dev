"""Tests: AdaptiveMesh + GPUAccelerator."""
import pytest
from ai_assist_cad.mesh_adaptive import AdaptiveMesh
from ai_assist_cad.gpu_accelerator import GPUAccelerator


def test_mesh_generate_levels():
    mesh = AdaptiveMesh(base_size_mm=10.0)
    c = mesh.generate("coarse")
    m = mesh.generate("medium")
    f = mesh.generate("fine")
    assert c["element_size_mm"] == 10.0
    assert m["element_size_mm"] == 5.0
    assert f["element_size_mm"] == 2.5
    assert c["elements_estimated"] < f["elements_estimated"]


def test_mesh_invalid_level():
    mesh = AdaptiveMesh()
    with pytest.raises(ValueError, match="Unknown level"):
        mesh.generate("ultra_fine")


def test_convergence_study_passes():
    mesh = AdaptiveMesh()
    # Results converging to 100: [100.5, 100.3, 100.1] — max delta < 0.5%
    result = mesh.convergence_study([100.5, 100.3, 100.1])
    assert result["converged"] is True


def test_convergence_study_fails():
    mesh = AdaptiveMesh()
    result = mesh.convergence_study([1.0, 5.0, 10.0])
    assert result["converged"] is False


def test_gpu_accelerator_fallback():
    acc = GPUAccelerator()
    assert hasattr(acc, "is_available")
    assert hasattr(acc, "solve_cg")


def test_gpu_benchmark():
    acc = GPUAccelerator()
    result = acc.benchmark_vs_cpu(size=50)
    assert result["matrix_size"] == 50
    assert result["cpu_time_s"] > 0
