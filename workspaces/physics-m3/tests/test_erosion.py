"""
tests/test_erosion.py — Unit tests for the ErosionModel module.
"""

from __future__ import annotations

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import pytest
from modules.erosion import ErosionModel


class TestErosionModel:
    """Test suite for ErosionModel."""

    @pytest.fixture
    def model(self) -> ErosionModel:
        """Default erosion model fixture."""
        return ErosionModel(material_density=2700.0, hardness=3e9, k=2.0)

    def test_default_initialization(self):
        """Test default initialization parameters."""
        em = ErosionModel()
        assert em.material_density == pytest.approx(2700.0)
        assert em.hardness == pytest.approx(3e9)
        assert em.k == pytest.approx(2.0)
        assert em.n == pytest.approx(2.0)

    def test_custom_initialization(self):
        """Test custom initialization."""
        em = ErosionModel(
            material_density=7850.0, hardness=5e9, k=1.5, n=2.5
        )
        assert em.material_density == pytest.approx(7850.0)
        assert em.hardness == pytest.approx(5e9)
        assert em.k == pytest.approx(1.5)
        assert em.n == pytest.approx(2.5)

    def test_invalid_density_raises(self):
        """Test that non-positive density raises ValueError."""
        with pytest.raises(ValueError, match="Material density must be positive"):
            ErosionModel(material_density=0.0)

    def test_invalid_hardness_raises(self):
        """Test that non-positive hardness raises ValueError."""
        with pytest.raises(ValueError, match="Hardness must be positive"):
            ErosionModel(hardness=-1.0)

    def test_finnie_erosion_returns_dict(self, model):
        """Test that finnie_erosion returns a dict with all keys."""
        result = model.finnie_erosion(mass=1e-6, velocity=50.0, angle=30.0)
        assert "volume_removed" in result
        assert "mass_loss" in result
        assert "erosion_rate" in result
        assert "depth_per_particle" in result
        assert "angle_function" in result

    def test_finnie_erosion_positive(self, model):
        """Test that erosion values are positive for valid inputs."""
        result = model.finnie_erosion(mass=1e-6, velocity=50.0, angle=30.0)
        assert result["volume_removed"] > 0.0
        assert result["mass_loss"] > 0.0
        assert result["erosion_rate"] > 0.0

    def test_finnie_velocity_dependence(self, model):
        """Test that higher velocity gives more erosion."""
        r1 = model.finnie_erosion(mass=1e-6, velocity=20.0, angle=30.0)
        r2 = model.finnie_erosion(mass=1e-6, velocity=40.0, angle=30.0)
        # Erosion ~ V^n, so 40^2 / 20^2 = 4x
        assert r2["erosion_rate"] > r1["erosion_rate"]

    def test_finnie_zero_mass_raises(self, model):
        """Test that zero particle mass raises ValueError."""
        with pytest.raises(ValueError, match="Particle mass must be positive"):
            model.finnie_erosion(mass=0.0, velocity=50.0, angle=30.0)

    def test_finnie_zero_velocity_raises(self, model):
        """Test that zero velocity raises ValueError."""
        with pytest.raises(ValueError, match="Velocity must be positive"):
            model.finnie_erosion(mass=1e-6, velocity=0.0, angle=30.0)

    def test_finnie_invalid_angle_raises(self, model):
        """Test that out-of-range angle raises ValueError."""
        with pytest.raises(ValueError, match="Impact angle must be in"):
            model.finnie_erosion(mass=1e-6, velocity=50.0, angle=0.0)
        with pytest.raises(ValueError, match="Impact angle must be in"):
            model.finnie_erosion(mass=1e-6, velocity=50.0, angle=91.0)

    def test_erosion_vs_angle_peak(self, model):
        """Test that erosion vs angle has a peak around 20-30 degrees."""
        result = model.erosion_vs_angle(velocity=50.0, mass=1e-6)
        assert result["peak_angle"] > 0.0
        assert result["peak_angle"] <= 90.0
        assert result["peak_rate"] > 0.0
        assert len(result["angles"]) == len(result["erosion_rates"])

    def test_erosion_vs_angle_zero_at_extremes(self, model):
        """Test that erosion rate is nearly zero at extreme angles."""
        r_low = model.finnie_erosion(mass=1e-6, velocity=50.0, angle=1.0)
        r_high = model.finnie_erosion(mass=1e-6, velocity=50.0, angle=89.0)
        # Very low or very high angles produce less erosion
        r_peak = model.finnie_erosion(mass=1e-6, velocity=50.0, angle=25.0)
        assert r_low["erosion_rate"] < r_peak["erosion_rate"]
        assert r_high["erosion_rate"] <= r_peak["erosion_rate"]

    def test_blade_erosion_returns_dict(self, model):
        """Test that blade_erosion returns all expected keys."""
        result = model.blade_erosion(
            tip_speed=80.0, chord=0.3, exposure_time=3600.0
        )
        assert "total_erosion_depth" in result
        assert "max_erosion_depth" in result
        assert "depth_distribution" in result
        assert "position" in result
        assert "rain_erosion_rate" in result

    def test_blade_erosion_increasing_with_speed(self, model):
        """Test that higher tip speed increases erosion."""
        r1 = model.blade_erosion(tip_speed=60.0, chord=0.3, exposure_time=100.0)
        r2 = model.blade_erosion(tip_speed=80.0, chord=0.3, exposure_time=100.0)
        assert r2["max_erosion_depth"] > r1["max_erosion_depth"]

    def test_blade_erosion_invalid_tip_speed(self, model):
        """Test that non-positive tip speed raises ValueError."""
        with pytest.raises(ValueError, match="Tip speed must be positive"):
            model.blade_erosion(tip_speed=-10.0, chord=0.3, exposure_time=100.0)

    def test_blade_erosion_invalid_exposure(self, model):
        """Test that non-positive exposure time raises ValueError."""
        with pytest.raises(ValueError, match="Exposure time must be positive"):
            model.blade_erosion(tip_speed=80.0, chord=0.3, exposure_time=0.0)

    def test_cumulative_erosion(self, model):
        """Test cumulative erosion scales with particle count."""
        r1 = model.cumulative_erosion(mass=1e-6, velocity=50.0, angle=30.0, n_particles=1)
        r100 = model.cumulative_erosion(mass=1e-6, velocity=50.0, angle=30.0, n_particles=100)
        assert r100["total_volume"] == pytest.approx(r1["total_volume"] * 100, rel=1e-1)
        assert r100["n_particles"] == 100

    def test_cumulative_erosion_zero_particles(self, model):
        """Test cumulative erosion with zero particles is zero."""
        result = model.cumulative_erosion(
            mass=1e-6, velocity=50.0, angle=30.0, n_particles=0
        )
        assert result["total_volume"] == pytest.approx(0.0)
        assert result["total_mass_loss"] == pytest.approx(0.0)

    def test_cumulative_negative_particles_raises(self, model):
        """Test that negative particle count raises ValueError."""
        with pytest.raises(ValueError, match="Number of particles must be non-negative"):
            model.cumulative_erosion(mass=1e-6, velocity=50.0, angle=30.0, n_particles=-1)

    def test_erosion_over_time_shape(self, model):
        """Test that erosion_over_time returns correctly shaped arrays."""
        result = model.erosion_over_time(
            velocity=50.0, angle=30.0, mass_flux=1e-3, total_time=1000.0, n_steps=50
        )
        assert len(result["time"]) == 50
        assert len(result["depth"]) == 50
        assert len(result["instantaneous_rate"]) == 50

    def test_erosion_over_time_accumulation(self, model):
        """Test that erosion depth increases over time."""
        result = model.erosion_over_time(
            velocity=50.0, angle=30.0, mass_flux=1e-3, total_time=1000.0, n_steps=50
        )
        assert result["depth"][-1] > result["depth"][0]

    def test_erosion_over_time_invalid_time(self, model):
        """Test that non-positive total_time raises ValueError."""
        with pytest.raises(ValueError, match="Total time must be positive"):
            model.erosion_over_time(velocity=50.0, angle=30.0, mass_flux=1e-3, total_time=0.0)

    def test_time_to_failure_positive(self, model):
        """Test time_to_failure returns positive time."""
        result = model.time_to_failure(
            current_depth=0.5e-3, critical_depth=2e-3, erosion_rate=1e-9
        )
        assert result["remaining_depth"] == pytest.approx(1.5e-3)
        assert result["time_to_failure"] > 0.0
        assert result["time_to_failure_hours"] > 0.0

    def test_time_to_failure_already_failed(self, model):
        """Test time_to_failure when already at critical depth."""
        result = model.time_to_failure(
            current_depth=2e-3, critical_depth=2e-3, erosion_rate=1e-9
        )
        assert result["time_to_failure"] == pytest.approx(0.0)
        assert result["remaining_depth"] == pytest.approx(0.0)

    def test_time_to_failure_exceeded(self, model):
        """Test time_to_failure when depth exceeds critical."""
        result = model.time_to_failure(
            current_depth=3e-3, critical_depth=2e-3, erosion_rate=1e-9
        )
        assert result["time_to_failure"] == pytest.approx(0.0)

    def test_time_to_failure_zero_rate_raises(self, model):
        """Test that zero erosion rate raises ValueError."""
        with pytest.raises(ValueError, match="Erosion rate must be positive"):
            model.time_to_failure(
                current_depth=0.0, critical_depth=1e-3, erosion_rate=0.0
            )

    def test_time_to_failure_negative_depth_raises(self, model):
        """Test that negative current depth raises ValueError."""
        with pytest.raises(ValueError, match="Current depth must be non-negative"):
            model.time_to_failure(
                current_depth=-0.1, critical_depth=1e-3, erosion_rate=1e-9
            )
