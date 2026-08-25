# -*- coding: utf-8 -*-
"""Visual themes, color palettes, and material specifications for osm2threejs."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ThemePalette:
    """Color palette and material parameters for a 3D city scene."""

    name: str
    island_color: str
    terrain_outside_color: str
    terrain_side_color: str
    road_color: str
    park_color: str
    sport_color: str
    water_color: str
    building_wall_color: str
    building_roof_color: str
    roof_texture: str
    asset_theme: str
    lighting_preset: str
    background_color: str = "#0d1117"
    fog_color: str = "#161b22"
    fog_density: float = 0.0015

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "islandColor": self.island_color,
            "terrainOutsideColor": self.terrain_outside_color,
            "terrainSideColor": self.terrain_side_color,
            "roadColor": self.road_color,
            "parkColor": self.park_color,
            "sportColor": self.sport_color,
            "waterColor": self.water_color,
            "buildingWallColor": self.building_wall_color,
            "buildingRoofColor": self.building_roof_color,
            "roofTexture": self.roof_texture,
            "assetTheme": self.asset_theme,
            "lightingPreset": self.lighting_preset,
            "backgroundColor": self.background_color,
            "fogColor": self.fog_color,
            "fogDensity": self.fog_density,
        }


# 12 Curated Master Themes
_THEME_CATALOG: dict[str, ThemePalette] = {
    "Editorial Paper": ThemePalette(
        name="Editorial Paper",
        island_color="#e6dfd3",
        terrain_outside_color="#fdfbf7",
        terrain_side_color="#b9aa96",
        road_color="#7c5c43",
        park_color="#c2c5aa",
        sport_color="#aeb89a",
        water_color="#9ab8c2",
        building_wall_color="#f4ede2",
        building_roof_color="#c9b9a6",
        roof_texture="RoofA",
        asset_theme="Civic Heritage",
        lighting_preset="warm_sun",
        background_color="#f5f2eb",
        fog_color="#e8e2d5",
        fog_density=0.001,
    ),
    "Cyberpunk Neon": ThemePalette(
        name="Cyberpunk Neon",
        island_color="#0f172a",
        terrain_outside_color="#090d16",
        terrain_side_color="#1e293b",
        road_color="#334155",
        park_color="#064e3b",
        sport_color="#047857",
        water_color="#0284c7",
        building_wall_color="#1e1e38",
        building_roof_color="#ec4899",
        roof_texture="NeonGrid",
        asset_theme="Cyberpunk",
        lighting_preset="night_glow",
        background_color="#08071a",
        fog_color="#120e2e",
        fog_density=0.002,
    ),
    "Blueprint Architectural": ThemePalette(
        name="Blueprint Architectural",
        island_color="#0f2b48",
        terrain_outside_color="#091b2e",
        terrain_side_color="#163c63",
        road_color="#1b4975",
        park_color="#1d5b8a",
        sport_color="#20699f",
        water_color="#38bdf8",
        building_wall_color="#1e3a5f",
        building_roof_color="#60a5fa",
        roof_texture="BlueprintGrid",
        asset_theme="Monochrome",
        lighting_preset="cyan_glow",
        background_color="#0b192c",
        fog_color="#0f2b48",
        fog_density=0.0015,
    ),
    "Anime Pastel": ThemePalette(
        name="Anime Pastel",
        island_color="#e9f1e4",
        terrain_outside_color="#eef5ec",
        terrain_side_color="#b9d0c0",
        road_color="#7d8a96",
        park_color="#7fc785",
        sport_color="#6fb8a0",
        water_color="#68b0d8",
        building_wall_color="#fffaf0",
        building_roof_color="#f472b6",
        roof_texture="CeramicLight",
        asset_theme="Coastal Light",
        lighting_preset="soft_bloom",
        background_color="#f0f9ff",
        fog_color="#e0f2fe",
        fog_density=0.0008,
    ),
    "Dark Glow": ThemePalette(
        name="Dark Glow",
        island_color="#18181b",
        terrain_outside_color="#09090b",
        terrain_side_color="#27272a",
        road_color="#3f3f46",
        park_color="#14532d",
        sport_color="#166534",
        water_color="#0369a1",
        building_wall_color="#27272a",
        building_roof_color="#e11d48",
        roof_texture="DarkShingle",
        asset_theme="Night Minimal",
        lighting_preset="amber_night",
        background_color="#09090b",
        fog_color="#18181b",
        fog_density=0.002,
    ),
    "Warm Sand & Slate": ThemePalette(
        name="Warm Sand & Slate",
        island_color="#e8ddc7",
        terrain_outside_color="#efe7d4",
        terrain_side_color="#c2a878",
        road_color="#46413a",
        park_color="#8aa05e",
        sport_color="#7a9050",
        water_color="#608b98",
        building_wall_color="#f3ede2",
        building_roof_color="#c27d53",
        roof_texture="GermanTile",
        asset_theme="Modern Urban",
        lighting_preset="sunset",
        background_color="#f8f4eb",
        fog_color="#ede4d3",
        fog_density=0.001,
    ),
    "Teal & Salmon": ThemePalette(
        name="Teal & Salmon",
        island_color="#e7d7d0",
        terrain_outside_color="#dfeae7",
        terrain_side_color="#4f8c84",
        road_color="#2f4a46",
        park_color="#5e9e7e",
        sport_color="#4f8e70",
        water_color="#388e85",
        building_wall_color="#fdf4f0",
        building_roof_color="#fb7185",
        roof_texture="StandingSeam",
        asset_theme="Modern Urban",
        lighting_preset="clear_day",
        background_color="#f4f8f7",
        fog_color="#e5efe9",
        fog_density=0.001,
    ),
    "Light Purple & Black": ThemePalette(
        name="Light Purple & Black",
        island_color="#e7e2f0",
        terrain_outside_color="#efecf6",
        terrain_side_color="#9b8fb0",
        road_color="#2a2a30",
        park_color="#8a9e6e",
        sport_color="#7a8e60",
        water_color="#7a8eb8",
        building_wall_color="#faf7fc",
        building_roof_color="#a855f7",
        roof_texture="USShingle",
        asset_theme="Modern Urban",
        lighting_preset="twilight",
        background_color="#f8f6fc",
        fog_color="#eae5f2",
        fog_density=0.0012,
    ),
    "Tinted Gray Teal": ThemePalette(
        name="Tinted Gray Teal",
        island_color="#dde6e3",
        terrain_outside_color="#e6efec",
        terrain_side_color="#7fb0a8",
        road_color="#36433f",
        park_color="#6fa589",
        sport_color="#5f9579",
        water_color="#4f8f87",
        building_wall_color="#f0f5f3",
        building_roof_color="#0d9488",
        roof_texture="StandingSeam",
        asset_theme="Modern Urban",
        lighting_preset="morning",
        background_color="#f0f6f4",
        fog_color="#e0eae6",
        fog_density=0.001,
    ),
    "Cartoon Stylized": ThemePalette(
        name="Cartoon Stylized",
        island_color="#fbe7c6",
        terrain_outside_color="#fdf1da",
        terrain_side_color="#d9b98a",
        road_color="#4a4540",
        park_color="#5fbf57",
        sport_color="#4fae87",
        water_color="#45b0e6",
        building_wall_color="#ffffff",
        building_roof_color="#f97316",
        roof_texture="CartoonTile",
        asset_theme="Cartoon",
        lighting_preset="vibrant_sun",
        background_color="#fffbeb",
        fog_color="#fef3c7",
        fog_density=0.0005,
    ),
    "Monochrome Clay": ThemePalette(
        name="Monochrome Clay",
        island_color="#e5e5e5",
        terrain_outside_color="#f5f5f5",
        terrain_side_color="#a3a3a3",
        road_color="#737373",
        park_color="#a3a3a3",
        sport_color="#8c8c8c",
        water_color="#525252",
        building_wall_color="#f5f5f5",
        building_roof_color="#d4d4d4",
        roof_texture="ClayFlat",
        asset_theme="Sculpture",
        lighting_preset="studio_key",
        background_color="#ffffff",
        fog_color="#e5e5e5",
        fog_density=0.001,
    ),
    "Realistic Satellite": ThemePalette(
        name="Realistic Satellite",
        island_color="#4b5563",
        terrain_outside_color="#374151",
        terrain_side_color="#1f2937",
        road_color="#1f2937",
        park_color="#15803d",
        sport_color="#166534",
        water_color="#1e3a8a",
        building_wall_color="#d1d5db",
        building_roof_color="#b91c1c",
        roof_texture="RealTile",
        asset_theme="Photoreal",
        lighting_preset="noon_direct",
        background_color="#111827",
        fog_color="#1f2937",
        fog_density=0.0012,
    ),
}

ColorTheme = ThemePalette


def get_theme(name: str = "Editorial Paper") -> ThemePalette:
    """Retrieve theme palette by name with fuzzy fallback."""
    if name in _THEME_CATALOG:
        return _THEME_CATALOG[name]
    for k, v in _THEME_CATALOG.items():
        if k.lower() == name.lower():
            return v
    return _THEME_CATALOG["Editorial Paper"]


def list_theme_names() -> list[str]:
    """List all registered theme names."""
    return list(_THEME_CATALOG.keys())
