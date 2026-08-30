# -*- coding: utf-8 -*-
"""
osm2threejs — Pure-Python 3D City Generator from OpenStreetMap into Three.js WebGL & 3D Assets.
"""

from __future__ import annotations

__version__ = "0.9.0"
__author__ = "Yusuf Eminoğlu"

from .billboard_lod_manager import (
    BuildingLODSet,
    LODDistanceConfig,
    generate_lod_building_levels,
)
from .bundler import (
    StandaloneHtmlBundler,
    bundle_city_to_html,
)
from .camera_director import (
    CameraKeyframe3D,
    CinematicFlythroughPath,
    generate_cinematic_flythrough_path,
)
from .interactive_poi_callout_labels import (
    CalloutPin3D,
    POICalloutSet,
    generate_3d_poi_callouts,
)
from .procedural_bridge_piers_cables import (
    BridgePylonType,
    BridgeStructure3D,
    generate_3d_suspension_bridge_mesh,
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
from .lighting_rig import (
    CityLightingRig,
    StreetlampInstance,
    generate_night_city_effects,
)
from .road_3d_builder import (
    BridgeDeckMesh,
    RoadGeometry3D,
    generate_3d_road_mesh,
)
from .roof_generator import (
    RoofMesh3D,
    RoofType,
    generate_roof_mesh,
)
from .shadow_caster_baking import (
    ShadowBakeResult,
    bake_static_building_shadows,
)
from .solar_shadow import (
    BuildingSolarAssessment,
    CitySolarReport,
    SolarPosition,
    calculate_solar_position,
    compute_rooftop_solar_potential,
    project_building_shadow,
)
from .street_furniture_instancer import (
    FurniturePlacementReport,
    StreetFurnitureInstance,
    instantiate_street_furniture,
)
from .thermal_envelope import (
    BuildingThermalLoss,
    ThermalEnvelopeReport,
    compute_building_thermal_loss,
)
from .themes import (
    ColorTheme,
    ThemePalette,
    get_theme,
    list_theme_names,
)
from .traffic_mesh_simulator import (
    TrafficSimulationMesh,
    TrafficVehicle3D,
    generate_traffic_flow_geometry,
)
from .tunnel_subsurface_builder import (
    TunnelGeometry3D,
    generate_3d_tunnel_mesh,
)
from .vegetation_generator import (
    TreeMesh3D,
    TreeType,
    generate_forest_canopy_mesh,
    generate_procedural_tree_mesh,
)
from .water_mesh_builder import (
    GerstnerWaveParams,
    WaterSurfaceMesh3D,
    generate_animated_water_mesh,
)
from .weather_particle_fx import (
    WeatherParticleFX,
    WeatherType,
    generate_weather_particle_system,
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
    # Roof Generator
    "RoofMesh3D",
    "RoofType",
    "generate_roof_mesh",
    # Solar Shadow & Irradiance
    "SolarPosition",
    "BuildingSolarAssessment",
    "CitySolarReport",
    "calculate_solar_position",
    "project_building_shadow",
    "compute_rooftop_solar_potential",
    # Procedural Vegetation
    "TreeType",
    "TreeMesh3D",
    "generate_procedural_tree_mesh",
    "generate_forest_canopy_mesh",
    # Thermal Envelope & Heat Loss
    "BuildingThermalLoss",
    "ThermalEnvelopeReport",
    "compute_building_thermal_loss",
    # 3D Road Network & Bridges
    "RoadGeometry3D",
    "BridgeDeckMesh",
    "generate_3d_road_mesh",
    # City Lighting Rig
    "CityLightingRig",
    "StreetlampInstance",
    "generate_night_city_effects",
    # 3D Water & Waves
    "WaterSurfaceMesh3D",
    "GerstnerWaveParams",
    "generate_animated_water_mesh",
    # Cinematic Camera Director
    "CinematicFlythroughPath",
    "CameraKeyframe3D",
    "generate_cinematic_flythrough_path",
    # 3D Traffic Flow Simulator
    "generate_traffic_flow_geometry",
    "TrafficSimulationMesh",
    "TrafficVehicle3D",
    # Ground Shadow Baking
    "bake_static_building_shadows",
    "ShadowBakeResult",
    # Street Furniture Instancer
    "instantiate_street_furniture",
    "FurniturePlacementReport",
    "StreetFurnitureInstance",
    # Weather Particle FX
    "generate_weather_particle_system",
    "WeatherParticleFX",
    "WeatherType",
    # 3D Subsurface Tunnel Tube Builder
    "generate_3d_tunnel_mesh",
    "TunnelGeometry3D",
    # Multi-LOD & Billboard Impostor Manager
    "generate_lod_building_levels",
    "BuildingLODSet",
    "LODDistanceConfig",
    # 3D Suspension Bridge Pylon & Catenary Cables
    "generate_3d_suspension_bridge_mesh",
    "BridgeStructure3D",
    "BridgePylonType",
    # 3D POI Callout Labels & Leader Lines
    "generate_3d_poi_callouts",
    "POICalloutSet",
    "CalloutPin3D",
]
