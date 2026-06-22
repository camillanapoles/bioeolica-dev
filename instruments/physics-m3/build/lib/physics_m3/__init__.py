"""Physics M³ Workspace — computational mechanics for multi-scale analysis."""
from modules.composite_model import CompositeMaterial, FabricationProcess
from modules.m3_analysis import M3Analysis
from modules.structural_analysis import BeamSection, PlyProperties, CompositeLaminate
from modules.fem_solver import BeamElement, FEModel
from modules.fluid_dynamics import Airfoil
from modules.thermodynamics import DryingProcess
from modules.electromechanical import PMSG, DCMachine, BatteryStorage
from modules.method_selector import MethodRecommendation, ProblemCharacteristics
from modules.uncertainty import UncertainValue, MonteCarloSampler
from modules.vvv_protocol import VVVReport, CrossValidation
from modules.topopt_avancada import TopOpt3D
from modules.topopt_multiobj import TopOptMultiObj
from modules.topopt_manufacturing import TopOptManufacturing
from modules.validacao_experimental import (
    compare_simulation_experiment,
    calibrate_model,
    validate_structural_benchmark,
    generate_vvv_report,
    monte_carlo_uq,
    sensitivity_analysis,
)

__version__ = "1.2.0"
