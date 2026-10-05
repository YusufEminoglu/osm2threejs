# -*- coding: utf-8 -*-
"""Acoustic Highway Noise Barrier & Soundwall Extrusion Engine for osm2threejs."""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from typing import Any, Sequence


class AcousticPanelMaterial(str, Enum):
    TRANSPARENT_PMMA = "TRANSPARENT_PMMA"  # Clear acrylic / plexiglass
    PERFORATED_ALUMINUM = "PERFORATED_ALUMINUM"
    POROUS_CONCRETE = "POROUS_CONCRETE"
    TIMBER_REFLECTIVE = "TIMBER_REFLECTIVE"


@dataclass
class NoiseBarrierMesh3D:
    barrier_id: str
    material: AcousticPanelMaterial
    height_m: float
    total_barrier_length_m: float
    wall_quad_faces_count: int
    steel_post_locations: list[tuple[float, float, float]]
    sound_transmission_class_stc_db: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "barrier_id": self.barrier_id,
            "material": self.material.value,
            "height_m": round(self.height_m, 2),
            "length_m": round(self.total_barrier_length_m, 1),
            "quad_faces": self.wall_quad_faces_count,
            "posts_count": len(self.steel_post_locations),
            "stc_db": round(self.sound_transmission_class_stc_db, 1),
        }


def generate_3d_noise_barrier_mesh(
    barrier_path_3d: Sequence[tuple[float, float, float]],
    barrier_id: str = "Soundwall_Corridor",
    barrier_height_m: float = 3.5,
    post_spacing_m: float = 4.0,
    material: AcousticPanelMaterial = AcousticPanelMaterial.TRANSPARENT_PMMA,
) -> NoiseBarrierMesh3D:
    """Extrude acoustic noise barrier soundwalls along highway edges with vertical structural steel H-beams."""
    pts = list(barrier_path_3d)
    if len(pts) < 2:
        return NoiseBarrierMesh3D(barrier_id, material, barrier_height_m, 0.0, 0, [], 0.0)

    tot_len = 0.0
    for i in range(len(pts) - 1):
        tot_len += math.dist(pts[i], pts[i + 1])

    # Sound transmission class (STC in dB) by material
    stc_map = {
        AcousticPanelMaterial.TRANSPARENT_PMMA: 32.0,
        AcousticPanelMaterial.PERFORATED_ALUMINUM: 36.0,
        AcousticPanelMaterial.POROUS_CONCRETE: 42.0,
        AcousticPanelMaterial.TIMBER_REFLECTIVE: 28.0,
    }
    stc = stc_map.get(material, 30.0)

    posts: list[tuple[float, float, float]] = []

    for p in pts:
        posts.append((round(p[0], 2), round(p[1], 2), round(p[2], 2)))

    quad_faces = (len(pts) - 1) * 2  # Front and back vertical faces

    return NoiseBarrierMesh3D(
        barrier_id=barrier_id,
        material=material,
        height_m=barrier_height_m,
        total_barrier_length_m=tot_len,
        wall_quad_faces_count=quad_faces,
        steel_post_locations=posts,
        sound_transmission_class_stc_db=stc,
    )
