# -*- coding: utf-8 -*-
"""3D Procedural Traffic Vehicle Stream & Animated Headlight Trails for osm2threejs."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Sequence


@dataclass
class TrafficVehicle3D:
    vehicle_id: str
    vehicle_type: str  # 'sedan', 'bus', 'truck'
    position_3d: tuple[float, float, float]
    heading_degrees: float
    speed_kmh: float
    color_hex: str = "#e11d48"
    length_m: float = 4.5
    width_m: float = 1.8
    height_m: float = 1.4


@dataclass
class TrafficSimulationMesh:
    road_id: str
    total_vehicles: int
    mean_speed_kmh: float
    vehicles: list[TrafficVehicle3D]

    def to_threejs_instances(self) -> list[dict[str, Any]]:
        return [
            {
                "id": v.vehicle_id,
                "type": v.vehicle_type,
                "pos": [round(c, 2) for c in v.position_3d],
                "heading": round(v.heading_degrees, 1),
                "dims": [v.length_m, v.width_m, v.height_m],
                "color": v.color_hex,
            }
            for v in self.vehicles
        ]


def generate_traffic_flow_geometry(
    road_centerline_3d: Sequence[tuple[float, float, float]],
    traffic_density_per_km: float = 25.0,
    flow_speed_kmh: float = 50.0,
    road_id: str = "road_primary_1",
) -> TrafficSimulationMesh:
    """Populate 3D vehicles along road centerline splines with directional orientation."""
    pts = list(road_centerline_3d)
    if len(pts) < 2:
        return TrafficSimulationMesh(road_id, 0, 0.0, [])

    # Calculate total length of road spline
    seg_lengths = []
    tot_len = 0.0
    for i in range(len(pts) - 1):
        d = math.dist(pts[i], pts[i + 1])
        seg_lengths.append(d)
        tot_len += d

    num_vehicles = max(1, int((tot_len / 1000.0) * traffic_density_per_km))
    spacing = tot_len / max(1, num_vehicles)

    vehicles: list[TrafficVehicle3D] = []
    palette = ["#3b82f6", "#ef4444", "#10b981", "#f59e0b", "#ffffff", "#334155"]

    for v_idx in range(num_vehicles):
        target_dist = (v_idx * spacing) % tot_len

        # Locate segment
        accum = 0.0
        for i, slen in enumerate(seg_lengths):
            if accum + slen >= target_dist or i == len(seg_lengths) - 1:
                t = (target_dist - accum) / max(1e-4, slen)
                t = max(0.0, min(1.0, t))
                p1 = pts[i]
                p2 = pts[i + 1]

                vx = p1[0] + t * (p2[0] - p1[0])
                vy = p1[1] + t * (p2[1] - p1[1])
                vz = p1[2] + t * (p2[2] - p1[2]) + 0.7  # Centered at vehicle mid-height

                dx = p2[0] - p1[0]
                dy = p2[1] - p1[1]
                heading = math.degrees(math.atan2(dy, dx))

                v_type = "bus" if (v_idx % 8 == 0) else "sedan"
                v_len = 11.5 if v_type == "bus" else 4.5
                v_h = 3.2 if v_type == "bus" else 1.4

                vehicles.append(
                    TrafficVehicle3D(
                        vehicle_id=f"veh_{road_id}_{v_idx+1}",
                        vehicle_type=v_type,
                        position_3d=(vx, vy, vz),
                        heading_degrees=heading,
                        speed_kmh=flow_speed_kmh,
                        color_hex=palette[v_idx % len(palette)],
                        length_m=v_len,
                        height_m=v_h,
                    )
                )
                break
            accum += slen

    return TrafficSimulationMesh(
        road_id=road_id,
        total_vehicles=len(vehicles),
        mean_speed_kmh=flow_speed_kmh,
        vehicles=vehicles,
    )
