"""Tests for VolumeConstraint."""

import numpy as np
import openmdao.api as om
import pytest
from src.topopt.volume_constraint import VolumeConstraint


def test_volume_uniform():
    """Uniform density produces correct volume fraction."""
    comp = VolumeConstraint()
    prob = om.Problem()
    prob.model.add_subsystem("vc", comp, promotes=["*"])
    prob.setup()

    prob.set_val("density_field", np.full(100, 0.3))
    prob.run_model()
    assert float(prob.get_val("volume_fraction")[0]) == pytest.approx(0.3)


def test_volume_empty():
    """Zero density produces zero volume fraction."""
    comp = VolumeConstraint()
    prob = om.Problem()
    prob.model.add_subsystem("vc", comp, promotes=["*"])
    prob.setup()

    prob.set_val("density_field", np.zeros(50))
    prob.run_model()
    assert float(prob.get_val("volume_fraction")[0]) == pytest.approx(0.0)


def test_volume_all_ones():
    """Unit density produces unit volume fraction."""
    comp = VolumeConstraint()
    prob = om.Problem()
    prob.model.add_subsystem("vc", comp, promotes=["*"])
    prob.setup()

    prob.set_val("density_field", np.ones(25))
    prob.run_model()
    assert float(prob.get_val("volume_fraction")[0]) == pytest.approx(1.0)


if __name__ == "__main__":
    pytest.main([__file__])
