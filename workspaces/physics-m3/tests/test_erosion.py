import numpy as np; import pytest
from modules.erosion import ErosionModel

def test_init():
    e = ErosionModel(material_density=2700, hardness=3e9)
    assert e is not None

def test_finnie():
    e = ErosionModel(material_density=2700, hardness=3e9)
    r = e.finnie_erosion(mass=1e-6, velocity=50, angle=30)
    assert isinstance(r, dict)

def test_blade():
    e = ErosionModel(material_density=2700, hardness=3e9)
    r = e.blade_erosion(tip_speed=80, chord=0.3)
    assert isinstance(r, dict)

def test_cumulative():
    e = ErosionModel(material_density=2700, hardness=3e9)
    r = e.cumulative_erosion(mass=1e-6, velocity=50, angle=30, n_particles=100)
    assert isinstance(r, dict)
