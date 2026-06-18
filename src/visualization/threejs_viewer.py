"""
threejs_viewer.py — 3D visualization via Three.js HTML generation.

Supports: heat maps (stress, temperature), section cuts, mesh overlay,
part interaction (rotate/zoom/pan), and automated camera paths.

Uses Jinja2 template stored alongside the module.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import jinja2

_TEMPLATE_DIR = Path(__file__).parent / "templates"
_ENV = jinja2.Environment(
    loader=jinja2.FileSystemLoader(str(_TEMPLATE_DIR)),
    autoescape=False,
)


def generate_viewer_html(
    title: str = "3D Model Viewer",
    legend_label: str = "Field Value",
    legend_min: str = "0",
    legend_max: str = "100",
    camera_position: tuple[float, float, float] = (5.0, 4.0, 8.0),
    geometry_json: str = "{}",
    field_values: list[float] | None = None,
    domain_options: list[str] | None = None,
) -> str:
    """Generate 3D viewer HTML with embedded Three.js visualization."""
    if domain_options is None:
        domain_options = ["von Mises (MPa)", "Temperature (C)", "Displacement (mm)"]

    template = _ENV.get_template("viewer.html.j2")
    return template.render(
        title=title,
        domain_options=domain_options,
        legend_label=legend_label,
        legend_min=legend_min,
        legend_max=legend_max,
        camera_x=camera_position[0],
        camera_y=camera_position[1],
        camera_z=camera_position[2],
        geometry_json=geometry_json,
        field_values=json.dumps(field_values or []),
    )


def generate_cylinder_viewer(
    title: str = "Cylinder — Thermal Analysis",
    temp_field: list[float] | None = None,
    output_path: str | None = None,
) -> str:
    """Generate a viewer for a cylinder with temperature heat map."""
    html = generate_viewer_html(
        title=title,
        legend_label="Temperature (K)",
        legend_min="300",
        legend_max="500",
        geometry_json='{"type":"cylinder","radiusTop":1.5,"radiusBottom":1.5,"height":2.0,"radialSegments":32}',
        field_values=temp_field,
        domain_options=["Temperature (K)", "Thermal Gradient", "Thermal Stress (MPa)"],
    )
    if output_path:
        Path(output_path).write_text(html)
    return html


def generate_stress_viewer(
    stress_data: dict[str, Any],
    output_path: str | None = None,
) -> str:
    """Generate a 3D stress visualization viewer."""
    html = generate_viewer_html(
        title=stress_data.get("title", "Stress Analysis"),
        legend_label="von Mises (MPa)",
        legend_min=str(round(stress_data.get("min_stress", 0), 1)),
        legend_max=str(round(stress_data.get("max_stress", 100), 1)),
        geometry_json='{"type":"box","width":2,"height":1,"depth":1}',
        domain_options=["von Mises (MPa)", "Principal Stress", "Displacement (mm)"],
    )
    if output_path:
        Path(output_path).write_text(html)
    return html
