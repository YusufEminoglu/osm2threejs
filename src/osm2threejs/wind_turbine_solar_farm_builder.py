# -*- coding: utf-8 -*-
"""Parametric Wind Turbine Rotor & Rooftop/Ground Solar PV Array 3D Mesh Generator for osm2threejs."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Sequence


@dataclass
class WindTurbineSpec:
    hub_height_m: float = 120.0
    rotor_diameter_m: float = 110.0
    tower_base_radius_m: float = 3.5
    tower_top_radius_m: float = 2.0
    num_blades: int = 3
    rated_power_mw: float = 4.2


@dataclass
class RenewableEnergyScene3D:
    total_turbines_count: int
    total_solar_panels_count: int
    estimated_annual_energy_gwh: float
    wind_turbines_mesh: dict[str, Any]
    solar_arrays_mesh: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "turbines_count": self.total_turbines_count,
            "solar_panels_count": self.total_solar_panels_count,
            "annual_energy_gwh": round(self.estimated_annual_energy_gwh, 2),
            "turbines_vertices": len(self.wind_turbines_mesh.get("vertices", [])),
            "solar_vertices": len(self.solar_arrays_mesh.get("vertices", [])),
        }


def generate_3d_renewable_energy_assets(
    turbine_locations: Sequence[tuple[float, float, float]],
    solar_farm_boundary_polygon: Sequence[tuple[float, float]] | None = None,
    turbine_spec: WindTurbineSpec | None = None,
    solar_panel_tilt_deg: float = 30.0,
) -> RenewableEnergyScene3D:
    """Generate 3D procedural meshes for wind turbine towers, rotors, and PV panel tables."""
    spec = turbine_spec or WindTurbineSpec()
    locs = list(turbine_locations)

    turbine_verts: list[tuple[float, float, float]] = []
    turbine_faces: list[tuple[int, int, int]] = []

    for tx, ty, tz in locs:
        # Tower base and hub vertices
        b_idx = len(turbine_verts)
        turbine_verts.append((tx, ty, tz))
        turbine_verts.append((tx, ty, tz + spec.hub_height_m))

        # Nacelle and 3 blades
        hub_z = tz + spec.hub_height_m
        for b in range(spec.num_blades):
            ang = (2.0 * math.pi / spec.num_blades) * b
            tip_x = tx + (spec.rotor_diameter_m / 2.0) * math.cos(ang)
            tip_z = hub_z + (spec.rotor_diameter_m / 2.0) * math.sin(ang)
            turbine_verts.append((tip_x, ty, tip_z))

    # Solar PV tables
    solar_verts: list[tuple[float, float, float]] = []
    solar_faces: list[tuple[int, int, int]] = []
    num_panels = 0

    if solar_farm_boundary_polygon and len(solar_farm_boundary_polygon) >= 3:
        min_x = min(p[0] for p in solar_farm_boundary_polygon)
        max_x = max(p[0] for p in solar_farm_boundary_polygon)
        min_y = min(p[1] for p in solar_farm_boundary_polygon)
        max_y = max(p[1] for p in solar_farm_boundary_polygon)

        panel_w = 4.0
        panel_l = 2.0
        tilt_rad = math.radians(solar_panel_tilt_deg)
        dz = panel_l * math.sin(tilt_rad)
        dy = panel_l * math.cos(tilt_rad)

        for sx in range(int(min_x), int(max_x), 8):
            for sy in range(int(min_y), int(max_y), 6):
                # 4 vertices per PV table
                v_start = len(solar_verts)
                solar_verts.append((float(sx), float(sy), 0.5))
                solar_verts.append((float(sx + panel_w), float(sy), 0.5))
                solar_verts.append((float(sx + panel_w), float(sy + dy), 0.5 + dz))
                solar_verts.append((float(sx), float(sy + dy), 0.5 + dz))

                solar_faces.append((v_start, v_start + 1, v_start + 2))
                solar_faces.append((v_start, v_start + 2, v_start + 3))
                num_panels += 1

    # Annual energy yield: ~2.5 GWh per MW turbine, ~1.4 GWh per MWp solar
    annual_wind_gwh = len(locs) * spec.rated_power_mw * 2.8
    annual_solar_gwh = num_panels * 0.0006 * 1.5

    return RenewableEnergyScene3D(
        total_turbines_count=len(locs),
        total_solar_panels_count=num_panels,
        estimated_annual_energy_gwh=annual_wind_gwh + annual_solar_gwh,
        wind_turbines_mesh={"vertices": turbine_verts, "faces": turbine_faces},
        solar_arrays_mesh={"vertices": solar_verts, "faces": solar_faces},
    )
