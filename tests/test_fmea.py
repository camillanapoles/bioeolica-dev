"""Tests for FMEA safety module."""

import pytest
from src.common.safety.fmea import (
    FailureMode, FMEAResult, SafetyLevel, Severity, Occurrence, Detection,
    classify_safety_level,
)


def test_fmea_creation():
    """FailureMode can be created with valid parameters."""
    fm = FailureMode(
        component="shaft",
        failure_mode="fatigue_crack",
        cause="cyclic_bending",
        effect="catastrophic_break",
        severity=Severity.FATAL,
        occurrence=Occurrence.LOW,
        detection=Detection.MODERATE,
    )
    assert fm.component == "shaft"


def test_rpn_calculation():
    """RPN = S × O × D."""
    fm = FailureMode("shaft", "crack", "load", "break",
                      severity=Severity.MAJOR, occurrence=Occurrence.FREQUENT,
                      detection=Detection.LIKELY)
    assert fm.rpn == 5 * 4 * 4 == 80


def test_safety_level_critical():
    """Severity >= 7 → S1_CRITICAL."""
    fm = FailureMode("blade", "detach", "fatigue", "rotor_imbalance",
                      severity=Severity.FATAL, occurrence=Occurrence.LOW,
                      detection=Detection.LIKELY)
    assert fm.safety_level == SafetyLevel.S1_CRITICAL


def test_safety_level_relevant():
    """Severity 3-6 → S2_RELEVANT."""
    fm = FailureMode("bearing", "overheat", "wear", "noise",
                      severity=Severity.MODERATE, occurrence=Occurrence.MODERATE,
                      detection=Detection.ALWAYS_CAUGHT)
    assert fm.safety_level == SafetyLevel.S2_RELEVANT


def test_redesign_required():
    """RPN > 200 requires redesign."""
    fm = FailureMode("rotor", "burst", "overspeed", "containment_breach",
                      severity=Severity.FATAL, occurrence=Occurrence.REPEATED,
                      detection=Detection.VERY_HARD)
    assert fm.requires_redesign
    assert fm.rpn == 10 * 6 * 8 == 480


def test_fmea_result():
    """FMEAResult aggregates failures correctly."""
    result = FMEAResult("wind_turbine")
    result.add(FailureMode("blade", "crack", "fatigue", "failure",
                            severity=Severity.CRITICAL, occurrence=Occurrence.LOW,
                            detection=Detection.MODERATE))
    assert len(result.top_rpn) == 1
    assert len(result.safety_critical) == 1


def test_summary():
    """Summary dict is well-formed."""
    result = FMEAResult("test")
    result.add(FailureMode("a", "fail", "cause", "effect",
                            severity=Severity.MINOR, occurrence=Occurrence.REMOTE,
                            detection=Detection.ALWAYS_CAUGHT))
    s = result.summary()
    assert s["total_failures"] == 1
    assert "top_5_rpn" in s


def test_classify_safety_level():
    """classify_safety_level returns correct level."""
    assert classify_safety_level(140, 200) == SafetyLevel.S2_RELEVANT
    assert classify_safety_level(50, 200) == SafetyLevel.S3_STANDARD
    assert classify_safety_level(190, 200) == SafetyLevel.S1_CRITICAL


def test_to_dict():
    """to_dict serialization includes all fields."""
    fm = FailureMode("shaft", "crack", "load", "break",
                      severity=Severity.MAJOR, occurrence=Occurrence.FREQUENT,
                      detection=Detection.LIKELY, mitigation="inspect_weekly")
    d = fm.to_dict()
    assert d["rpn"] == 80
    assert d["mitigation"] == "inspect_weekly"
    assert "safety_level" in d
