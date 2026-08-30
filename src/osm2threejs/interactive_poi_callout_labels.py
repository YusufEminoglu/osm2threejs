# -*- coding: utf-8 -*-
"""3D Projected Screen-Space Landmark POI Callout Labels & Leader Lines for osm2threejs."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Sequence


@dataclass
class CalloutPin3D:
    poi_id: str
    label_text: str
    category: str  # "LANDMARK", "TRANSIT", "CIVIC", "COMMERCIAL"
    world_position_3d: tuple[float, float, float]
    pin_color_hex: str = "#3b82f6"
    vertical_stem_height_m: float = 12.0


@dataclass
class POICalloutSet:
    city_name: str
    pins: list[CalloutPin3D]

    def to_threejs_overlay_json(self) -> dict[str, Any]:
        return {
            "city": self.city_name,
            "total_pins": len(self.pins),
            "pins": [
                {
                    "id": p.poi_id,
                    "label": p.label_text,
                    "cat": p.category,
                    "pos": list(p.world_position_3d),
                    "color": p.pin_color_hex,
                    "stem_h": p.vertical_stem_height_m,
                }
                for p in self.pins
            ],
        }


def generate_3d_poi_callouts(
    landmarks_data: Sequence[dict[str, Any]],
    city_name: str = "Metropolis 3D",
) -> POICalloutSet:
    """Generate 3D callout marker pins with vertical leader stems and screen-space tracking labels."""
    pins: list[CalloutPin3D] = []

    for item in landmarks_data:
        pos = item.get("position", (0.0, 0.0, 0.0))
        if len(pos) == 2:
            pos_3d = (float(pos[0]), float(pos[1]), 0.0)
        else:
            pos_3d = (float(pos[0]), float(pos[1]), float(pos[2]))

        pins.append(
            CalloutPin3D(
                poi_id=str(item.get("id", f"poi_{len(pins)+1}")),
                label_text=str(item.get("name", "Landmark")),
                category=str(item.get("category", "LANDMARK")),
                world_position_3d=pos_3d,
                pin_color_hex=str(item.get("color", "#ef4444")),
                vertical_stem_height_m=float(item.get("height_m", 15.0)),
            )
        )

    return POICalloutSet(
        city_name=city_name,
        pins=pins,
    )
