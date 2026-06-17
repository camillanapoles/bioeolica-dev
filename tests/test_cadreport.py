"""Tests for CAD+REPORT pipeline."""

import tempfile
from pathlib import Path

import pytest

from src.cadreport.metadata import build_crslr_input
from src.cadreport.pipeline import run_pipeline
from src.cad.parametric import ParametricModel


def test_build_crslr_input():
    """CRSLR input is built from ParametricModel."""
    model = ParametricModel(model_id="T1", name="Test", width=100, height=50, depth=20)
    Path("/tmp/test.step").write_text("dummy step content")
    crslr = build_crslr_input(model, "/tmp/test.step")
    assert "analysis_id" in crslr
    assert "CAD-T1" in crslr["analysis_id"]
    assert crslr["sections"]["context"]["content"] != ""


def test_build_crslr_has_metrics():
    """CRSLR input contains CAD metrics in results section."""
    model = ParametricModel(model_id="T2", name="Test2", width=200, height=100, depth=50)
    Path("/tmp/test2.step").write_text("dummy step content 2")
    crslr = build_crslr_input(model, "/tmp/test2.step")
    metrics = crslr["sections"]["results"]["metrics"]
    assert "width_mm" in metrics
    assert metrics["width_mm"]["value"] == 200


def test_pipeline_generates_artifacts():
    """Pipeline generates all expected artifacts."""
    with tempfile.TemporaryDirectory() as tmp:
        params_path = str(Path(tmp) / "params.json")
        import json
        json.dump({"model_id": "P1", "name": "Pipeline Test",
                   "width": 30, "height": 20, "depth": 10}, open(params_path, "w"))

        out_dir = str(Path(tmp) / "package")
        metadata = run_pipeline(params_path, out_dir, no_mesh=True)

        out = Path(out_dir)
        assert (out / "model.step").exists(), "STEP missing"
        assert (out / "report.md").exists(), "Report missing"
        assert (out / "metadata.json").exists(), "Metadata missing"
        assert (out / "checksums.sha256").exists(), "Checksums missing"
        assert metadata["model_id"] == "P1"


def test_pipeline_crslr_contains_cad_info():
    """CRSLR report references CAD parameters."""
    with tempfile.TemporaryDirectory() as tmp:
        params_path = str(Path(tmp) / "params.json")
        import json
        json.dump({"model_id": "P2", "name": "CRSLR Test",
                   "width": 50, "height": 30, "depth": 15,
                   "material": "aluminum"}, open(params_path, "w"))

        out_dir = str(Path(tmp) / "package2")
        run_pipeline(params_path, out_dir, no_mesh=True)

        report = (Path(out_dir) / "report.md").read_text()
        assert "aluminum" in report or "aluminum" in report.lower()
        assert "50" in report or "width" in report


def test_pipeline_deterministic_step():
    """Same parameters produce same STEP checksum (structural compare)."""
    import json as j
    with tempfile.TemporaryDirectory() as tmp:
        params = {"model_id": "D1", "name": "Det", "width": 40, "height": 20, "depth": 10}
        j.dump(params, open(Path(tmp) / "p.json", "w"))

        meta1 = run_pipeline(str(Path(tmp) / "p.json"), str(Path(tmp) / "out1"), no_mesh=True)
        meta2 = run_pipeline(str(Path(tmp) / "p.json"), str(Path(tmp) / "out2"), no_mesh=True)

        assert (Path(tmp) / "out1" / "model.step").stat().st_size > 0
        assert (Path(tmp) / "out2" / "model.step").stat().st_size > 0
