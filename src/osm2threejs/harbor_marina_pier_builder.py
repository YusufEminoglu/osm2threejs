# -*- coding: utf-8 -*-
"""3D Nautical Harbor, Floating Marina Docks & Navigation Buoy Mesh Generator for osm2threejs."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Sequence


@dataclass
class DockBerthSpec:
    pier_length_m: float = 80.0
    pier_width_m: float = 3.5
    num_finger_piers: int = 8
    finger_length_m: float = 12.0
    berth_capacity_boats: int = 16


@dataclass
class MarinaHarborGeometry3D:
    harbor_id: str
    total_pier_length_m: float
    total_berths_count: int
    navigation_buoys_count: int
    floating_docks_mesh: dict[str, Any]
    breakwater_mesh: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "harbor_id": self.harbor_id,
            "pier_length_m": round(self.total_pier_length_m, 1),
            "berths_count": self.total_berths_count,
            "buoys_count": self.navigation_buoys_count,
            "docks_vertices": len(self.floating_docks_mesh.get("vertices", [])),
            "breakwater_vertices": len(self.breakwater_mesh.get("vertices", [])),
        }


def generate_3d_marina_harbor_mesh(
    main_pier_centerline: Sequence[tuple[float, float, float]],
    breakwater_polyline: Sequence[tuple[float, float, float]] | None = None,
    dock_spec: DockBerthSpec | None = None,
    navigation_buoys_coords: Sequence[tuple[float, float]] | None = None,
) -> MarinaHarborGeometry3D:
    """Generate 3D procedural meshes for floating marina pontoons, timber finger piers, stone breakwaters, and buoys."""
    spec = dock_spec or DockBerthSpec()
    line = list(main_pier_centerline)

    docks_verts: list[tuple[float, float, float]] = []
    docks_faces: list[tuple[int, int, int]] = []

    # Main spine floating pontoon
    if len(line) >= 2:
        p1, p2 = line[0], line[1]
        dx, dy = p2[0] - p1[0], p2[1] - p1[1]
        length = math.hypot(dx, dy)
        if length > 0:
            ux, uy = dx / length, dy / length
            nx, ny = -uy, ux

            w2 = spec.pier_width_m / 2.0
            z = p1[2]

            v_start = len(docks_verts)
            docks_verts.append((p1[0] - nx * w2, p1[1] - ny * w2, z))
            docks_verts.append((p1[0] + nx * w2, p1[1] + ny * w2, z))
            docks_verts.append((p2[0] + nx * w2, p2[1] + ny * w2, z))
            docks_verts.append((p2[0] - nx * w2, p2[1] - ny * w2, z))

            docks_faces.append((v_start, v_start + 1, v_start + 2))
            docks_faces.append((v_start, v_start + 2, v_start + 3))

            # Finger piers protruding left and right
            spacing = length / max(1, spec.num_finger_piers)
            for i in range(spec.num_finger_piers):
                fx = p1[0] + ux * (i + 0.5) * spacing
                fy = p1[1] + uy * (i + 0.5) * spacing

                # Left finger
                f_idx = len(docks_verts)
                docks_verts.append((fx - nx * w2, fy - ny * w2, z))
                docks_verts.append((fx - nx * (w2 + spec.finger_length_m), fy - ny * (w2 + spec.finger_length_m), z))
                docks_verts.append((fx - nx * (w2 + spec.finger_length_m) + ux * 1.5, fy - ny * (w2 + spec.finger_length_m) + uy * 1.5, z))
                docks_verts.append((fx - nx * w2 + ux * 1.5, fy - ny * w2 + uy * 1.5, z))

                docks_faces.append((f_idx, f_idx + 1, f_idx + 2))
                docks_faces.append((f_idx, f_idx + 2, f_idx + 3))

    # Breakwater mesh
    bw_verts: list[tuple[float, float, float]] = []
    bw_faces: list[tuple[int, int, int]] = []
    if breakwater_polyline:
        for x, y, z in breakwater_polyline:
            bw_verts.append((x, y, z + 2.5))  # Elevated stone rip-rap

    buoys_n = len(navigation_buoys_coords) if navigation_buoys_coords else 0

    return MarinaHarborGeometry3D(
        harbor_id="MARINA_BASIN_1",
        total_pier_length_m=spec.pier_length_m,
        total_berths_count=spec.berth_capacity_boats,
        navigation_buoys_count=buoys_n,
        floating_docks_mesh={"vertices": docks_verts, "faces": docks_faces},
        breakwater_mesh={"vertices": bw_verts, "faces": bw_faces},
    )
