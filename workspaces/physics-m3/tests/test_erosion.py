import numpy as np; import pytest
from modules.erosion import ErosionModel

def test_init():
    e = ErosionModel(material_density=2700, hardness=3e9)
    assert e is not None

def test_finnie_returns_dict():
    e = ErosionModel(material_density=2700, hardness=3e9)
    result = e.finnie_erosion(mass=1e-6, velocity=50, angle=30)
    assert isinstance(result, dict)

def test_blade_erosion():
    e = ErosionModel(material_density=2700, hardness=3e9)
    r = e.blade_erosion(tip_speed=80, chord=0.3, particle_mass=1e-6)
    assert isinstance(r, dict)

def test_cumulative_erosion():
    e = ErosionModel(material_density=2700, hardness=3e9)
    r = e.cumulative_erosion(mass=1e-6, velocity=50, angle=30, n_particles=100)
    assert isinstance(r, dict)
