"""Tests for SIMPFemComponent."""

import numpy as np
import openmdao.api as om
import pytest
from src.topopt.fem_component import SIMPFemComponent


def test_fem_component_setup():
    """FEM component can be instantiated."""
    comp = SIMPFemComponent(nelx=10, nely=5)
    assert comp.nelx == 10
    assert comp.nely == 5
    assert comp.nelem == 50
    assert comp.ndof > 0


def test_fem_component_forward():
    """FEM component produces displacements and compliance from valid inputs."""
    nelx, nely = 8, 4
    nelem = nelx * nely
    ndof = 2 * (nelx + 1) * (nely + 1)

    comp = SIMPFemComponent(nelx=nelx, nely=nely)
    prob = om.Problem()
    prob.model.add_subsystem("fea", comp, promotes=["*"])
    prob.setup()

    x = np.full(nelem, 0.5)
    f = np.zeros(ndof)
    f[ndof // 2] = -1.0

    prob.set_val("density_field", x)
    prob.set_val("load_vector", f)
    prob.run_model()

    u = prob.get_val("displacements")
    c = prob.get_val("compliance")
    assert u.shape == (ndof,)
    assert c.shape == (1,)
    assert float(c[0]) > 0


def test_fem_component_stiffer_density():
    """Higher density produces lower compliance (stiffer structure)."""
    nelx, nely = 6, 3
    nelem = nelx * nely
    ndof = 2 * (nelx + 1) * (nely + 1)

    comp = SIMPFemComponent(nelx=nelx, nely=nely)

    def compliance_for_density(rho):
        prob = om.Problem()
        prob.model.add_subsystem("fea", comp, promotes=["*"])
        prob.setup()
        prob.set_val("density_field", np.full(nelem, rho))
        f = np.zeros(ndof)
        f[ndof // 2] = -1.0
        prob.set_val("load_vector", f)
        prob.run_model()
        return float(prob.get_val("compliance")[0])

    c_low = compliance_for_density(0.3)
    c_high = compliance_for_density(0.9)
    assert c_high < c_low, f"Expected lower compliance at higher density: {c_high} vs {c_low}"


if __name__ == "__main__":
    pytest.main([__file__])
