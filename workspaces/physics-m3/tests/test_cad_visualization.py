"""Tests for the cad_visualization module."""

import matplotlib
matplotlib.use("Agg")

import numpy as np
import pytest
from modules.cad_visualization import (
    AirfoilCoordinates, BladeGeometry, StressField, HeatMap3D,
    M3Visualizer, FailureEnvelope, WindRose, LaminateView,
    stress_color_map, geometry_to_stl,
)


def test_airfoil():
    a = AirfoilCoordinates(chord=1.0, n_points=20)
    assert len(a.x_upper) == 20
    assert len(a.x_lower) == 20


def test_blade_init():
    b = BladeGeometry(chord=0.5, twist_deg=5)
    assert b.chord == 0.5


def test_stress_color():
    c = stress_color_map(100, 250)
    assert isinstance(c, str) and c.startswith("#")


def test_stress_field_init():
    sf = StressField()
    assert sf is not None


def test_heatmap3d_init():
    hm = HeatMap3D()
    assert hm is not None


def test_m3_viz_init():
    viz = M3Visualizer()
    assert viz is not None


def test_failure_envelope():
    fe = FailureEnvelope()
    assert fe is not None


def test_windrose():
    wr = WindRose()
    assert wr is not None


def test_laminate():
    lv = LaminateView()
    assert lv is not None


def test_geometry_to_stl():
    verts = np.array([[0,0,0],[1,0,0],[0,1,0],[0,0,1]], dtype=float)
    faces = np.array([[0,1,2],[0,1,3]], dtype=int)
    stl = geometry_to_stl(verts, faces)
    assert stl is not None
