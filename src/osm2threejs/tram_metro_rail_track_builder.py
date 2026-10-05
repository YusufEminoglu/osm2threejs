# -*- coding: utf-8 -*-
"""3D Urban Light Rail & Tram Track Extrusion with Overhead Catenary Wires for osm2threejs."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Sequence


@dataclass
class RailTrackProfile:
    gauge_width_m: float = 1.435  # Standard UIC track gauge (1435 mm)
    rail_head_width_m: float = 0.07
    rail_height_m: float = 0.17
    sleeper_spacing_m: float = 0.60
    sleeper_width_m: float = 2.40
    catenary_wire_height_m: float = 5.50
    catenary_mast_spacing_m: float = 40.0


@dataclass
class RailwayGeometry3D:
    track_id: str
    track_length_m: float
    rail_left_vertices: list[tuple[float, float, float]]
    rail_right_vertices: list[tuple[float, float, float]]
    sleepers_count: int
    catenary_masts_count: int
    overhead_wire_vertices: list[tuple[float, float, float]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "track_id": self.track_id,
            "track_length_m": round(self.track_length_m, 1),
            "rail_verts": len(self.rail_left_vertices) * 2,
            "sleepers": self.sleepers_count,
            "catenary_masts": self.catenary_masts_count,
            "wire_points": len(self.overhead_wire_vertices),
        }


def generate_3d_railway_mesh(
    track_centerline_3d: Sequence[tuple[float, float, float]],
    track_id: str = "T1_Tramway",
    profile: RailTrackProfile | None = None,
) -> RailwayGeometry3D:
    """Generate 3D twin steel rails, transverse sleepers, and overhead electric catenary wire geometry."""
    p = profile or RailTrackProfile()
    pts = list(track_centerline_3d)

    if len(pts) < 2:
        return RailwayGeometry3D(track_id, 0.0, [], [], 0, 0, [])

    half_gauge = p.gauge_width_m / 2.0
    left_rails: list[tuple[float, float, float]] = []
    right_rails: list[tuple[float, float, float]] = []
    catenary_wire: list[tuple[float, float, float]] = []

    tot_len = 0.0

    for i in range(len(pts)):
        curr = pts[i]
        # Tangent vector
        if i == 0:
            dx = pts[1][0] - curr[0]
            dy = pts[1][1] - curr[1]
        elif i == len(pts) - 1:
            dx = curr[0] - pts[i - 1][0]
            dy = curr[1] - pts[i - 1][1]
        else:
            dx = pts[i + 1][0] - pts[i - 1][0]
            dy = pts[i + 1][1] - pts[i - 1][1]

        seg_len = math.hypot(dx, dy)
        if seg_len < 1e-4:
            nx, ny = 1.0, 0.0
        else:
            # Perpendicular normal vector
            nx = -dy / seg_len
            ny = dx / seg_len

        lx = curr[0] + nx * half_gauge
        ly = curr[1] + ny * half_gauge
        rx = curr[0] - nx * half_gauge
        ry = curr[1] - ny * half_gauge

        left_rails.append((round(lx, 3), round(ly, 3), round(curr[2] + p.rail_height_m, 3)))
        right_rails.append((round(rx, 3), round(ry, 3), round(curr[2] + p.rail_height_m, 3)))
        catenary_wire.append((round(curr[0], 3), round(curr[1], 3), round(curr[2] + p.catenary_wire_height_m, 3)))

        if i > 0:
            tot_len += math.dist(pts[i - 1], pts[i])

    sleepers_count = int(tot_len // p.sleeper_spacing_m) + 1
    masts_count = int(tot_len // p.catenary_mast_spacing_m) + 1

    return RailwayGeometry3D(
        track_id=track_id,
        track_length_m=tot_len,
        rail_left_vertices=left_rails,
        rail_right_vertices=right_rails,
        sleepers_count=sleepers_count,
        catenary_masts_count=masts_count,
        overhead_wire_vertices=catenary_wire,
    )
