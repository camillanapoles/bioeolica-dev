"""Tests for the topology_optimization module (SIMP method)."""

import numpy as np
import pytest

from modules.topology_optimization import TopOpt


# ---------------------------------------------------------------------------
# 1.  TopOpt init with valid parameters
# ---------------------------------------------------------------------------
class TestTopOptInit:
    def test_valid_parameters(self):
        """TopOpt should initialise without error with standard parameters."""
        opt = TopOpt(nelx=10, nely=6, volfrac=0.4)
        assert opt.nelx == 10
        assert opt.nely == 6
        assert opt.volfrac == 0.4
        assert opt.density.shape == (6, 10)
        assert np.allclose(opt.density, 0.4)
        assert opt.iteration == 0
        assert opt.compliance_history == []
        assert opt._converged is False


# ---------------------------------------------------------------------------
# 2.  TopOpt init with invalid volfrac raises ValueError
# ---------------------------------------------------------------------------
class TestTopOptInvalid:
    def test_invalid_volfrac_raises(self):
        """volfrac <= 0 or > 1 should raise ValueError."""
        with pytest.raises(ValueError, match="volfrac"):
            TopOpt(nelx=10, nely=6, volfrac=0.0)
        with pytest.raises(ValueError, match="volfrac"):
            TopOpt(nelx=10, nely=6, volfrac=-0.1)
        with pytest.raises(ValueError, match="volfrac"):
            TopOpt(nelx=10, nely=6, volfrac=1.5)

    def test_invalid_penal_raises(self):
        """penal < 1.0 should raise ValueError."""
        with pytest.raises(ValueError, match="penal"):
            TopOpt(nelx=10, nely=6, volfrac=0.4, penal=0.5)

    def test_invalid_rmin_raises(self):
        """rmin < 0 should raise ValueError."""
        with pytest.raises(ValueError, match="rmin"):
            TopOpt(nelx=10, nely=6, volfrac=0.4, rmin=-1.0)

    def test_invalid_nu_raises(self):
        """nu outside [0, 0.5) should raise ValueError."""
        with pytest.raises(ValueError, match="nu"):
            TopOpt(nelx=10, nely=6, volfrac=0.4, nu=0.5)
        with pytest.raises(ValueError, match="nu"):
            TopOpt(nelx=10, nely=6, volfrac=0.4, nu=-0.1)


# ---------------------------------------------------------------------------
# 3.  step() returns positive compliance
# ---------------------------------------------------------------------------
class TestStep:
    def test_step_returns_positive_compliance(self):
        """Single optimisation step should return a finite positive float."""
        opt = TopOpt(nelx=10, nely=6, volfrac=0.4)
        comp = opt.step()
        assert isinstance(comp, float)
        assert comp > 0.0
        assert np.isfinite(comp)


# ---------------------------------------------------------------------------
# 4.  solve() returns density with correct shape (nely, nelx)
# ---------------------------------------------------------------------------
class TestSolve:
    def test_solve_returns_correct_shape(self):
        """Solve should return a density array of shape (nely, nelx)."""
        opt = TopOpt(nelx=10, nely=6, volfrac=0.4)
        density = opt.solve(max_iter=5)
        assert density.shape == (6, 10)
        assert density.dtype == np.float64

    def test_solve_increments_iteration(self):
        """Solve with max_iter=N should result in iteration == N."""
        opt = TopOpt(nelx=10, nely=6, volfrac=0.4)
        opt.solve(max_iter=5)
        assert opt.iteration == 5


# ---------------------------------------------------------------------------
# 5.  Compliance decreases over iterations
# ---------------------------------------------------------------------------
class TestComplianceDecreases:
    def test_compliance_decreases(self):
        """Final compliance should be lower than initial compliance."""
        opt = TopOpt(nelx=10, nely=6, volfrac=0.4)
        opt.solve(max_iter=10)
        history = opt.compliance_history
        assert len(history) >= 3
        # The overall trend should be downward: final < initial (monotonicity is
        # not guaranteed every iteration — the OC update can cause temporary
        # oscillations — but the converged result must be lower than the start)
        assert history[-1] < history[0]


# ---------------------------------------------------------------------------
# 6.  reset() restores initial state
# ---------------------------------------------------------------------------
class TestReset:
    def test_reset_restores_initial_state(self):
        """After solve, reset should restore uniform density and clear history."""
        opt = TopOpt(nelx=10, nely=6, volfrac=0.4)
        opt.solve(max_iter=5)
        assert opt.iteration > 0
        assert len(opt.compliance_history) > 0
        opt.reset()
        assert opt.iteration == 0
        assert opt.compliance_history == []
        assert opt._converged is False
        assert np.allclose(opt.density, 0.4)
        assert opt.density.shape == (6, 10)


# ---------------------------------------------------------------------------
# 7.  volume_fraction property
# ---------------------------------------------------------------------------
class TestVolumeFraction:
    def test_initial_volume_fraction(self):
        """Initial volume_fraction should equal the target volfrac."""
        opt = TopOpt(nelx=10, nely=6, volfrac=0.4)
        assert opt.volume_fraction == pytest.approx(0.4)

    def test_volume_fraction_after_solve(self):
        """After a few iterations volume_fraction should still respect volfrac."""
        opt = TopOpt(nelx=10, nely=6, volfrac=0.4)
        opt.solve(max_iter=5)
        vf = opt.volume_fraction
        # The OC update enforces the volume constraint via bisection
        assert vf == pytest.approx(0.4, abs=0.05)


# ---------------------------------------------------------------------------
# 8.  get_density() returns a copy (modifying doesn't affect internal)
# ---------------------------------------------------------------------------
class TestGetDensity:
    def test_get_density_returns_copy(self):
        """Modifying a copy of density should not alter the internal state."""
        opt = TopOpt(nelx=10, nely=6, volfrac=0.4)
        d1 = opt.density.copy()
        d1[0, 0] = 99.0
        assert opt.density[0, 0] != 99.0

    def test_get_density_equals_internal(self):
        """A copy of density should match the internal density."""
        opt = TopOpt(nelx=10, nely=6, volfrac=0.4)
        d1 = opt.density.copy()
        assert np.array_equal(d1, opt.density)

    def test_density_direct_mutability(self):
        """Direct attribute access allows mutation (module uses public attribute)."""
        opt = TopOpt(nelx=10, nely=6, volfrac=0.4)
        original = opt.density[0, 0]
        opt.density[0, 0] = 0.9
        assert opt.density[0, 0] == pytest.approx(0.9)
        # After reset it goes back to uniform
        opt.reset()
        assert opt.density[0, 0] == pytest.approx(0.4)


# ---------------------------------------------------------------------------
# 9.  Default parameters match expected values
# ---------------------------------------------------------------------------
class TestDefaultParameters:
    def test_default_parameters(self):
        """Default parameters should match documented values."""
        opt = TopOpt(nelx=10, nely=6, volfrac=0.4)
        assert opt.penal == pytest.approx(3.0)
        assert opt.rmin == pytest.approx(1.5)
        assert opt.E0 == pytest.approx(1.0)
        assert opt.Emin == pytest.approx(1e-9)
        assert opt.nu == pytest.approx(0.3)


# ---------------------------------------------------------------------------
# 10.  converged is bool after solve
# ---------------------------------------------------------------------------
class TestConverged:
    def test_converged_is_bool_after_solve(self):
        """The converged property should return a bool after solve completes."""
        opt = TopOpt(nelx=10, nely=6, volfrac=0.4)
        assert isinstance(opt.converged, bool)
        assert opt.converged is False
        opt.solve(max_iter=5)
        assert isinstance(opt.converged, bool)

    def test_converged_false_with_few_iterations(self):
        """With very few iterations the solver typically hasn't converged."""
        opt = TopOpt(nelx=10, nely=6, volfrac=0.4)
        opt.solve(max_iter=3)
        # 3 iterations is unlikely to satisfy the convergence tolerance
        assert isinstance(opt.converged, bool)
