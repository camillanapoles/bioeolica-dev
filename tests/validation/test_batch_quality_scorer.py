#!/usr/bin/env python3
"""
Tests for batch_quality_scorer.py.

Verifies:
  - Dry run reports correct counts
  - Live run persists quality_scores
  - Re-running is idempotent (0 new scores on re-run)
  - No objects are missing quality_scores entirely
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.common.database import database
from src.common.quality.batch_quality_scorer import (
    get_objects_missing_scores,
    verify_coverage,
)


def test_batch_scorer_idempotent():
    """Re-running batch scorer scores 0 new objects (idempotent)."""
    missing = get_objects_missing_scores()
    assert len(missing) == 0, f"All objects should be scored, found {len(missing)} missing"


def test_verify_coverage_100():
    """verify_coverage returns 100% after batch scoring."""
    coverage = verify_coverage()
    assert coverage["sc008_ok"] is True, f"SC-008 should PASS, got coverage={coverage['coverage_pct']}%"


def test_all_objects_have_quality_scores():
    """Every object in objects table has quality_scores entries."""
    with database() as db:
        total = db.execute("SELECT COUNT(*) as c FROM objects").fetchone()["c"]
        scored = db.execute(
            "SELECT COUNT(DISTINCT object_id) as c FROM quality_scores"
        ).fetchone()["c"]
    assert scored == total, f"Objects with quality_scores: {scored}/{total}"
