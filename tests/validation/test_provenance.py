#!/usr/bin/env python3
"""
Provenance Audit Verification Script — Composite Biomaterial for Wind Energy.

Tests the provenance tracking system:
  1. Basic edge recording between two objects
  2. Upstream and downstream tracing
  3. Cycle detection (should reject cycles)
  4. Full provenance chain retrieval
  5. Orphan detection
  6. v_provenance_audit view (SC-007)
  7. v_provenance_coverage view
"""
import sys
import os

_project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from src.common.database import database
from src.common.registry import create_object
from src.common.provenance import (
    record_edge,
    get_upstream,
    get_downstream,
    get_chain,
    verify_acyclic,
    verify_orphans,
    ProvenanceError,
)
from src.common.registry import ObjectNotFound


def test_basic_edge_recording() -> dict:
    """Test: record a basic provenance edge and verify it exists."""
    source = create_object("specimen", tags=["test_source"])
    target = create_object("test_result", tags=["test_target"])

    edge_id = record_edge(source, target, "mechanical_test",
                          {"standard": "ASTM D638"})

    # Verify by checking upstream
    up = get_upstream(target)
    down = get_downstream(source)

    result = {
        "name": "basic_edge_recording",
        "description": "Record edge and verify upstream/downstream",
        "passed": False,
        "details": {},
    }

    up_ids = [e["source_id"] for e in up]
    down_ids = [e["target_id"] for e in down]

    result["passed"] = (source in up_ids) and (target in down_ids)
    result["details"] = {
        "edge_id": edge_id,
        "source": source[:8],
        "target": target[:8],
        "upstream_found": source in up_ids,
        "downstream_found": target in down_ids,
    }
    return result


def test_cycle_rejection() -> dict:
    """Test: cycle creation should be rejected."""
    a = create_object("specimen", tags=["cycle_a"])
    b = create_object("test_result", tags=["cycle_b"])

    # Create A → B
    record_edge(a, b, "step_1")

    # Create B → A should fail (2-node cycle)
    try:
        record_edge(b, a, "step_2")
        cycle_rejected = False
    except ProvenanceError:
        cycle_rejected = True

    result = {
        "name": "cycle_rejection",
        "description": "2-node cycle should be rejected",
        "passed": cycle_rejected,
        "details": {"cycle_rejected": cycle_rejected},
    }
    return result


def test_provenance_chain() -> dict:
    """Test: 3-node linear chain."""
    a = create_object("specimen", tags=["chain_a"])
    b = create_object("test_result", tags=["chain_b"])
    c = create_object("simulation_result", tags=["chain_c"])

    record_edge(a, b, "test")
    record_edge(b, c, "simulate")

    chain = get_chain(b)
    up = get_upstream(b)
    down = get_downstream(b)

    up_sources = {e["source_id"] for e in up}
    down_targets = {e["target_id"] for e in down}

    passed = (a in up_sources) and (c in down_targets)

    result = {
        "name": "provenance_chain",
        "description": "3-node chain has correct upstream/downstream",
        "passed": passed,
        "details": {
            "upstream_count": chain["upstream_count"],
            "downstream_count": chain["downstream_count"],
            "a_in_upstream": a in up_sources,
            "c_in_downstream": c in down_targets,
        },
    }
    return result


def test_verify_acyclic() -> dict:
    """Test: verify_acyclic() on known acyclic DAG."""
    result = verify_acyclic()
    return {
        "name": "verify_acyclic",
        "description": "verify_acyclic() on clean DAG returns ok=True",
        "passed": result["ok"],
        "details": {"total_edges": result["total_edges"], "cycles": len(result["cycles"])},
    }


def test_verify_orphans() -> dict:
    """Test: verify_orphans() — all edges should reference existing objects."""
    result = verify_orphans()
    return {
        "name": "verify_orphans",
        "description": "verify_orphans() returns ok=True on clean data",
        "passed": result["ok"],
        "details": {"orphan_count": len(result["orphans"])},
    }


def test_provenance_audit_view() -> dict:
    """Test: v_provenance_audit view correctly classifies objects."""
    # Create objects with known provenance states — self-contained test
    specimen = create_object("specimen", tags=["audit_test_edge"])
    test_result = create_object("test_result", tags=["audit_test_edge"])
    orphan_obj = create_object("specimen", tags=["audit_test_orphan"])
    community = create_object("community_profile", tags=["audit_test_root"])

    # Record one edge: specimen → test_result
    record_edge(specimen, test_result, "test", {"standard": "ASTM D638"})

    # Query the view for our test objects only
    with database() as db:
        rows = db.execute(
            """SELECT object_id, object_type, provenance_audit_status
               FROM v_provenance_audit
               WHERE object_id IN (?, ?, ?, ?)""",
            (specimen, test_result, orphan_obj, community),
        ).fetchall()

    results = {r["object_id"]: dict(r) for r in rows}

    # Check each classification
    spec_status = results.get(specimen, {}).get("provenance_audit_status", "MISSING")
    result_status = results.get(test_result, {}).get("provenance_audit_status", "MISSING")
    orphan_status = results.get(orphan_obj, {}).get("provenance_audit_status", "MISSING")
    root_status = results.get(community, {}).get("provenance_audit_status", "MISSING")

    spec_ok = spec_status.startswith("PASS")
    result_ok = result_status.startswith("PASS")
    orphan_fail = orphan_status.startswith("FAIL")
    root_ok = "root node" in root_status

    passed = spec_ok and result_ok and orphan_fail and root_ok

    return {
        "name": "provenance_audit_view",
        "description": "SC-007 provenance audit view classifies objects correctly",
        "passed": passed,
        "details": {
            "specimen_with_edge": spec_status,
            "specimen_ok": spec_ok,
            "test_result_with_edge": result_status,
            "test_result_ok": result_ok,
            "orphan_no_edges": orphan_status,
            "orphan_flagged_fail": orphan_fail,
            "community_profile_root": root_status,
            "root_node_exception": root_ok,
        },
    }


def test_object_not_found() -> dict:
    """Test: record_edge with non-existent object raises error."""
    fake_id = "00000000-0000-0000-0000-000000000000"
    real = create_object("specimen", tags=["not_found_test"])

    try:
        record_edge(fake_id, real, "test")
        source_check = False
    except ObjectNotFound:
        source_check = True

    try:
        record_edge(real, fake_id, "test")
        target_check = False
    except ObjectNotFound:
        target_check = True

    result = {
        "name": "object_not_found",
        "description": "record_edge with non-existent object raises ObjectNotFound",
        "passed": source_check and target_check,
        "details": {
            "missing_source_raises": source_check,
            "missing_target_raises": target_check,
        },
    }
    return result


def run_all() -> dict:
    """Run all provenance tests."""
    tests = [
        test_basic_edge_recording(),
        test_cycle_rejection(),
        test_provenance_chain(),
        test_verify_acyclic(),
        test_verify_orphans(),
        test_provenance_audit_view(),
        test_object_not_found(),
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
    print(f"Provenance Audit Verification")
    print(f"  {'=' * 60}")
    for t in results["tests"]:
        status = "PASS" if t["passed"] else "FAIL"
        print(f"  [{status}] {t['name']}: {t['description']}")
        for k, v in t.get("details", {}).items():
            print(f"         {k}: {v}")
    print(f"  {'=' * 60}")
    print(f"  Total: {results['total']}  Pass: {results['pass']}  Fail: {results['fail']}")
    sys.exit(0 if results["fail"] == 0 else 1)


if __name__ == "__main__":
    main()
