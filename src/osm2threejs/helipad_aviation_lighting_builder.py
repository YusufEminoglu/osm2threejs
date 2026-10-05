# -*- coding: utf-8 -*-
"""3D Rooftop & Ground Helipad Mesh with Aviation Beacon Lighting for osm2threejs."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any


@dataclass
class HelipadLightingProfile:
    perimeter_lights_count: int = 16
    beacon_light_color_hex: str = "#00ff00"  # ICAO Green perimeter lighting
    floodlight_towers_count: int = 4
    has_flashing_identification_beacon: bool = True


@dataclass
class HelipadAviation3D:
    helipad_id: str
    touchdown_diameter_m: float
    approach_heading_deg: float
    perimeter_beacons_count: int
    helipad_mesh: dict[str, Any]
    aviation_lighting_nodes: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "helipad_id": self.helipad_id,
            "diameter_m": round(self.touchdown_diameter_m, 1),
            "heading_deg": round(self.approach_heading_deg, 1),
            "beacons_count": self.perimeter_beacons_count,
            "vertices_count": len(self.helipad_mesh.get("vertices", [])),
            "lights_count": len(self.aviation_lighting_nodes),
        }


def generate_3d_helipad_mesh(
    center_coordinates: tuple[float, float, float] = (0.0, 0.0, 25.0),
    touchdown_diameter_m: float = 18.0,
    approach_heading_deg: float = 45.0,
    lighting: HelipadLightingProfile | None = None,
) -> HelipadAviation3D:
    """Generate 3D procedural meshes for ICAO Annex 14 compliant rooftop helipads with LED perimeter beacons."""
    prof = lighting or HelipadLightingProfile()
    cx, cy, cz = center_coordinates
    r = touchdown_diameter_m / 2.0

    # Helipad deck circular disc vertices
    num_segments = 24
    verts: list[tuple[float, float, float]] = [(cx, cy, cz)]
    faces: list[tuple[int, int, int]] = []

    for i in range(num_segments):
        ang = (2.0 * math.pi / num_segments) * i
        vx = cx + r * math.cos(ang)
        vy = cy + r * math.sin(ang)
        verts.append((vx, vy, cz))

    for i in range(1, num_segments):
        faces.append((0, i, i + 1))
    faces.append((0, num_segments, 1))

    # Aviation lighting nodes along perimeter
    lights: list[dict[str, Any]] = []
    for i in range(prof.perimeter_lights_count):
        ang = (2.0 * math.pi / prof.perimeter_lights_count) * i
        lx = cx + (r * 1.05) * math.cos(ang)
        ly = cy + (r * 1.05) * math.sin(ang)
        lights.append({
            "id": f"PERIMETER_LED_{i+1}",
            "position": (round(lx, 2), round(ly, 2), round(cz + 0.15, 2)),
            "color": prof.beacon_light_color_hex,
            "intensity_cd": 100.0,
        })

    return HelipadAviation3D(
        helipad_id="HELIPAD_ROOFTOP_1",
        touchdown_diameter_m=touchdown_diameter_m,
        approach_heading_deg=approach_heading_deg,
        perimeter_beacons_count=len(lights),
        helipad_mesh={"vertices": verts, "faces": faces},
        aviation_lighting_nodes=lights,
    )
