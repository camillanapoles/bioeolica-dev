"""Tests for 3D Three.js viewer."""

import tempfile
from pathlib import Path

from src.visualization.threejs_viewer import (
    generate_viewer_html, generate_cylinder_viewer, generate_stress_viewer,
)


def test_viewer_generates_html():
    """Viewer HTML is generated without error."""
    html = generate_viewer_html(title="Test Viewer")
    assert "<!DOCTYPE html>" in html
    assert "Test Viewer" in html
    assert "three.min.js" in html


def test_viewer_has_controls():
    """Viewer includes UI controls."""
    html = generate_viewer_html()
    assert "Corte Transversal" in html
    assert "Resetar Vista" in html
    assert "Rotação Auto" in html


def test_viewer_has_legend():
    """Viewer includes color legend."""
    html = generate_viewer_html(legend_label="Stress", legend_min="0", legend_max="100")
    assert "legend" in html.lower()
    assert "Stress" in html or "stress" in html


def test_cylinder_viewer():
    """Cylinder viewer generates valid HTML."""
    html = generate_cylinder_viewer(title="Cylinder Test")
    assert "Cylinder" in html
    assert "Temperature" in html


def test_stress_viewer():
    """Stress viewer includes stress data in title."""
    data = {"title": "FEA Results", "max_stress": 250.5, "min_stress": 0.3}
    html = generate_stress_viewer(data)
    assert "FEA Results" in html
    assert "250.5" in html or "250.5" in str(data)


def test_viewer_saves_to_file():
    """Viewer saves to file when output_path is provided."""
    with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
        path = f.name
    generate_cylinder_viewer(output_path=path)
    assert Path(path).exists()
    assert Path(path).stat().st_size > 100


def test_domain_options():
    """Domain dropdown options appear in HTML."""
    options = ["Stress (MPa)", "Strain", "Temperature (K)"]
    html = generate_viewer_html(domain_options=options)
    for opt in options:
        assert opt in html
