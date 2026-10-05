# -*- coding: utf-8 -*-
"""Procedural 3D Road Network, Bridge Decks & Overpass Geometry Generator for osm2threejs."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence


@dataclass
class BridgeDeckMesh:
    """3D Mesh for an elevated bridge deck or overpass."""

    vertices: list[tuple[float, float, float]]
    faces: list[tuple[int, int, int]]
    pier_positions: list[tuple[float, float, float]]
    deck_thickness: float = 0.80


@dataclass
class RoadGeometry3D:
    """Complete 3D procedural road mesh."""

    road_id: str
    road_class: str  # 'motorway', 'primary', 'secondary', 'residential'
    width_meters: float
    vertices: list[tuple[float, float, float]]
    faces: list[tuple[int, int, int]]
    is_bridge: bool = False
    bridge_mesh: BridgeDeckMesh | None = None


def generate_3d_road_mesh(
    centerline_coords: Sequence[tuple[float, float, float] | tuple[float, float]],
    road_id: str = "road_1",
    road_class: str = "primary",
    width: float = 8.0,
    is_bridge: bool = False,
    bridge_elevation: float = 6.0,
) -> RoadGeometry3D:
    """Generate 3D extruded road strip with curbs, elevation transitions, and bridge deck."""
    coords_3d = [
        (p[0], p[1], (p[2] if len(p) > 2 else 0.0) + (bridge_elevation if is_bridge else 0.0))
        for p in centerline_coords
    ]
    n = len(coords_3d)
    if n < 2:
        return RoadGeometry3D(road_id=road_id, road_class=road_class, width_meters=width, vertices=[], faces=[])

    half_w = width / 2.0
    vertices: list[tuple[float, float, float]] = []
    faces: list[tuple[int, int, int]] = []

    # Generate parallel left and right edge vertices
    for i in range(n):
        cx, cy, cz = coords_3d[i]
        if i < n - 1:
            dx = coords_3d[i + 1][0] - cx
            dy = coords_3d[i + 1][1] - cy
        else:
            dx = cx - coords_3d[i - 1][0]
            dy = cy - coords_3d[i - 1][1]

        length = math.hypot(dx, dy)
        if length <= 1e-6:
            nx, ny = 0.0, 1.0
        else:
            nx = -dy / length
            ny = dx / length

        # Left vertex
        vertices.append((cx + nx * half_w, cy + ny * half_w, cz))
        # Right vertex
        vertices.append((cx - nx * half_w, cy - ny * half_w, cz))

    # Connect road strip quads
    for i in range(n - 1):
        l1 = 2 * i
        r1 = 2 * i + 1
        l2 = 2 * (i + 1)
        r2 = 2 * (i + 1) + 1

        faces.append((l1, r1, l2))
        faces.append((r1, r2, l2))

    bridge_mesh: BridgeDeckMesh | None = None
    if is_bridge:
        pier_positions = [(coords_3d[i][0], coords_3d[i][1], 0.0) for i in range(1, n - 1)]
        bridge_mesh = BridgeDeckMesh(
            vertices=vertices,
            faces=faces,
            pier_positions=pier_positions,
            deck_thickness=1.0,
        )

    return RoadGeometry3D(
        road_id=road_id,
        road_class=road_class,
        width_meters=width,
        vertices=vertices,
        faces=faces,
        is_bridge=is_bridge,
        bridge_mesh=bridge_mesh,
    )
