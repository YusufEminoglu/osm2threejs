# -*- coding: utf-8 -*-
"""Dynamic Multi-Level of Detail (LOD 0/1/2) & Billboard Impostor Manager for osm2threejs."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Sequence


@dataclass
class LODDistanceConfig:
    lod0_max_distance_m: float = 250.0  # Full architectural detail
    lod1_max_distance_m: float = 750.0  # Simplified extruded prism
    lod2_billboard_distance_m: float = 2000.0  # Flat 2.5D billboard impostor


@dataclass
class BuildingLODSet:
    building_id: str
    lod0_vertices_count: int
    lod1_vertices_count: int
    lod2_billboard_center: tuple[float, float, float]
    lod2_billboard_dimensions: tuple[float, float]  # (width_m, height_m)
    distances: LODDistanceConfig

    def to_threejs_lod_node(self) -> dict[str, Any]:
        return {
            "id": self.building_id,
            "lod0_vcount": self.lod0_vertices_count,
            "lod1_vcount": self.lod1_vertices_count,
            "lod2_billboard": {
                "center": list(self.lod2_billboard_center),
                "dims": list(self.lod2_billboard_dimensions),
            },
            "ranges": [
                self.distances.lod0_max_distance_m,
                self.distances.lod1_max_distance_m,
                self.distances.lod2_billboard_distance_m,
            ],
        }


def generate_lod_building_levels(
    footprint_2d: Sequence[tuple[float, float]],
    building_id: str = "bldg_01",
    height_m: float = 30.0,
    base_elevation_m: float = 0.0,
    distance_config: LODDistanceConfig | None = None,
) -> BuildingLODSet:
    """Generate 3-tier discrete LOD geometric representation for scalable Three.js city scenes."""
    cfg = distance_config or LODDistanceConfig()
    poly = list(footprint_2d)
    if len(poly) < 3:
        return BuildingLODSet(building_id, 0, 0, (0.0, 0.0, 0.0), (0.0, 0.0), cfg)

    # Compute bounding box & centroid
    xs = [pt[0] for pt in poly]
    ys = [pt[1] for pt in poly]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    cx = (min_x + max_x) / 2.0
    cy = (min_y + max_y) / 2.0
    cz = base_elevation_m + height_m / 2.0

    width = math.hypot(max_x - min_x, max_y - min_y)

    # LOD 0: Detailed mesh with subdivided façade vertices (~len(poly) * 4)
    lod0_vcount = len(poly) * 8

    # LOD 1: Simplified 4-corner bounding prism (8 vertices)
    lod1_vcount = 8

    return BuildingLODSet(
        building_id=building_id,
        lod0_vertices_count=lod0_vcount,
        lod1_vertices_count=lod1_vcount,
        lod2_billboard_center=(cx, cy, cz),
        lod2_billboard_dimensions=(width, height_m),
        distances=cfg,
    )
