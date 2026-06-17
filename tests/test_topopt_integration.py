"""Integration tests for topology optimization pipeline."""

import numpy as np
import pytest
from src.topopt.run_optimization import run_topopt


def test_topopt_small_converges():
    """Small topology optimization runs without error and produces valid density field."""
    result = run_topopt(nelx=12, nely=6, vol_frac=0.3, max_iter=15, verbose=False)
    assert result["compliance"] > 0
    x = result["density_field"]
    assert x.shape == (72,)
    assert np.all(x >= 0) and np.all(x <= 1)


def test_topopt_volume_constraint():
    """Optimized density field respects volume fraction constraint within margin."""
    result = run_topopt(nelx=10, nely=5, vol_frac=0.3, max_iter=10, verbose=False)
    vol = result["volume_fraction"]
    assert vol <= 0.31, f"Volume fraction {vol} exceeds 0.3 by more than margin"


def test_topopt_lower_volume_stiffer():
    """Lower volume fraction produces higher compliance (less stiff)."""
    r1 = run_topopt(nelx=8, nely=4, vol_frac=0.4, max_iter=8, verbose=False)
    r2 = run_topopt(nelx=8, nely=4, vol_frac=0.2, max_iter=8, verbose=False)
    assert r2["compliance"] > r1["compliance"], (
        f"Expected higher compliance at lower volume: {r2['compliance']} vs {r1['compliance']}"
    )


if __name__ == "__main__":
    pytest.main([__file__])
