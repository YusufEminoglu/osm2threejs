# -*- coding: utf-8 -*-
"""Parametric Suspension & Cable-Stayed Bridge 3D Pylon & Catenary Cable Generator for osm2threejs."""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from typing import Any, Sequence


class BridgePylonType(str, Enum):
    H_FRAME = "H_FRAME"
    A_FRAME = "A_FRAME"
    SINGLE_PYLON = "SINGLE_PYLON"


@dataclass
class BridgeStructure3D:
    bridge_id: str
    pylon_type: BridgePylonType
    span_length_m: float
    tower_height_m: float
    pylon_vertices: list[tuple[float, float, float]]
    cable_catenary_points: list[tuple[float, float, float]]
    hanger_count: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "bridge_id": self.bridge_id,
            "pylon_type": self.pylon_type.value,
            "span_length_m": round(self.span_length_m, 1),
            "tower_height_m": round(self.tower_height_m, 1),
            "pylon_vcount": len(self.pylon_vertices),
            "cable_points_count": len(self.cable_catenary_points),
            "hangers_count": self.hanger_count,
        }


def generate_3d_suspension_bridge_mesh(
    bridge_centerline: Sequence[tuple[float, float, float]],
    bridge_id: str = "Bosphorus_Bridge",
    pylon_type: BridgePylonType = BridgePylonType.H_FRAME,
    tower_height_m: float = 65.0,
    num_hangers: int = 16,
) -> BridgeStructure3D:
    """Generate 3D structural suspension bridge geometry including main catenary cables and vertical suspenders."""
    pts = list(bridge_centerline)
    if len(pts) < 2:
        return BridgeStructure3D(bridge_id, pylon_type, 0.0, tower_height_m, [], [], 0)

    p_start = pts[0]
    p_end = pts[-1]
    span = math.dist(p_start, p_end)

    # Compute pylon tower positions at 1/4 and 3/4 span
    dx = (p_end[0] - p_start[0]) / span
    dy = (p_end[1] - p_start[1]) / span
    deck_z = (p_start[2] + p_end[2]) / 2.0

    t1_x = p_start[0] + dx * (span * 0.25)
    t1_y = p_start[1] + dy * (span * 0.25)

    t2_x = p_start[0] + dx * (span * 0.75)
    t2_y = p_start[1] + dy * (span * 0.75)

    pylon_verts: list[tuple[float, float, float]] = [
        # Tower 1 footing to peak
        (t1_x, t1_y, deck_z - 15.0),
        (t1_x, t1_y, deck_z + tower_height_m),
        # Tower 2 footing to peak
        (t2_x, t2_y, deck_z - 15.0),
        (t2_x, t2_y, deck_z + tower_height_m),
    ]

    # Generate parabolic catenary cable curve between towers:
    # z(s) = z_peak - 4 * sag * (s / span_main) * (1 - s / span_main)
    cables: list[tuple[float, float, float]] = []
    sag_m = tower_height_m * 0.75

    for i in range(num_hangers + 1):
        frac = i / float(num_hangers)
        s_x = t1_x + (t2_x - t1_x) * frac
        s_y = t1_y + (t2_y - t1_y) * frac
        catenary_z = (deck_z + tower_height_m) - 4.0 * sag_m * frac * (1.0 - frac)
        cables.append((round(s_x, 2), round(s_y, 2), round(catenary_z, 2)))

    return BridgeStructure3D(
        bridge_id=bridge_id,
        pylon_type=pylon_type,
        span_length_m=span,
        tower_height_m=tower_height_m,
        pylon_vertices=pylon_verts,
        cable_catenary_points=cables,
        hanger_count=num_hangers,
    )
