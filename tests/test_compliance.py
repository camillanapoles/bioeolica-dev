"""Tests for ComplianceComponent."""

import numpy as np
import openmdao.api as om
import pytest
from src.topopt.compliance import ComplianceComponent


def test_compliance_dot_product():
    """Compliance = f^T * u."""
    comp = ComplianceComponent()
    prob = om.Problem()
    prob.model.add_subsystem("obj", comp, promotes=["*"])
    prob.setup()

    u = np.array([1.0, 2.0, 3.0])
    f = np.array([4.0, 5.0, 6.0])
    prob.set_val("displacements", u)
    prob.set_val("load_vector", f)
    prob.run_model()

    expected = np.dot(f, u)
    assert float(prob.get_val("compliance_value")[0]) == pytest.approx(expected)


if __name__ == "__main__":
    pytest.main([__file__])
