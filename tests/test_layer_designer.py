import pytest
import numpy as np
from ai_assist_cad.layer_designer import LayerPattern, CompositeStack


def test_layer_pattern_creation():
    pattern = LayerPattern(
        materials=[{"name": "aluminum", "E_GPa": 70, "fraction": 0.97},
                   {"name": "graphite", "E_GPa": 10, "fraction": 0.03}],
        binder="epoxy resin",
        thickness_mm=2.0,
    )
    assert pattern.thickness_mm == 2.0
    assert len(pattern.materials) == 2
    assert abs(sum(m["fraction"] for m in pattern.materials) - 1.0) < 0.01


def test_composite_stack_homogenization():
    pattern = LayerPattern(
        materials=[{"name": "aluminum", "E_GPa": 70, "nu": 0.33, "fraction": 1.0}],
        thickness_mm=2.0,
    )
    stack = CompositeStack(layer_pattern=pattern, repetitions=3)
    props = stack.effective_properties
    assert abs(props["E1_GPa"] - 70.0) < 0.1
    assert abs(props["total_thickness_mm"] - 6.0) < 0.1
    assert props["repetitions"] == 3


def test_multi_material_homogenization():
    pattern = LayerPattern(
        materials=[{"name": "steel", "E_GPa": 200, "nu": 0.29, "fraction": 0.6, "density": 7800},
                   {"name": "aluminum", "E_GPa": 70, "nu": 0.33, "fraction": 0.4, "density": 2700}],
        thickness_mm=3.0,
    )
    stack = CompositeStack(layer_pattern=pattern, repetitions=2)
    props = stack.effective_properties
    assert 100 < props["E1_GPa"] < 180  # Voigt mixed: 200*0.6 + 70*0.4 = 148
    assert abs(props["total_thickness_mm"] - 6.0) < 0.1
    assert 5000 < props["density_kgm3"] < 6000  # 7800*0.6 + 2700*0.4 = 5760


def test_process_params():
    pattern = LayerPattern(
        materials=[{"name": "steel", "E_GPa": 200, "fraction": 0.8},
                   {"name": "nickel", "E_GPa": 207, "fraction": 0.2}],
        process="shot_blasting",
        process_params={"pressure_bar": 6, "duration_min": 15},
    )
    assert pattern.process == "shot_blasting"
    assert pattern.process_params["pressure_bar"] == 6


def test_save_load(tmp_path):
    pattern = LayerPattern(materials=[{"name": "steel", "E_GPa": 200, "fraction": 1.0}], thickness_mm=5.0)
    path = tmp_path / "test_pattern.json"
    pattern.save(str(path))
    loaded = LayerPattern.load(str(path))
    assert loaded.thickness_mm == 5.0
    assert loaded.materials[0]["name"] == "steel"
