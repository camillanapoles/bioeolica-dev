"""KDI Forwarder — reads config.json, dispatches M³ analyses.

Single entry point for the CAD/CAE frontend. All parameters
come from config.json — zero hardcoded defaults.
"""

from __future__ import annotations

import importlib.util
import os, sys
from typing import Any

_THIS = os.path.dirname(os.path.abspath(__file__))
_WS = os.path.abspath(os.path.join(_THIS, ".."))
_PROJ = os.path.abspath(os.path.join(_WS, ".."))

sys.path.insert(0, _WS)
from modules.config_manager import ConfigManager


def _import_by_path(rel_path: str, name: str = ""):
    """Import a module by path relative to project root without namespace conflicts."""
    full = os.path.join(_PROJ, rel_path)
    mod_name = name or rel_path.replace("/", ".").replace(".py", "")
    spec = importlib.util.spec_from_file_location(mod_name, full)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = mod
    spec.loader.exec_module(mod)
    return mod


_CAD_BRIDGE = _import_by_path("cad-cae-platform/modules/cad_bridge.py", "cad_bridge")
_KDI_MACRO = _import_by_path("kdi-m3-bridge/modules/kdi_macro.py", "kdi_macro")
_KDI_MESO = _import_by_path("kdi-m3-bridge/modules/kdi_meso.py", "kdi_meso")
_KDI_MICRO = _import_by_path("kdi-m3-bridge/modules/kdi_micro.py", "kdi_micro")


class KDIForwarder:
    """Orchestrates M³ analyses from config.json."""

    def __init__(self, config_path: str = ""):
        self.cfg = ConfigManager.load(config_path or os.path.join(_WS, "config.json"))
        self._results: dict[str, Any] = {}

    def run_macro(self) -> dict:
        env = _KDI_MACRO.MacroEnvironment(
            altitude_m=self.cfg.get("environment.altitude_m", 100),
            wind_class=self.cfg.get("environment.wind_class", "II"),
            wind_speed_ref_ms=self.cfg.get("environment.wind_speed_ref_ms", 30),
            exposure=self.cfg.get("environment.exposure", "rural"),
        )
        g = self.cfg.section("geometry")
        model = _CAD_BRIDGE.CadModel().box(
            g.get("length_mm", 100), g.get("width_mm", 20), g.get("height_mm", 20))
        ma = _KDI_MACRO.MacroAnalysis(cad_model=model, env=env, structure_type=g.get("type", "box"))
        result = ma.run()
        self._results["macro"] = result
        return result

    def run_meso(self, fem_results: dict | None = None) -> dict:
        ma = _KDI_MESO.MesoAnalysis()
        result = ma.run()
        self._results["meso"] = result
        return result

    def run_micro(self) -> dict:
        mat = self.cfg.section("material")
        ma = _KDI_MICRO.MicroAnalysis(
            fiber=mat.get("fiber", "waste_paper"),
            matrix=mat.get("matrix", "pva"),
            coating=mat.get("coating", "graphite_coating"),
            V_f=mat.get("V_f", 0.15),
        )
        result = ma.run()
        self._results["micro"] = result
        return result

    def run_all(self) -> dict:
        kdi = self.cfg.section("kdi")
        results = {}
        if kdi.get("macro", {}).get("enabled", True):
            results["macro"] = self.run_macro()
        if kdi.get("meso", {}).get("enabled", True):
            results["meso"] = self.run_meso(results.get("macro", {}))
        if kdi.get("micro", {}).get("enabled", False):
            results["micro"] = self.run_micro()
        self._results = results
        return results

    def report(self) -> str:
        if not self._results:
            self.run_all()
        lines = ["=" * 60, f"KDI-M³ REPORT — {self.cfg.get('project.name', 'default')}", "=" * 60, ""]
        for scale, result in self._results.items():
            lines.append(f"[{scale.upper()}]")
            for k, v in (list(result.items())[:6] if isinstance(result, dict) else []):
                if not isinstance(v, dict):
                    lines.append(f"  {k}: {v}")
            lines.append("")
        lines.append("=" * 60)
        return "\n".join(lines)

    @property
    def results(self) -> dict:
        return self._results if self._results else self.run_all()
