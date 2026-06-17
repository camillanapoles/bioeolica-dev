import pytest
from ai_assist_cad.nlp_parser import parse_project_parameters


def test_parse_machine_with_material():
    text = "Projete um gerador 3MW com rotor de aço silício"
    result = parse_project_parameters(text)
    assert result["machine_type"] == "generator"
    assert result["power_kW"] == 3000
    assert result["materials"] == ["steel"]


def test_parse_with_layers():
    text = "carcaça alumínio 3 camadas 6mm com jateamento"
    result = parse_project_parameters(text)
    assert "aluminum" in result["materials"]
    assert len(result["layers"]) == 1
    assert result["layers"][0]["repetitions"] == 3
    assert result["layers"][0]["thickness_mm"] == 6.0
    assert "shot_blasting" in result["processes"]


def test_parse_empty_raises():
    with pytest.raises(ValueError, match="No project description"):
        parse_project_parameters("")


def test_parse_turbine():
    text = "turbina eólica 5MW pás compósito"
    result = parse_project_parameters(text)
    assert result["machine_type"] == "turbine"
    assert result["power_kW"] == 5000
    assert "composite" in result["materials"]


def test_parse_motor_with_process():
    text = "motor com têmpera e oxidação"
    result = parse_project_parameters(text)
    assert result["machine_type"] == "motor"
    assert "tempering" in result["processes"]
    assert "oxidation" in result["processes"]
