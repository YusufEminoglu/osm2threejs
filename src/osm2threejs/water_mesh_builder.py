# -*- coding: utf-8 -*-
"""3D Animated Water Surface & Gerstner Wave Geometry Generator for osm2threejs."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Sequence


@dataclass
class GerstnerWaveParams:
    amplitude_m: float = 0.45
    wavelength_m: float = 25.0
    speed_ms: float = 1.2
    direction_degrees: float = 45.0  # Wave propagation heading


@dataclass
class WaterSurfaceMesh3D:
    waterbody_id: str
    grid_rows: int
    grid_cols: int
    vertices: list[tuple[float, float, float]]
    faces: list[tuple[int, int, int]]
    normals: list[tuple[float, float, float]]
    water_color_hex: str = "#0077b6"
    foam_color_hex: str = "#e0fbfc"

    def to_dict(self) -> dict[str, Any]:
        return {
            "waterbody_id": self.waterbody_id,
            "vertex_count": len(self.vertices),
            "face_count": len(self.faces),
            "color": self.water_color_hex,
        }


def generate_animated_water_mesh(
    bounding_polygon: Sequence[tuple[float, float]],
    waterbody_id: str = "water_1",
    mesh_resolution: float = 15.0,
    elevation_z: float = 0.0,
    wave_params: GerstnerWaveParams | None = None,
) -> WaterSurfaceMesh3D:
    """Generate triangulated 3D water polygon mesh with Gerstner wave displacement vertices."""
    poly = list(bounding_polygon)
    if len(poly) < 3:
        return WaterSurfaceMesh3D(waterbody_id, 0, 0, [], [], [])

    min_x = min(p[0] for p in poly)
    max_x = max(p[0] for p in poly)
    min_y = min(p[1] for p in poly)
    max_y = max(p[1] for p in poly)

    cols = max(2, int((max_x - min_x) / mesh_resolution) + 1)
    rows = max(2, int((max_y - min_y) / mesh_resolution) + 1)
    dx = (max_x - min_x) / max(1, cols - 1)
    dy = (max_y - min_y) / max(1, rows - 1)

    waves = wave_params or GerstnerWaveParams()
    w_k = (2.0 * math.pi) / max(1.0, waves.wavelength_m)
    w_rad = math.radians(waves.direction_degrees)
    dir_x = math.cos(w_rad)
    dir_y = math.sin(w_rad)

    vertices: list[tuple[float, float, float]] = []
    normals: list[tuple[float, float, float]] = []

    for r in range(rows):
        vy = min_y + r * dy
        for c in range(cols):
            vx = min_x + c * dx
            # Gerstner Wave displacement
            dot_prod = dir_x * vx + dir_y * vy
            wave_disp = waves.amplitude_m * math.sin(w_k * dot_prod)
            disp_x = vx - dir_x * waves.amplitude_m * math.cos(w_k * dot_prod) * 0.5
            disp_y = vy - dir_y * waves.amplitude_m * math.cos(w_k * dot_prod) * 0.5
            disp_z = elevation_z + wave_disp

            vertices.append((disp_x, disp_y, disp_z))
            normals.append((0.0, 0.0, 1.0))

    faces: list[tuple[int, int, int]] = []
    for r in range(rows - 1):
        for c in range(cols - 1):
            i1 = r * cols + c
            i2 = r * cols + (c + 1)
            i3 = (r + 1) * cols + c
            i4 = (r + 1) * cols + (c + 1)

            faces.append((i1, i2, i3))
            faces.append((i2, i4, i3))

    return WaterSurfaceMesh3D(
        waterbody_id=waterbody_id,
        grid_rows=rows,
        grid_cols=cols,
        vertices=vertices,
        faces=faces,
        normals=normals,
    )
