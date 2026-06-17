"""Tests for KnowledgeEngine v2 — 10 engineering domains."""

import pytest
from ai_assist_cad.knowledge_engine import KnowledgeEngine


@pytest.fixture
def ke():
    return KnowledgeEngine("data")


# Domain 1: Mecânica
def test_load_materials(ke):
    assert len(ke.materials) >= 5
    mat = ke.get_material("steel_4340")
    assert mat["E_GPa"] == 205
    assert mat["sigma_y_MPa"] == 710


def test_get_material_not_found(ke):
    assert ke.get_material("unknown_material") is None


def test_list_materials(ke):
    mats = ke.list_materials()
    assert isinstance(mats, list) and len(mats) > 0


def test_dimension_shaft(ke):
    shaft = ke.dimension_shaft(torque_Nm=20000)
    assert 30 < shaft["diameter_mm"] < 200
    assert shaft["torque_Nm"] == 20000


def test_beam_bending(ke):
    beam = ke.dimension_beam_bending(moment_Nm=5000, sigma_adm_MPa=150)
    assert beam["section_modulus_mm3"] > 0
    assert beam["height_mm"] > 0


# Domain 2: Fluidos
def test_pump_power(ke):
    pump = ke.dimension_pump_power(rho_kgm3=1000, Q_m3s=0.1, head_m=30)
    assert pump["power_W"] > 0
    assert pump["power_kW"] > 0


def test_pipe_diameter(ke):
    pipe = ke.dimension_pipe_diameter(Q_m3s=0.05, v_max_ms=2.5)
    assert pipe["diameter_mm"] > 0


# Domain 3: Termo
def test_heat_exchanger(ke):
    hx = ke.dimension_heat_exchanger(Q_W=50000, U_Wm2K=500, delta_T_log_K=30)
    assert hx["area_m2"] > 0


def test_thermal_expansion(ke):
    exp = ke.thermal_expansion(L0_m=10, delta_T_K=50)
    assert exp["expansion_mm"] > 0


# Domain 4: Energia
def test_battery_capacity(ke):
    batt = ke.dimension_battery_capacity(P_W=5000, t_h=10, V_V=48)
    assert batt["capacity_Ah"] > 0
    assert batt["energy_Wh"] > 0


# Domain 5: Eletricidade
def test_dimension_stator(ke):
    stator = ke.dimension_stator_outer(power_kW=3000, rpm=1500, poles=4)
    assert 200 < stator["diameter_mm"] < 1000
    assert stator["frequency_Hz"] == 50.0


def test_transformer(ke):
    tf = ke.dimension_transformer(S_kVA=500, B_T=1.5, J_Amm2=3.0)
    assert tf["core_area_cm2"] > 0


# Domain 6: Materiais
def test_estimate_mass(ke):
    mass = ke.estimate_mass(volume_m3=1.0, material_key="steel_4340")
    assert mass == 7850.0
    assert ke.estimate_mass(1.0, "unknown") is None


def test_material_cost(ke):
    cost = ke.material_cost(mass_kg=100, material_key="steel_4340")
    assert cost["cost_USD"] > 0


# Domain 7: Construção
def test_bolt_dimension(ke):
    bolt = ke.dimension_bolt(force_N=50000, sigma_adm_MPa=200)
    assert bolt["diameter_mm"] > 0


def test_weld_throat(ke):
    weld = ke.weld_throat(force_N=30000, weld_length_mm=100, tau_adm_MPa=100)
    assert weld["throat_mm"] > 0
    assert weld["leg_mm"] > weld["throat_mm"]


# Domain 8: Ambiente
def test_wind_load(ke):
    wind = ke.wind_load(rho_kgm3=1.2, v_ms=30, A_m2=10)
    assert wind["force_N"] > 0


# Domain 9: Normativo
def test_safety_factor(ke):
    sf = ke.safety_factor_yield(sigma_yield_MPa=250, sigma_applied_MPa=100)
    assert sf["safety_factor"] == 2.5
    assert sf["status"] == "PASS"


# Domain 10: Econômico
def test_lifecycle_cost(ke):
    lcc = ke.lifecycle_cost(initial_cost=50000, annual_opex=5000, years=5)
    assert lcc["LCC_USD"] > 50000


# Multi-domain
def test_dimension_all(ke):
    ctx = {"torque_Nm": 20000, "power_kW": 3000, "volume_m3": 0.5, "material": "steel_4340"}
    results = ke.dimension_all(ctx)
    assert "shaft" in results
    assert "stator" in results
    assert "mass_kg" in results
