"""Tests for preCICE coupling adapter."""

import pytest
from src.coupling.precice_adapter import (
    PreCICEAdapter, CouplingConfig, CouplingParticipant,
    FSI_CONFIG, THERMAL_STRUCTURAL_CONFIG, generate_precice_xml,
)


def test_fsi_config_valid():
    """Default FSI config is valid."""
    errors = FSI_CONFIG.validate()
    assert errors == []


def test_thermal_structural_config_valid():
    """Default thermal-structural config is valid."""
    errors = THERMAL_STRUCTURAL_CONFIG.validate()
    assert errors == []


def test_invalid_scenario():
    """Unknown scenario returns validation error."""
    config = CouplingConfig(scenario="unknown")
    errors = config.validate()
    assert len(errors) > 0


def test_single_participant_invalid():
    """Single participant is invalid."""
    config = CouplingConfig(scenario="fsi", participants=[
        CouplingParticipant("Fluid", "FluidMesh", write_data=["Force"]),
    ])
    errors = config.validate()
    assert any("≥2" in e for e in errors)


def test_adapter_initialize():
    """Adapter initializes and validates."""
    adapter = PreCICEAdapter("fsi")
    assert adapter.initialize() is True


def test_adapter_generates_xml():
    """XML config is generated without error."""
    adapter = PreCICEAdapter("fsi")
    xml = adapter.generate_xml()
    assert "<precice-configuration>" in xml
    assert "Fluid" in xml
    assert "Solid" in xml


def test_adapter_advance():
    """Advance succeeds when initialized."""
    adapter = PreCICEAdapter("fsi")
    adapter.initialize()
    assert adapter.advance(0.01) is True


def test_adapter_advance_fails_uninitialized():
    """Advance fails without initialization."""
    adapter = PreCICEAdapter("fsi")
    assert adapter.advance(0.01) is False


def test_custom_config():
    """Custom coupling config works."""
    config = CouplingConfig(
        scenario="conjugate_ht",
        participants=[
            CouplingParticipant("Fluid", "Mesh1", write_data=["Temperature"]),
            CouplingParticipant("Solid", "Mesh2", read_data=["Temperature"]),
        ],
    )
    assert config.validate() == []


def test_xml_generated_for_thermal():
    """Thermal-structural XML is generated."""
    adapter = PreCICEAdapter("thermal_structural")
    xml = adapter.generate_xml()
    assert "Thermal" in xml or "Structural" in xml
