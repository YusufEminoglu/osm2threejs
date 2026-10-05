# -*- coding: utf-8 -*-
"""3D Subsurface Tunnel Tube & Portal Geometry Generator for osm2threejs."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Sequence


@dataclass
class TunnelGeometry3D:
    tunnel_id: str
    vertices: list[tuple[float, float, float]]
    faces: list[tuple[int, int, int]]
    normals: list[tuple[float, float, float]]
    tunnel_length_m: float
    inner_radius_m: float
    tunnel_color_hex: str = "#475569"
    invert_road_deck_z: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "tunnel_id": self.tunnel_id,
            "length_m": round(self.tunnel_length_m, 1),
            "radius_m": self.inner_radius_m,
            "vertex_count": len(self.vertices),
            "face_count": len(self.faces),
        }


def generate_3d_tunnel_mesh(
    tunnel_centerline_3d: Sequence[tuple[float, float, float]],
    tunnel_id: str = "tunnel_main",
    tunnel_radius_m: float = 4.5,
    radial_segments: int = 12,
    subsurface_depth_offset_m: float = -15.0,
) -> TunnelGeometry3D:
    """Extrude parametric horseshoe/cylindrical tunnel cross-sections along 3D subsurface path."""
    pts = list(tunnel_centerline_3d)
    if len(pts) < 2:
        return TunnelGeometry3D(tunnel_id, [], [], [], 0.0, tunnel_radius_m)

    # Offset path into subsurface
    sub_pts = [(p[0], p[1], p[2] + subsurface_depth_offset_m) for p in pts]

    vertices: list[tuple[float, float, float]] = []
    normals: list[tuple[float, float, float]] = []
    faces: list[tuple[int, int, int]] = []

    tot_len = 0.0
    for i in range(len(sub_pts) - 1):
        tot_len += math.dist(sub_pts[i], sub_pts[i + 1])

    # Generate rings of vertices along centerline
    for i, pt in enumerate(sub_pts):
        # Calculate forward tangent vector
        if i < len(sub_pts) - 1:
            p_next = sub_pts[i + 1]
            dx = p_next[0] - pt[0]
            dy = p_next[1] - pt[1]
            dz = p_next[2] - pt[2]
        else:
            p_prev = sub_pts[i - 1]
            dx = pt[0] - p_prev[0]
            dy = pt[1] - p_prev[1]
            dz = pt[2] - p_prev[2]

        fwd_len = math.hypot(dx, dy, dz)
        tx, ty, tz = (dx / max(1e-4, fwd_len), dy / max(1e-4, fwd_len), dz / max(1e-4, fwd_len))

        # Lateral normal perpendicular in XY plane
        nx = -ty
        ny = tx
        nz = 0.0

        # Binormal (vertical)
        bx = ny * tz - nz * ty
        by = nz * tx - nx * tz
        bz = nx * ty - ny * tx
        b_len = math.hypot(bx, by, bz)
        bx, by, bz = (bx / max(1e-4, b_len), by / max(1e-4, b_len), bz / max(1e-4, b_len))

        # Parametric Horseshoe arch: theta from 0 to 2*pi
        for seg in range(radial_segments):
            angle = (2.0 * math.pi * seg) / radial_segments
            cos_th = math.cos(angle)
            sin_th = math.sin(angle)

            vx = pt[0] + tunnel_radius_m * (nx * cos_th + bx * sin_th)
            vy = pt[1] + tunnel_radius_m * (ny * cos_th + by * sin_th)
            vz = pt[2] + tunnel_radius_m * (nz * cos_th + bz * sin_th)

            vertices.append((vx, vy, vz))
            normals.append((nx * cos_th, ny * cos_th, bz * sin_th))

    # Stitch adjacent rings into quad/tri faces
    num_rings = len(sub_pts)
    for r in range(num_rings - 1):
        ring_start = r * radial_segments
        next_ring_start = (r + 1) * radial_segments
        for s in range(radial_segments):
            next_s = (s + 1) % radial_segments

            v0 = ring_start + s
            v1 = ring_start + next_s
            v2 = next_ring_start + next_s
            v3 = next_ring_start + s

            faces.append((v0, v1, v2))
            faces.append((v0, v2, v3))

    return TunnelGeometry3D(
        tunnel_id=tunnel_id,
        vertices=vertices,
        faces=faces,
        normals=normals,
        tunnel_length_m=tot_len,
        inner_radius_m=tunnel_radius_m,
        invert_road_deck_z=sub_pts[0][2] - (tunnel_radius_m * 0.7),
    )
