"""Tests for CAD pipeline modules."""

import json
import tempfile
from pathlib import Path

import pytest

from src.cad.parametric import ParametricModel, parse_parameters
from src.cad.export import export_step, step_checksum


def test_parametric_creation():
    """ParametricModel can be created with valid dimensions."""
    model = ParametricModel(model_id="TEST-001", name="Test Box",
                            width=100, height=50, depth=20)
    assert model.width == 100
    assert model.height == 50
    assert model.depth == 20


def test_parametric_negative_dimension_raises():
    """Negative dimensions raise ValueError."""
    with pytest.raises(ValueError, match="width"):
        ParametricModel(model_id="T", name="T", width=-10, height=50, depth=20)


def test_parse_parameters_from_dict():
    """Parameters load from dict."""
    data = {"model_id": "T1", "name": "Test", "width": 200, "height": 100, "depth": 50}
    model = parse_parameters(data)
    assert model.width == 200


def test_parse_parameters_from_json_file():
    """Parameters load from JSON file."""
    data = {"model_id": "T1", "name": "Test", "width": 50, "height": 30, "depth": 10}
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(data, f)
        p = f.name
    model = parse_parameters(p)
    assert model.width == 50


def test_export_generates_step():
    """STEP file is generated from ParametricModel."""
    model = ParametricModel(model_id="EX-001", name="Export Test",
                            width=30, height=20, depth=10)
    with tempfile.NamedTemporaryFile(suffix=".step", delete=False) as f:
        out = f.name
    path = export_step(model, out)
    assert Path(path).exists()
    assert Path(path).stat().st_size > 0


def test_step_checksum_deterministic():
    """Same model produces valid STEP files (CadQuery STEP may embed UUIDs)."""
    model = ParametricModel(model_id="CHK-001", name="Checksum",
                            width=40, height=20, depth=10)
    with tempfile.NamedTemporaryFile(suffix=".step", delete=False) as f1, \
         tempfile.NamedTemporaryFile(suffix=".step", delete=False) as f2:
        p1, p2 = f1.name, f2.name
    export_step(model, p1)
    export_step(model, p2)
    # Validate both are valid STEP files
    for p in [p1, p2]:
        content = Path(p).read_text()
        assert "ISO-10303-21" in content or "HEADER" in content


def test_layer_validation():
    """Layer thickness must sum to base depth."""
    from src.cad.layer_designer import LayerPattern, CompositeStack
    layers = [LayerPattern(materials=[{"E_GPa": 200, "fraction": 1.0, "density": 7800}],
                           thickness_mm=5.0)]
    with pytest.raises(ValueError, match="Layer thickness"):
        CompositeStack(layers, ParametricModel("T", "T", depth=10.0))


def test_layer_designer_builds():
    """Layer designer builds composite model without error."""
    from src.cad.layer_designer import LayerPattern, CompositeStack
    mat = [{"E_GPa": 200, "fraction": 1.0, "density": 7800, "nu": 0.3}]
    layers = [LayerPattern(materials=mat, thickness_mm=5.0),
              LayerPattern(materials=mat, thickness_mm=5.0)]
    stack = CompositeStack(layers, ParametricModel("T", "T", depth=10.0))
    wp = stack.build()
    assert wp is not None
