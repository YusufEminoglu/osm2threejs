# -*- coding: utf-8 -*-
"""3D City Day/Night Lighting, Streetlamp Placement & Window Emissive Shaders for osm2threejs."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Sequence


@dataclass
class StreetlampInstance:
    position: tuple[float, float, float]
    height_m: float
    color_hex: str  # Warm sodium amber #ffb703 or crisp LED #ffffff
    intensity_lumens: float
    light_radius_m: float


@dataclass
class CityLightingRig:
    """Master lighting rig configuration for Three.js scene."""

    is_night_mode: bool
    ambient_light_color: str
    ambient_intensity: float
    directional_sun_color: str
    sun_position: tuple[float, float, float]
    fog_color: str
    fog_density: float
    streetlamps: list[StreetlampInstance]

    def to_dict(self) -> dict[str, Any]:
        return {
            "night_mode": self.is_night_mode,
            "ambient_color": self.ambient_light_color,
            "ambient_intensity": self.ambient_intensity,
            "sun_position": self.sun_position,
            "streetlamps_count": len(self.streetlamps),
        }


def generate_night_city_effects(
    road_centerlines: Sequence[Sequence[tuple[float, float, float] | tuple[float, float]]],
    lamp_interval_meters: float = 30.0,
    lamp_height: float = 6.5,
    lamp_color: str = "#ffb703",
) -> CityLightingRig:
    """Generate realistic nocturnal city lighting with automatic streetlamp placements along road polylines."""
    lamps: list[StreetlampInstance] = []

    for line in road_centerlines:
        n = len(line)
        if n < 2:
            continue
        accum_dist = 0.0
        for i in range(n - 1):
            p1 = line[i]
            p2 = line[i + 1]
            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]
            seg_len = math.hypot(dx, dy)
            if seg_len <= 1e-4:
                continue

            num_lamps = int(seg_len / lamp_interval_meters)
            for k in range(num_lamps):
                t = (k + 0.5) / max(1, num_lamps)
                lx = p1[0] + dx * t
                ly = p1[1] + dy * t
                lz = (p1[2] if len(p1) > 2 else 0.0) + lamp_height
                lamps.append(
                    StreetlampInstance(
                        position=(lx, ly, lz),
                        height_m=lamp_height,
                        color_hex=lamp_color,
                        intensity_lumens=4500.0,
                        light_radius_m=18.0,
                    )
                )

    return CityLightingRig(
        is_night_mode=True,
        ambient_light_color="#0a0e17",
        ambient_intensity=0.15,
        directional_sun_color="#1d2d44",  # Moonlight tint
        sun_position=(-200.0, 300.0, 150.0),
        fog_color="#050811",
        fog_density=0.0015,
        streetlamps=lamps,
    )
