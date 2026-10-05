# -*- coding: utf-8 -*-
"""Parametric Procedural 3D Architectural Roof Topologies for osm2threejs."""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from typing import Any, Sequence


class RoofType(str, Enum):
    """Supported 3D architectural roof types."""

    FLAT = "flat"
    GABLED = "gabled"
    HIPPED = "hipped"
    PYRAMIDAL = "pyramidal"
    MANSARD = "mansard"
    SKILLION = "skillion"


@dataclass
class RoofMesh3D:
    """3D Geometry of a procedural architectural roof."""

    roof_type: RoofType
    height: float
    vertices: list[tuple[float, float, float]]  # (x, y, z)
    faces: list[tuple[int, int, int]]  # 0-indexed triangle tuples
    area: float = 0.0
    tilt_degrees: float = 0.0
    azimuth_degrees: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "roof_type": self.roof_type.value,
            "height": round(self.height, 2),
            "vertex_count": len(self.vertices),
            "face_count": len(self.faces),
            "area": round(self.area, 2),
            "tilt_degrees": round(self.tilt_degrees, 1),
            "azimuth_degrees": round(self.azimuth_degrees, 1),
        }


def _compute_polygon_centroid(ring: Sequence[tuple[float, float]]) -> tuple[float, float]:
    """Compute centroid (cx, cy) of a 2D polygon ring."""
    n = len(ring)
    if n == 0:
        return 0.0, 0.0
    cx = sum(p[0] for p in ring) / n
    cy = sum(p[1] for p in ring) / n
    return cx, cy


def _compute_polygon_bbox(ring: Sequence[tuple[float, float]]) -> tuple[float, float, float, float]:
    min_x = min(p[0] for p in ring)
    max_x = max(p[0] for p in ring)
    min_y = min(p[1] for p in ring)
    max_y = max(p[1] for p in ring)
    return min_x, min_y, max_x, max_y


def generate_roof_mesh(
    ring: Sequence[tuple[float, float]],
    base_height: float,
    roof_type: str | RoofType = RoofType.GABLED,
    roof_height: float = 3.0,
    ridge_orientation: float | None = None,
) -> RoofMesh3D:
    """Generate 3D procedural roof geometry on top of a 2D building footprint polygon.

    Args:
        ring: Sequence of (x, y) building footprint perimeter coordinates.
        base_height: Eaves level / top of building wall height (Z).
        roof_type: Roof shape ('flat', 'gabled', 'hipped', 'pyramidal', 'mansard', 'skillion').
        roof_height: Additional peak height of the roof above base_height.
        ridge_orientation: Optional ridge line angle in degrees (0 = East-West, 90 = North-South).

    Returns:
        RoofMesh3D instance containing vertices and triangular faces.
    """
    if isinstance(roof_type, str):
        try:
            r_type = RoofType(roof_type.lower())
        except ValueError:
            r_type = RoofType.GABLED
    else:
        r_type = roof_type

    # Ensure clean non-repeating vertices
    pts = list(ring)
    if len(pts) > 1 and pts[0] == pts[-1]:
        pts = pts[:-1]

    n = len(pts)
    if n < 3:
        # Fallback degenerate
        return RoofMesh3D(
            roof_type=r_type,
            height=0.0,
            vertices=[(p[0], p[1], base_height) for p in pts],
            faces=[],
        )

    cx, cy = _compute_polygon_centroid(pts)
    min_x, min_y, max_x, max_y = _compute_polygon_bbox(pts)
    width = max_x - min_x
    length = max_y - min_y

    vertices: list[tuple[float, float, float]] = []
    faces: list[tuple[int, int, int]] = []

    # 1. Base perimeter ring vertices (indices 0 .. n-1)
    for p in pts:
        vertices.append((p[0], p[1], base_height))

    tilt = 0.0
    azimuth = 0.0

    if r_type == RoofType.FLAT or roof_height <= 0.01:
        # Flat roof: simple fan triangulation from centroid
        c_idx = len(vertices)
        vertices.append((cx, cy, base_height))
        for i in range(n):
            j = (i + 1) % n
            faces.append((i, j, c_idx))
        tilt = 0.0

    elif r_type == RoofType.PYRAMIDAL:
        # Pyramidal: central apex at (cx, cy, base_height + roof_height)
        apex_idx = len(vertices)
        vertices.append((cx, cy, base_height + roof_height))
        for i in range(n):
            j = (i + 1) % n
            faces.append((i, j, apex_idx))
        tilt = math.degrees(math.atan2(roof_height, max(width, length) / 2.0))

    elif r_type == RoofType.SKILLION:
        # Skillion: Monopitch sloping from min_y to max_y
        vertices.clear()
        for p in pts:
            slope_factor = (p[1] - min_y) / max(1e-4, length)
            z = base_height + slope_factor * roof_height
            vertices.append((p[0], p[1], z))
        c_idx = len(vertices)
        vertices.append((cx, cy, base_height + 0.5 * roof_height))
        for i in range(n):
            j = (i + 1) % n
            faces.append((i, j, c_idx))
        tilt = math.degrees(math.atan2(roof_height, max(1e-4, length)))
        azimuth = 180.0

    elif r_type == RoofType.GABLED or r_type == RoofType.HIPPED:
        # Determine ridge direction along longer axis
        is_ew = width >= length
        peak_z = base_height + roof_height

        if r_type == RoofType.GABLED:
            # Two ridge end vertices extending along central axis
            if is_ew:
                r1 = (min_x, cy, peak_z)
                r2 = (max_x, cy, peak_z)
            else:
                r1 = (cx, min_y, peak_z)
                r2 = (cx, max_y, peak_z)

            r1_idx = len(vertices)
            r2_idx = r1_idx + 1
            vertices.append(r1)
            vertices.append(r2)

            for i in range(n):
                j = (i + 1) % n
                # Connect to nearest ridge point or form dual slope
                faces.append((i, j, r1_idx if i < n // 2 else r2_idx))
            tilt = math.degrees(math.atan2(roof_height, min(width, length) / 2.0))

        else:  # HIPPED
            # Shorter central ridge inset by hip offset
            hip_offset = min(width, length) * 0.25
            if is_ew:
                r1 = (min_x + hip_offset, cy, peak_z)
                r2 = (max_x - hip_offset, cy, peak_z)
            else:
                r1 = (cx, min_y + hip_offset, peak_z)
                r2 = (cx, max_y - hip_offset, peak_z)

            r1_idx = len(vertices)
            r2_idx = r1_idx + 1
            vertices.append(r1)
            vertices.append(r2)

            for i in range(n):
                j = (i + 1) % n
                faces.append((i, j, r1_idx if i < n // 2 else r2_idx))
            tilt = math.degrees(math.atan2(roof_height, hip_offset))

    elif r_type == RoofType.MANSARD:
        # Mansard: Steeper lower pitch + flat/shallow upper deck
        inset_factor = 0.25
        deck_z = base_height + roof_height * 0.7
        apex_z = base_height + roof_height

        deck_indices = []
        for p in pts:
            dx = cx + (p[0] - cx) * (1.0 - inset_factor)
            dy = cy + (p[1] - cy) * (1.0 - inset_factor)
            deck_indices.append(len(vertices))
            vertices.append((dx, dy, deck_z))

        # Side faces
        for i in range(n):
            j = (i + 1) % n
            faces.append((i, j, deck_indices[j]))
            faces.append((i, deck_indices[j], deck_indices[i]))

        # Top cap
        apex_idx = len(vertices)
        vertices.append((cx, cy, apex_z))
        for i in range(n):
            j = (i + 1) % n
            faces.append((deck_indices[i], deck_indices[j], apex_idx))
        tilt = 65.0

    # Calculate 3D surface area
    total_area = 0.0
    for f1, f2, f3 in faces:
        v1 = vertices[f1]
        v2 = vertices[f2]
        v3 = vertices[f3]
        # Cross product of edges (v2 - v1) x (v3 - v1)
        e1 = (v2[0] - v1[0], v2[1] - v1[1], v2[2] - v1[2])
        e2 = (v3[0] - v1[0], v3[1] - v1[1], v3[2] - v1[2])
        cross = (
            e1[1] * e2[2] - e1[2] * e2[1],
            e1[2] * e2[0] - e1[0] * e2[2],
            e1[0] * e2[1] - e1[1] * e2[0],
        )
        tri_area = 0.5 * math.sqrt(cross[0] ** 2 + cross[1] ** 2 + cross[2] ** 2)
        total_area += tri_area

    return RoofMesh3D(
        roof_type=r_type,
        height=roof_height,
        vertices=vertices,
        faces=faces,
        area=total_area,
        tilt_degrees=tilt,
        azimuth_degrees=azimuth,
    )
