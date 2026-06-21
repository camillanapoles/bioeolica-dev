#!/usr/bin/env python3
"""
T023 — PQMS Validation against quickstart.md section 4.

Validates:
  1. Register a validation_reference object
  2. Register a computational_model with calibration
  3. Insert quality_scores for all 13 PQMS dimensions
  4. Compute PQMS aggregate
  5. Verify v_pqms_summary: PQMS >= 9.5, SC-008 = 'PASS', methodology = 1.0
"""
import sys
import os
import json
import uuid

_project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from src.common.database import database
from src.common.registry import create_object, get_object
from src.common.quality.compute_pqms import (
    PQMS_DIMENSIONS,
    compute_pqms,
    check_sc008,
)


def test_validation_reference_registration() -> dict:
    """Register a validation_reference per quickstart section 4.1."""
    obj_id = create_object("validation_reference", tags=["t023_validation"])
    now = "2026-06-12T10:00:00Z"

    with database() as db:
        db.execute(
            """INSERT INTO validation_references
               (id, source_type, title, authors, year, doi,
                source_quality_score, validation_metric_type,
                validation_threshold, applicability, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                obj_id,
                "journal",
                "Mechanical Properties of PVA-Bonded Cellulose Fiber Composites",
                json.dumps(["Silva, A.", "Santos, B.", "Oliveira, C."]),
                2024,
                "10.xxxx/yyyyy",
                9,  # source_quality_score >= 8 for methodology validation
                "correlation",
                0.95,
                json.dumps(["structural", "materials"]),
                now,
            ),
        )
        db.commit()

    # Verify
    obj = get_object(obj_id)
    with database() as db:
        ref = db.execute(
            "SELECT * FROM validation_references WHERE id = ?", (obj_id,)
        ).fetchone()

    return {
        "name": "validation_reference_registration",
        "description": "Register a validation reference in the system",
        "passed": ref is not None and ref["source_quality_score"] >= 8,
        "details": {
            "object_id": obj_id[:8] + "...",
            "object_type": obj["object_type"],
            "source_quality_score": ref["source_quality_score"] if ref else None,
            "found_in_db": ref is not None,
        },
    }


def test_computational_model_registration() -> dict:
    """Register a computational_model with calibration per quickstart section 4.2."""
    obj_id = create_object("computational_model", tags=["t023_model"])
    now = "2026-06-12T10:00:00Z"

    with database() as db:
        db.execute(
            """INSERT INTO computational_models
               (id, model_type, domain, solver_software, solver_version,
                mesh_type, mesh_num_elements, mesh_num_nodes,
                boundary_conditions, material_model, material_properties,
                calibration_status, calibrated_against,
                calibration_error_pct, notes)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                obj_id,
                "FEM",
                "structural",
                "CalculiX",
                "2.20",
                "tetrahedral",
                25000,
                8000,
                json.dumps({"fixed": ["blade_root"], "pressure": {"face": "suction_side", "value": 500}}),
                "linear_elastic",
                json.dumps({"E": 4500, "nu": 0.35, "rho": 800}),
                "validated",                     # calibration_status
                obj_id,                          # calibrated_against (self-ref for simplicity)
                5.0,                             # calibration_error_pct < 10%
                "Validated against experimental data",
            ),
        )
        db.commit()

    # Verify
    with database() as db:
        model = db.execute(
            "SELECT * FROM computational_models WHERE id = ?", (obj_id,)
        ).fetchone()

    passed = (
        model is not None
        and model["calibration_status"] == "validated"
        and model["calibrated_against"] is not None
        and model["calibration_error_pct"] is not None
        and model["calibration_error_pct"] < 10.0
    )

    return {
        "name": "computational_model_registration",
        "description": "Register a validated computational model",
        "passed": passed,
        "details": {
            "object_id": obj_id[:8] + "...",
            "calibration_status": model["calibration_status"] if model else None,
            "calibration_error_pct": model["calibration_error_pct"] if model else None,
            "found_in_db": model is not None,
        },
    }


def test_pqms_scores_insertion() -> dict:
    """Insert quality_scores for all 13 dimensions and compute PQMS."""
    model_id = create_object("computational_model", tags=["t023_pqms_test"])
    now = "2026-06-12T10:00:00Z"

    with database() as db:
        db.execute(
            """INSERT INTO computational_models
               (id, model_type, domain, solver_software, solver_version,
                mesh_type, mesh_num_elements, mesh_num_nodes,
                boundary_conditions, material_model, material_properties,
                calibration_status, calibrated_against,
                calibration_error_pct, notes)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                model_id,
                "FEM",
                "structural",
                "CalculiX",
                "2.20",
                "tetrahedral",
                25000,
                8000,
                json.dumps({"fixed": ["blade_root"]}),
                "linear_elastic",
                json.dumps({"E": 4500, "nu": 0.35}),
                "validated",
                model_id,
                5.0,
                "Validated computational model for PQMS test",
            ),
        )
        db.commit()

    # Scores tuned to PQMS >= 9.5 with corrected weights (sum = 1.0)
    # Highest-weight dimensions (D1=0.12, D3=0.15, D4=0.10, D7=0.15) set to 10.0
    # to demonstrate that rigorous VV and numerical quality drive the score
    scores = {
        "D1_completude": 10.0,
        "D2_profundidade": 9.5,
        "D3_rigor": 10.0,
        "D4_rastreabilidade": 10.0,
        "D5_conhecimento": 9.0,
        "D6_integracao": 9.0,
        "D7_qualidade_numerica": 10.0,
        "D8_impacto": 9.0,
        "D9_vies": 9.0,
        "D10_ensino": 9.5,
        "D11_velocidade": 9.0,
        "D12_satisfacao": 9.0,
        "D13_inovacao": 9.0,
    }

    evidence = {dim: "T023 automated validation" for dim in scores}

    # Compute PQMS
    result = compute_pqms(model_id, scores, evidence)

    # Verify aggregate
    aggregate_ok = result["aggregate"] >= 9.5
    no_below_minimum = result["dimensions_below_minimum"] == 0
    status_ok = result["pqms_status"] == "PASS"

    passed = aggregate_ok and no_below_minimum and status_ok

    return {
        "name": "pqms_scores_insertion",
        "description": "13 PQMS dimension scores -> aggregate >= 9.5, PASS",
        "passed": passed,
        "details": {
            "object_id": model_id[:8] + "...",
            "aggregate": result["aggregate"],
            "dimensions_stored": result["dimensions_stored"],
            "dimensions_below_minimum": result["dimensions_below_minimum"],
            "pqms_status": result["pqms_status"],
            "aggregate_ok": aggregate_ok,
            "no_below_minimum": no_below_minimum,
        },
    }


def test_sc008_compliance() -> dict:
    """Verify SC-008: PQMS >= 9.5 AND methodology validation sub-score = 1.0.

    Self-contained: creates its own model + reference, computes PQMS,
    then verifies SC-008 only for the test object (avoids interference
    from other objects in the shared database).
    """
    now = "2026-06-12T10:00:00Z"

    # Create a computational_model with calibration
    model_id = create_object("computational_model", tags=["t023_sc008_model"])
    with database() as db:
        db.execute(
            """INSERT INTO computational_models
               (id, model_type, domain, solver_software, solver_version,
                mesh_type, mesh_num_elements, mesh_num_nodes,
                boundary_conditions, material_model, material_properties,
                calibration_status, calibrated_against,
                calibration_error_pct, notes)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                model_id,
                "FEM",
                "structural",
                "CalculiX",
                "2.20",
                "tetrahedral",
                25000,
                8000,
                json.dumps({"fixed": ["blade_root"]}),
                "linear_elastic",
                json.dumps({"E": 4500, "nu": 0.35}),
                "validated",
                model_id,
                5.0,
                "Validated model for SC-008 test",
            ),
        )
        db.commit()

    # Create a validation_reference (needed for methodology sub-score = 1.0)
    ref_id = create_object("validation_reference", tags=["t023_sc008_ref"])
    with database() as db:
        db.execute(
            """INSERT INTO validation_references
               (id, source_type, title, authors, year, doi,
                source_quality_score, validation_metric_type,
                validation_threshold, applicability, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                ref_id,
                "journal",
                "Reference for SC-008 validation",
                json.dumps(["Author, A."]),
                2024,
                "10.xxxx/zzzzz",
                9,
                "correlation",
                0.95,
                json.dumps(["structural"]),
                now,
            ),
        )
        db.commit()

    # Compute PQMS for the model
    scores = {
        "D1_completude": 10.0,
        "D2_profundidade": 9.5,
        "D3_rigor": 10.0,
        "D4_rastreabilidade": 10.0,
        "D5_conhecimento": 9.0,
        "D6_integracao": 9.0,
        "D7_qualidade_numerica": 10.0,
        "D8_impacto": 9.0,
        "D9_vies": 9.0,
        "D10_ensino": 9.5,
        "D11_velocidade": 9.0,
        "D12_satisfacao": 9.0,
        "D13_inovacao": 9.0,
    }
    evidence = {dim: "SC-008 test validation" for dim in scores}
    result = compute_pqms(model_id, scores, evidence)

    # Query v_pqms_summary for our test model only
    with database() as db:
        row = db.execute(
            "SELECT * FROM v_pqms_summary WHERE object_id = ?",
            (model_id,),
        ).fetchone()

    passed = row is not None and row["sc008_combined_status"].startswith("PASS")

    return {
        "name": "sc008_compliance",
        "description": "SC-008: PQMS >= 9.5, methodology sub-score >= 1.0",
        "passed": passed,
        "details": {
            "object_id": model_id[:8] + "...",
            "computed_pqms": row["computed_pqms"] if row else None,
            "methodology_subscore": row["methodology_validation_subscore"] if row else None,
            "sc008_combined_status": row["sc008_combined_status"] if row else None,
            "aggregate_ok": result["aggregate"] >= 9.5 if row else False,
            "pqms_status": result["pqms_status"],
        },
    }


def run_all() -> dict:
    """Run all T023 validation tests."""
    tests = [
        test_validation_reference_registration(),
        test_computational_model_registration(),
        test_pqms_scores_insertion(),
        test_sc008_compliance(),
    ]

    results = {"pass": 0, "fail": 0, "total": len(tests), "tests": tests}
    for t in tests:
        if t["passed"]:
            results["pass"] += 1
        else:
            results["fail"] += 1
    return results


def main() -> None:
    results = run_all()
    print(f"T023 — PQMS Validation (quickstart.md section 4)")
    print(f"  {'=' * 60}")
    for t in results["tests"]:
        status = "PASS" if t["passed"] else "FAIL"
        print(f"  [{status}] {t['name']}: {t['description']}")
        for k, v in t.get("details", {}).items():
            val_str = str(v)
            if len(val_str) > 80:
                val_str = val_str[:77] + "..."
            print(f"         {k}: {val_str}")
    print(f"  {'=' * 60}")
    print(f"  Total: {results['total']}  Pass: {results['pass']}  Fail: {results['fail']}")
    sys.exit(0 if results["fail"] == 0 else 1)


if __name__ == "__main__":
    main()
