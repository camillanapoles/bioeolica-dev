import pytest
from modules.method_selector import (
    ProblemCharacteristics, MethodRecommendation,
    select_method, recommend_for_wind_turbine_blade
)

def test_problem_init():
    pc = ProblemCharacteristics(is_fluid=True)
    assert pc.is_fluid is True

def test_select_method_fsi():
    pc = ProblemCharacteristics(deformation_regime="large", has_fsi=True)
    rec = select_method(pc)
    assert isinstance(rec, MethodRecommendation) or rec is not None

def test_wind_recommendation():
    rec = recommend_for_wind_turbine_blade()
    assert isinstance(rec, MethodRecommendation) or rec is not None
