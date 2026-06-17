"""Tests for CRSLR report engine."""

import json
from pathlib import Path

import pytest

from src.crslr.engine import create_report, render_report, add_uncertainty, add_m9_compliance
from src.crslr.schema import load_and_validate, make_sample, VALID_SECTIONS

FIXTURES = Path(__file__).parent / "fixtures"


def test_schema_loads_sample():
    """Sample JSON loads and validates."""
    result = load_and_validate(str(FIXTURES / "sample_results.json"))
    assert result.analysis_id == "ANL-001"
    assert len(result.sections) == 5
    assert result.vvv_status == "PASS"


def test_schema_make_sample():
    """make_sample() produces valid result."""
    result = make_sample()
    assert result.analysis_id == "ANL-001"
    assert result.vvv_status == "PASS"


def test_engine_creates_markdown():
    """Engine generates markdown with all 5 CRSLR sections."""
    result = load_and_validate(str(FIXTURES / "sample_results.json"))
    data = result.__dict__.copy()
    data = add_uncertainty(data)
    data = add_m9_compliance(data)
    md = create_report(data, format="markdown")
    for section in VALID_SECTIONS:
        assert section.title() in md or section.capitalize() in md


def test_engine_creates_html():
    """Engine generates HTML with proper structure."""
    result = load_and_validate(str(FIXTURES / "sample_results.json"))
    data = result.__dict__.copy()
    data = add_uncertainty(data)
    data = add_m9_compliance(data)
    html = create_report(data, format="html")
    assert "<!DOCTYPE html>" in html
    assert "<table>" in html or "<h2>" in html


def test_engine_has_all_sections():
    """Generated report contains all 5 required CRSLR sections."""
    result = load_and_validate(str(FIXTURES / "sample_results.json"))
    data = result.__dict__.copy()
    data = add_uncertainty(data)
    data = add_m9_compliance(data)
    md = create_report(data, format="markdown")
    for section in ["Context", "Results", "Synthesis", "Limitations", "Recommendations"]:
        assert section in md, f"Missing section: {section}"


def test_engine_has_uncertainty():
    """Uncertainty is quantified in generated report."""
    result = load_and_validate(str(FIXTURES / "sample_results.json"))
    data = result.__dict__.copy()
    data = add_uncertainty(data)
    assert any("±" in str(v.get("display", "")) for v in data["sections"]["results"]["metrics"].values())


def test_engine_has_vvv_badge():
    """VVV status badge is rendered."""
    result = load_and_validate(str(FIXTURES / "sample_results.json"))
    data = result.__dict__.copy()
    data = add_uncertainty(data)
    data = add_m9_compliance(data)
    md = create_report(data, format="markdown")
    assert "PASS" in md
    assert "VVV" in md or "Status" in md


def test_engine_has_m9_compliance():
    """M9 compliance data is included."""
    result = load_and_validate(str(FIXTURES / "sample_results.json"))
    data = result.__dict__.copy()
    data = add_m9_compliance(data)
    assert "m9_compliance" in data
    assert "map_index" in data["m9_compliance"]


def test_render_report_pipeline():
    """Full pipeline generates output file."""
    out_path = "/tmp/test_crslr_report.md"
    path = render_report(str(FIXTURES / "sample_results.json"), out_path)
    assert Path(path).exists()
    content = Path(path).read_text()
    assert len(content) > 100


def test_invalid_vvv_status_fails():
    """Invalid vvv_status raises validation error."""
    data = {
        "analysis_id": "TEST",
        "sections": {"context": {"content": "test", "priority": 1}},
        "vvv_status": "INVALID",
    }
    import json, tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(data, f)
        p = f.name
    with pytest.raises(ValueError, match="vvv_status"):
        load_and_validate(p)


def test_missing_section_fails():
    """Missing required sections are detected."""
    data = {
        "analysis_id": "TEST",
        "sections": {"unknown_section": {"content": "test", "priority": 1}},
    }
    import json, tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(data, f)
        p = f.name
    with pytest.raises(ValueError, match="unknown_section"):
        load_and_validate(p)
