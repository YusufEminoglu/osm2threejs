# -*- coding: utf-8 -*-
"""3D City Camera Orbit, Flythrough & Cinematic Spline Director for osm2threejs."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Sequence


@dataclass
class CameraKeyframe3D:
    time_seconds: float
    camera_position: tuple[float, float, float]
    look_at_target: tuple[float, float, float]
    field_of_view_deg: float = 60.0


@dataclass
class CinematicFlythroughPath:
    total_duration_seconds: float
    keyframes: list[CameraKeyframe3D]

    def to_json_keyframes(self) -> list[dict[str, Any]]:
        return [
            {
                "time": round(kf.time_seconds, 2),
                "pos": [round(v, 2) for v in kf.camera_position],
                "target": [round(v, 2) for v in kf.look_at_target],
                "fov": round(kf.field_of_view_deg, 1),
            }
            for kf in self.keyframes
        ]


def generate_cinematic_flythrough_path(
    city_center: tuple[float, float, float] = (0.0, 0.0, 0.0),
    orbit_radius: float = 300.0,
    flight_altitude: float = 120.0,
    duration_seconds: float = 30.0,
    num_keyframes: int = 36,
) -> CinematicFlythroughPath:
    """Generate smooth 360-degree orbital flythrough camera keyframes around the 3D urban model."""
    keyframes: list[CameraKeyframe3D] = []
    dt = duration_seconds / max(1, num_keyframes)

    for i in range(num_keyframes + 1):
        t = i * dt
        fraction = i / float(num_keyframes)
        angle_rad = fraction * (2.0 * math.pi)

        # Gentle altitude sinusoid oscillation
        curr_alt = flight_altitude + 20.0 * math.sin(fraction * 4.0 * math.pi)
        cam_x = city_center[0] + orbit_radius * math.cos(angle_rad)
        cam_y = city_center[1] + orbit_radius * math.sin(angle_rad)
        cam_z = city_center[2] + curr_alt

        keyframes.append(
            CameraKeyframe3D(
                time_seconds=t,
                camera_position=(cam_x, cam_y, cam_z),
                look_at_target=city_center,
                field_of_view_deg=55.0,
            )
        )

    return CinematicFlythroughPath(
        total_duration_seconds=duration_seconds,
        keyframes=keyframes,
    )
