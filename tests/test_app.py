"""tests/test_app.py"""
import pytest
from pathlib import Path


def test_viewer_template_exists():
    path = Path(__file__).parent.parent / "ai_assist_cad" / "viewer_template.html"
    assert path.exists(), f"Viewer template not found at {path}"
    assert path.stat().st_size > 500, "Viewer template too small"


def test_app_imports():
    from ai_assist_cad.app import check_outputs
    result = check_outputs()
    assert isinstance(result, dict)
    assert "has_nlp_input" in result
    assert "has_certify" in result


def test_html_has_threejs():
    path = Path(__file__).parent.parent / "ai_assist_cad" / "viewer_template.html"
    content = path.read_text(encoding="utf-8")
    assert "three.min.js" in content or "three.js" in content
    assert "renderer" in content
    assert "scene" in content


def test_html_has_controls():
    path = Path(__file__).parent.parent / "ai_assist_cad" / "viewer_template.html"
    content = path.read_text(encoding="utf-8")
    assert "toggleCut" in content or "Corte" in content
    assert "domainSelect" in content
