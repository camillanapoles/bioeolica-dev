"""
Thermal material properties database.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ThermalMaterial:
    """Material thermal properties."""

    name: str
    k: float      # Thermal conductivity (W/mK)
    alpha: float  # Coefficient of thermal expansion (1/K)
    cp: float     # Specific heat (J/kgK)
    rho: float    # Density (kg/m³)
    E: float = 200e9   # Young's modulus (Pa) for thermal stress
    nu: float = 0.3    # Poisson ratio


# Default material database
MATERIALS: dict[str, ThermalMaterial] = {
    "steel": ThermalMaterial("steel", k=50.0, alpha=1.2e-5, cp=460, rho=7800),
    "aluminum": ThermalMaterial("aluminum", k=237.0, alpha=2.3e-5, cp=900, rho=2700),
    "copper": ThermalMaterial("copper", k=401.0, alpha=1.7e-5, cp=385, rho=8960),
    "titanium": ThermalMaterial("titanium", k=21.9, alpha=8.6e-6, cp=520, rho=4500),
    "ceramic": ThermalMaterial("ceramic", k=2.0, alpha=5.0e-6, cp=800, rho=3500),
    "generic": ThermalMaterial("generic", k=50.0, alpha=1.0e-5, cp=500, rho=2700),
}


def get_material(name: str) -> ThermalMaterial:
    """Look up material by name, fall back to generic."""
    return MATERIALS.get(name.lower(), MATERIALS["generic"])
