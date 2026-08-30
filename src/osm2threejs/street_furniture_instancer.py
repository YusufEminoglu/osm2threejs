# -*- coding: utf-8 -*-
"""Procedural Street Furniture Instancer (Streetlights, Benches, Hydrants, Bins) for osm2threejs."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Sequence


@dataclass
class StreetFurnitureInstance:
    furniture_id: str
    furniture_type: str  # 'STREET_LIGHT', 'BENCH', 'FIRE_HYDRANT', 'WASTE_BIN', 'BOLLARD'
    position_3d: tuple[float, float, float]
    rotation_degrees: float
    road_side: str  # 'LEFT' or 'RIGHT'


@dataclass
class FurniturePlacementReport:
    total_furniture_count: int
    streetlight_count: int
    bench_count: int
    hydrant_count: int
    waste_bin_count: int
    instances: list[StreetFurnitureInstance]

    def to_threejs_instances(self) -> list[dict[str, Any]]:
        return [
            {
                "id": inst.furniture_id,
                "type": inst.furniture_type,
                "pos": [round(c, 2) for c in inst.position_3d],
                "rot_y": round(inst.rotation_degrees, 1),
                "side": inst.road_side,
            }
            for inst in self.instances
        ]


def instantiate_street_furniture(
    road_centerline_3d: Sequence[tuple[float, float, float]],
    road_width_m: float = 8.0,
    sidewalk_offset_m: float = 1.2,
    streetlight_spacing_m: float = 25.0,
    bench_spacing_m: float = 40.0,
    include_hydrants: bool = True,
) -> FurniturePlacementReport:
    """Populate realistic street furniture instances along road alignments at sidewalk offsets."""
    pts = list(road_centerline_3d)
    if len(pts) < 2:
        return FurniturePlacementReport(0, 0, 0, 0, 0, [])

    # Calculate total length
    seg_lengths = []
    tot_len = 0.0
    for i in range(len(pts) - 1):
        d = math.dist(pts[i], pts[i + 1])
        seg_lengths.append(d)
        tot_len += d

    lateral_offset = (road_width_m / 2.0) + sidewalk_offset_m

    instances: list[StreetFurnitureInstance] = []
    sl_cnt = 0
    bench_cnt = 0
    hyd_cnt = 0
    bin_cnt = 0

    # Interpolate along path
    step = 5.0
    cur_dist = 0.0
    inst_idx = 1

    while cur_dist <= tot_len:
        # Locate segment
        accum = 0.0
        for i, slen in enumerate(seg_lengths):
            if accum + slen >= cur_dist or i == len(seg_lengths) - 1:
                t = (cur_dist - accum) / max(1e-4, slen)
                t = max(0.0, min(1.0, t))
                p1 = pts[i]
                p2 = pts[i + 1]

                cx = p1[0] + t * (p2[0] - p1[0])
                cy = p1[1] + t * (p2[1] - p1[1])
                cz = p1[2] + t * (p2[2] - p1[2])

                dx = p2[0] - p1[0]
                dy = p2[1] - p1[1]
                seg_len = math.hypot(dx, dy)
                if seg_len > 1e-4:
                    # Normal vector perpendicular to road direction
                    nx = -dy / seg_len
                    ny = dx / seg_len
                    heading = math.degrees(math.atan2(dy, dx))

                    # Streetlights (alternating sides)
                    if abs(cur_dist % streetlight_spacing_m) < step * 0.6:
                        side = "RIGHT" if (sl_cnt % 2 == 0) else "LEFT"
                        sign = 1.0 if side == "RIGHT" else -1.0
                        pos = (cx + sign * nx * lateral_offset, cy + sign * ny * lateral_offset, cz)
                        instances.append(
                            StreetFurnitureInstance(
                                furniture_id=f"furn_light_{inst_idx}",
                                furniture_type="STREET_LIGHT",
                                position_3d=pos,
                                rotation_degrees=heading + (90.0 if side == "RIGHT" else -90.0),
                                road_side=side,
                            )
                        )
                        sl_cnt += 1
                        inst_idx += 1

                    # Benches
                    if abs(cur_dist % bench_spacing_m) < step * 0.6 and cur_dist > 5.0:
                        pos = (cx + nx * (lateral_offset + 0.8), cy + ny * (lateral_offset + 0.8), cz)
                        instances.append(
                            StreetFurnitureInstance(
                                furniture_id=f"furn_bench_{inst_idx}",
                                furniture_type="BENCH",
                                position_3d=pos,
                                rotation_degrees=heading - 90.0,
                                road_side="RIGHT",
                            )
                        )
                        bench_cnt += 1
                        inst_idx += 1

                        # Waste bin next to bench
                        pos_bin = (cx + nx * (lateral_offset + 1.2) + dx * 0.05, cy + ny * (lateral_offset + 1.2) + dy * 0.05, cz)
                        instances.append(
                            StreetFurnitureInstance(
                                furniture_id=f"furn_bin_{inst_idx}",
                                furniture_type="WASTE_BIN",
                                position_3d=pos_bin,
                                rotation_degrees=heading,
                                road_side="RIGHT",
                            )
                        )
                        bin_cnt += 1
                        inst_idx += 1
                break
            accum += slen
        cur_dist += step

    # Place fire hydrant near start if requested
    if include_hydrants and len(pts) >= 2:
        p1 = pts[0]
        p2 = pts[1]
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        sl = math.hypot(dx, dy)
        if sl > 1e-4:
            nx = -dy / sl
            ny = dx / sl
            instances.append(
                StreetFurnitureInstance(
                    furniture_id=f"furn_hydrant_1",
                    furniture_type="FIRE_HYDRANT",
                    position_3d=(p1[0] + nx * lateral_offset, p1[1] + ny * lateral_offset, p1[2]),
                    rotation_degrees=0.0,
                    road_side="RIGHT",
                )
            )
            hyd_cnt += 1

    return FurniturePlacementReport(
        total_furniture_count=len(instances),
        streetlight_count=sl_cnt,
        bench_count=bench_cnt,
        hydrant_count=hyd_cnt,
        waste_bin_count=bin_cnt,
        instances=instances,
    )
