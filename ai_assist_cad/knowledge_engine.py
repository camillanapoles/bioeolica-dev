"""ai_assist_cad/knowledge_engine.py"""
import json, os
from typing import Dict, Optional


class KnowledgeEngine:
    """Carrega dados externos — materiais, processos, conhecimento de máquinas.

    Single Source of Truth: todos os valores VIVEM em data/*.json,
    nunca hardcoded nos módulos.
    """

    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.materials: Dict = {}
        self._load()

    def _load(self):
        path = os.path.join(self.data_dir, "materials.json")
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                self.materials = json.load(f)

    def get_material(self, name: str) -> Optional[Dict]:
        return self.materials.get(name)

    def list_materials(self) -> list:
        return list(self.materials.keys())

    def dimension_shaft(self, torque_Nm: float, tau_adm_MPa: float = 80) -> Dict:
        """d = (16 * T / (pi * tau_adm))^(1/3) — torção em eixo maciço."""
        d_mm = ((16 * torque_Nm * 1000) / (3.14159 * tau_adm_MPa)) ** (1 / 3) * 1.5
        return {"diameter_mm": round(d_mm, 1), "torque_Nm": torque_Nm}

    def dimension_stator_outer(self, power_kW: float, rpm: float = 1500, poles: int = 4) -> Dict:
        """D_estator ≈ 250 * P^0.4 * (1500/n)^0.25 — escalonamento empírico."""
        D_mm = 250 * (power_kW / 100) ** 0.4 * (1500 / rpm) ** 0.25
        return {"diameter_mm": round(D_mm, 1), "poles": poles,
                "frequency_Hz": round(poles * rpm / 120, 1)}

    def estimate_mass(self, volume_m3: float, material_key: str) -> Optional[float]:
        mat = self.get_material(material_key)
        if mat:
            return round(volume_m3 * mat["density"], 1)
        return None
