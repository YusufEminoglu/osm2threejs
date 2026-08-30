# -*- coding: utf-8 -*-
"""3D Solar Ray-Traced Ground Shadow Baking & Occlusion Texture Generator for osm2threejs."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Sequence


@dataclass
class ShadowBakeResult:
    sun_azimuth_deg: float
    sun_elevation_deg: float
    total_shadow_area_m2: float
    ground_occlusion_ratio: float
    shadow_polygons: list[list[tuple[float, float]]]

    def to_geojson(self) -> dict[str, Any]:
        features = []
        for poly in self.shadow_polygons:
            features.append({
                "type": "Feature",
                "properties": {"type": "GROUND_SHADOW"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[round(p[0], 2), round(p[1], 2)] for p in poly]],
                },
            })
        return {"type": "FeatureCollection", "features": features}


def bake_static_building_shadows(
    building_footprints: Sequence[Sequence[tuple[float, float]]],
    building_heights: Sequence[float],
    sun_azimuth_deg: float = 180.0,  # 180 = Due South
    sun_elevation_deg: float = 45.0,  # 45 = Mid-day altitude
) -> ShadowBakeResult:
    """Cast geometric directional ground shadow polygons from extruded building prisms."""
    polys = list(building_footprints)
    heights = list(building_heights)
    n = len(polys)

    elev_rad = math.radians(max(5.0, min(89.0, sun_elevation_deg)))
    az_rad = math.radians(sun_azimuth_deg)

    # Shadow vector direction is opposite to sun direction
    # Sun vector points from azimuth, shadow points in (azimuth + 180)
    shad_dir_x = -math.sin(az_rad)
    shad_dir_y = -math.cos(az_rad)
    tan_elev = math.tan(elev_rad)

    shadow_polygons: list[list[tuple[float, float]]] = []
    tot_shadow_area = 0.0

    for i in range(n):
        fp = list(polys[i])
        h = heights[i] if i < len(heights) else 10.0
        if len(fp) < 3:
            continue

        shadow_len = h / tan_elev
        offset_x = shad_dir_x * shadow_len
        offset_y = shad_dir_y * shadow_len

        # Projected roof vertices
        projected_roof = [(p[0] + offset_x, p[1] + offset_y) for p in fp]

        # Combine footprint + projected roof into ground shadow convex envelope
        all_shadow_pts = fp + projected_roof

        # Approximate shadow polygon
        combined_poly = fp + list(reversed(projected_roof))
        if combined_poly[0] != combined_poly[-1]:
            combined_poly.append(combined_poly[0])

        shadow_polygons.append(combined_poly)

        # Shoelace area
        a = 0.0
        for j in range(len(combined_poly) - 1):
            a += combined_poly[j][0] * combined_poly[j + 1][1] - combined_poly[j + 1][0] * combined_poly[j][1]
        tot_shadow_area += abs(a) * 0.5

    return ShadowBakeResult(
        sun_azimuth_deg=sun_azimuth_deg,
        sun_elevation_deg=sun_elevation_deg,
        total_shadow_area_m2=tot_shadow_area,
        ground_occlusion_ratio=min(1.0, tot_shadow_area / 100000.0),
        shadow_polygons=shadow_polygons,
    )
