# -*- coding: utf-8 -*-
"""3D Urban Tree Canopy & Procedural Vegetation Generator for osm2threejs."""

from __future__ import annotations

import enum
import math
from dataclasses import dataclass, field
from typing import Any, Sequence


class TreeType(str, enum.Enum):
    BROADLEAF = "broadleaf"      # Round deciduous canopy
    CONIFER = "conifer"          # Conical evergreen pine
    PALM = "palm"                # Slender trunk with crown fronds
    COLUMNAR = "columnar"        # Narrow tall cypress
    SHRUB = "shrub"              # Low ground bush


@dataclass
class TreeMesh3D:
    """3D procedural mesh representation of a single tree."""

    tree_type: TreeType
    position: tuple[float, float, float]
    height: float
    crown_radius: float
    trunk_radius: float
    vertices: list[tuple[float, float, float]]
    faces: list[tuple[int, int, int]]  # Triangle face index tuples
    foliage_color_hex: str
    trunk_color_hex: str = "#5c4033"


def generate_procedural_tree_mesh(
    x: float,
    y: float,
    z: float = 0.0,
    tree_type: TreeType = TreeType.BROADLEAF,
    height: float = 7.5,
    crown_radius: float = 2.5,
    trunk_radius: float = 0.35,
    foliage_color: str = "#2d6a4f",
) -> TreeMesh3D:
    """Generate 3D triangle vertices and faces for a procedural tree."""
    vertices: list[tuple[float, float, float]] = []
    faces: list[tuple[int, int, int]] = []

    # 1. Trunk Cylinder (4 segments)
    trunk_h = height * 0.40 if tree_type != TreeType.SHRUB else height * 0.15
    t_segs = 6
    # Base ring (z)
    for i in range(t_segs):
        ang = i * (2.0 * math.pi / t_segs)
        vertices.append((x + trunk_radius * math.cos(ang), y + trunk_radius * math.sin(ang), z))
    # Top ring (z + trunk_h)
    for i in range(t_segs):
        ang = i * (2.0 * math.pi / t_segs)
        vertices.append((x + trunk_radius * 0.8 * math.cos(ang), y + trunk_radius * 0.8 * math.sin(ang), z + trunk_h))

    for i in range(t_segs):
        j = (i + 1) % t_segs
        b1, b2 = i, j
        t1, t2 = i + t_segs, j + t_segs
        faces.append((b1, b2, t1))
        faces.append((b2, t2, t1))

    # 2. Crown Canopy Geometry
    crown_base_idx = len(vertices)
    canopy_base_z = z + trunk_h
    canopy_top_z = z + height

    if tree_type in (TreeType.CONIFER, TreeType.COLUMNAR):
        # Conical Cone
        c_segs = 8
        apex_idx = crown_base_idx
        vertices.append((x, y, canopy_top_z))
        for i in range(c_segs):
            ang = i * (2.0 * math.pi / c_segs)
            vertices.append((x + crown_radius * math.cos(ang), y + crown_radius * math.sin(ang), canopy_base_z))
        for i in range(c_segs):
            j = (i + 1) % c_segs
            faces.append((apex_idx, crown_base_idx + 1 + i, crown_base_idx + 1 + j))
    else:
        # Octahedral / Icosphere-like Broadleaf canopy
        c_segs = 8
        mid_z = canopy_base_z + (canopy_top_z - canopy_base_z) * 0.5
        top_idx = crown_base_idx
        bot_idx = crown_base_idx + 1
        vertices.append((x, y, canopy_top_z))  # Top apex
        vertices.append((x, y, canopy_base_z))  # Bottom apex

        ring_start = len(vertices)
        for i in range(c_segs):
            ang = i * (2.0 * math.pi / c_segs)
            vertices.append((x + crown_radius * math.cos(ang), y + crown_radius * math.sin(ang), mid_z))

        for i in range(c_segs):
            j = (i + 1) % c_segs
            r1 = ring_start + i
            r2 = ring_start + j
            faces.append((top_idx, r1, r2))
            faces.append((bot_idx, r2, r1))

    return TreeMesh3D(
        tree_type=tree_type,
        position=(x, y, z),
        height=height,
        crown_radius=crown_radius,
        trunk_radius=trunk_radius,
        vertices=vertices,
        faces=faces,
        foliage_color_hex=foliage_color,
    )


def generate_forest_canopy_mesh(
    tree_points: Sequence[tuple[float, float, float]],
    tree_type: TreeType = TreeType.BROADLEAF,
) -> list[TreeMesh3D]:
    """Generate a batch of 3D tree instances across urban parks or street alignments."""
    meshes: list[TreeMesh3D] = []
    for pt in tree_points:
        z = pt[2] if len(pt) > 2 else 0.0
        meshes.append(generate_procedural_tree_mesh(pt[0], pt[1], z, tree_type=tree_type))
    return meshes
