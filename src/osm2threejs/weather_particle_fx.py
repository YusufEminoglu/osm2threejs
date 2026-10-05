# -*- coding: utf-8 -*-
"""3D Atmospheric Weather Particle FX (Rain, Snow, Fog) for osm2threejs."""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from typing import Any


class WeatherType(str, Enum):
    RAIN = "RAIN"
    HEAVY_STORM = "HEAVY_STORM"
    SNOW = "SNOW"
    FOG = "FOG"


@dataclass
class WeatherParticleFX:
    weather_type: WeatherType
    particle_count: int
    fall_velocity_ms: float
    wind_vector_3d: tuple[float, float, float]
    particle_color_hex: str
    bounding_box_size_m: tuple[float, float, float] = (500.0, 500.0, 150.0)

    def to_threejs_config(self) -> dict[str, Any]:
        return {
            "type": self.weather_type.value,
            "count": self.particle_count,
            "velocity": self.fall_velocity_ms,
            "wind": list(self.wind_vector_3d),
            "color": self.particle_color_hex,
            "box": list(self.bounding_box_size_m),
        }


def generate_weather_particle_system(
    weather_type: WeatherType | str = WeatherType.RAIN,
    intensity: float = 1.0,  # 0.1 (light) to 3.0 (extreme)
    wind_speed_ms: float = 5.0,
    wind_direction_deg: float = 45.0,
) -> WeatherParticleFX:
    """Configure dynamic GPU particle system for atmospheric weather simulations."""
    if isinstance(weather_type, str):
        try:
            w_type = WeatherType(weather_type.upper())
        except ValueError:
            w_type = WeatherType.RAIN
    else:
        w_type = weather_type

    rad = math.radians(wind_direction_deg)
    wx = wind_speed_ms * math.cos(rad)
    wy = wind_speed_ms * math.sin(rad)

    if w_type == WeatherType.RAIN:
        p_count = int(12000 * intensity)
        fall_v = 18.0 * math.sqrt(intensity)
        color = "#a5b4fc"
        wz = -fall_v
    elif w_type == WeatherType.HEAVY_STORM:
        p_count = int(25000 * intensity)
        fall_v = 28.0 * math.sqrt(intensity)
        color = "#94a3b8"
        wz = -fall_v
    elif w_type == WeatherType.SNOW:
        p_count = int(8000 * intensity)
        fall_v = 2.5
        color = "#ffffff"
        wz = -fall_v
    else:  # FOG
        p_count = int(4000 * intensity)
        fall_v = 0.2
        color = "#cbd5e1"
        wz = -0.1

    return WeatherParticleFX(
        weather_type=w_type,
        particle_count=p_count,
        fall_velocity_ms=fall_v,
        wind_vector_3d=(round(wx, 2), round(wy, 2), round(wz, 2)),
        particle_color_hex=color,
    )
