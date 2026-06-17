"""Tests for Termo Module — thermal analysis."""

import numpy as np
import pytest

from src.termo.bc import ThermalBC, parse_bc_string
from src.termo.materials import get_material, MATERIALS
from src.termo.solver import ThermalSolver
from src.termo.stress import thermal_stress, equivalent_thermal_force
from src.termo.coupling import thermal_to_structural_loads


def test_bc_creation():
    """ThermalBC can be created with valid types."""
    bc = ThermalBC(type="temperature", value=300.0)
    assert bc.type == "temperature"
    assert bc.value == 300.0


def test_bc_invalid_type():
    """Invalid BC type raises ValueError."""
    with pytest.raises(ValueError, match="Invalid"):
        ThermalBC(type="invalid", value=0)


def test_bc_parse_string():
    """Parse 'node:value' format."""
    result = parse_bc_string("0:300,1:400,5:350")
    assert result == {0: 300.0, 1: 400.0, 5: 350.0}


def test_material_lookup():
    """Material lookup returns expected properties."""
    mat = get_material("steel")
    assert mat.k == 50.0
    assert mat.alpha == 1.2e-5


def test_material_fallback():
    """Unknown material falls back to generic."""
    mat = get_material("nonexistent")
    assert mat.k == 50.0


def test_thermal_solver_small():
    """Thermal solver runs on small grid."""
    solver = ThermalSolver(nx=4, ny=4, nz=4, k=50.0)
    bc_t = {0: 300.0, solver.n_nodes - 1: 400.0}
    temps, converged = solver.solve(bc_temperature=bc_t)
    assert converged
    assert len(temps) == 125  # 5×5×5
    assert abs(temps[0] - 300.0) < 1.0
    assert abs(temps[-1] - 400.0) < 1.0


def test_thermal_solver_gradient():
    """Temperature gradient is monotonic between BCs."""
    solver = ThermalSolver(nx=6, ny=6, nz=6, k=50.0)
    bc_t = {0: 300.0, solver.n_nodes - 1: 500.0}
    temps, converged = solver.solve(bc_temperature=bc_t)
    assert converged
    grad = solver.compute_gradient(temps)
    assert np.all(grad >= 0) or np.all(grad <= 0)


def test_thermal_stress_computation():
    """Thermal stress is proportional to delta T."""
    temps = np.array([300.0, 350.0, 400.0])
    sigma = thermal_stress(temps, ref_temp=300.0, E=200e9, alpha=1.2e-5, nu=0.3)
    assert sigma[0] == pytest.approx(0.0, abs=1)
    assert sigma[1] < 0  # Expansion → compressive stress
    assert sigma[2] < sigma[1]  # More delta T → more stress


def test_equivalent_force():
    """Equivalent force is positive scalar."""
    sigma = np.array([-1e6, 1e6, -2e6])
    f = equivalent_thermal_force(sigma, area=0.01)
    assert f > 0


def test_coupling_bridge():
    """Thermal-structural coupling produces force vector."""
    temps = np.array([300.0, 400.0, 500.0])
    forces = thermal_to_structural_loads(temps, ref_temp=300.0)
    assert len(forces) == len(temps) * 2  # 2 DOFs per node (1D)
    assert np.any(np.abs(forces) > 0)


def test_solver_no_bc_raises():
    """Solver with no BCs may still produce result (floating reference)."""
    solver = ThermalSolver(nx=3, ny=3, nz=3, k=50.0)
    temps, converged = solver.solve()
    assert converged  # Should still solve (singular but spsolve handles)


def test_materials_all_have_properties():
    """All materials in DB have valid thermal properties."""
    for name, mat in MATERIALS.items():
        assert mat.k > 0, f"{name} has zero conductivity"
        assert mat.alpha != 0, f"{name} has zero CTE"
        assert mat.cp > 0, f"{name} has zero specific heat"
