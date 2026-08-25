# -*- coding: utf-8 -*-
"""
osm2threejs — Pure-Python 3D City Generator from OpenStreetMap into Three.js WebGL & 3D Assets.
"""

from __future__ import annotations

__version__ = "0.1.0"
__author__ = "Yusuf Eminoğlu"

from .bundler import (
    StandaloneHtmlBundler,
    bundle_city_to_html,
)
from .exporters import (
    export_to_dxf_3d,
    export_to_geojson_3d,
    export_to_glb,
    export_to_obj,
)
from .fetcher import (
    BoundingBox,
    OsmDataFetcher,
    geocode_place_name,
    query_overpass,
)
from .geometry import (
    BuildingMesh,
    CityModel3D,
    RoadMesh,
    TreeInstance,
    WaterMesh,
    generate_3d_city,
)
from .themes import (
    ColorTheme,
    ThemePalette,
    get_theme,
    list_theme_names,
)


def from_bbox(
    bbox: tuple[float, float, float, float] | BoundingBox,
    theme: str = "Editorial Paper",
    name: str = "3D City Model",
    default_building_levels: int = 3,
) -> CityModel3D:
    """Fetch OpenStreetMap data for a bounding box and generate a procedural 3D City Model.

    Args:
        bbox: (min_lon, min_lat, max_lon, max_lat) tuple or BoundingBox.
        theme: Name of the visual theme (e.g. 'Editorial Paper', 'Cyberpunk Neon', 'Blueprint').
        name: Name of the city model.
        default_building_levels: Default floor count when OSM has no level data (default: 3).

    Returns:
        CityModel3D instance with 3D buildings, roads, water, greenery, and exporters.
    """
    if isinstance(bbox, (list, tuple)):
        b = BoundingBox(min_lon=bbox[0], min_lat=bbox[1], max_lon=bbox[2], max_lat=bbox[3])
    else:
        b = bbox

    fetcher = OsmDataFetcher()
    osm_data = fetcher.fetch_bbox(b)
    return generate_3d_city(
        osm_data, bbox=b, theme=theme, name=name, default_levels=default_building_levels
    )


def from_place(
    place_name: str,
    theme: str = "Editorial Paper",
    radius_meters: float = 500.0,
    default_building_levels: int = 3,
) -> CityModel3D:
    """Geocode a place name (e.g. 'Kadıköy, İstanbul' or 'Eiffel Tower, Paris') and build a 3D City Model.

    Args:
        place_name: Location query string to geocode via Nominatim.
        theme: Name of the visual theme.
        radius_meters: Radius around the geocoded center point in meters (default: 500m).
        default_building_levels: Default floor count (default: 3).

    Returns:
        CityModel3D instance.
    """
    bbox = geocode_place_name(place_name, radius_meters=radius_meters)
    return from_bbox(
        bbox, theme=theme, name=place_name, default_building_levels=default_building_levels
    )


def from_geojson(
    geojson_data: dict | str,
    theme: str = "Editorial Paper",
    name: str = "Custom 3D City",
    default_building_levels: int = 3,
) -> CityModel3D:
    """Generate a 3D City Model directly from parsed or raw GeoJSON feature collections."""
    return generate_3d_city(
        geojson_data, theme=theme, name=name, default_levels=default_building_levels
    )


def list_themes() -> list[str]:
    """List all 12 available visual color themes."""
    return list_theme_names()


__all__ = [
    "__version__",
    "from_bbox",
    "from_place",
    "from_geojson",
    "list_themes",
    "BoundingBox",
    "CityModel3D",
    "BuildingMesh",
    "RoadMesh",
    "WaterMesh",
    "TreeInstance",
    "ColorTheme",
    "ThemePalette",
    "get_theme",
    "list_theme_names",
    "OsmDataFetcher",
    "geocode_place_name",
    "query_overpass",
    "generate_3d_city",
    "bundle_city_to_html",
    "StandaloneHtmlBundler",
    "export_to_glb",
    "export_to_obj",
    "export_to_geojson_3d",
    "export_to_dxf_3d",
]
