# -*- coding: utf-8 -*-
"""Procedural 3D City Geometry Generator, Mesh Representation, and CityModel3D Container."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

from .fetcher import BoundingBox
from .themes import ThemePalette, get_theme


@dataclass
class BuildingMesh:
    """3D Extruded Building Mesh with Roof Geometry and Semantic Tags."""

    osm_id: int | str
    footprint: list[tuple[float, float]]  # (lon, lat)
    height_m: float
    min_height_m: float = 0.0
    levels: int = 3
    roof_shape: str = "flat"  # flat, gabled, hipped, mansard, pyramidal, dome
    roof_height_m: float = 2.5
    wall_color: str | None = None
    roof_color: str | None = None
    building_type: str = "yes"
    tags: dict[str, str] = field(default_factory=dict)


@dataclass
class RoadMesh:
    """3D Road Ribbon with Centerline and Lane Attributes."""

    osm_id: int | str
    centerline: list[tuple[float, float]]  # (lon, lat)
    width_m: float
    highway_type: str
    lanes: int = 1
    name: str = ""
    surface: str = "asphalt"
    is_bridge: bool = False
    is_tunnel: bool = False
    tags: dict[str, str] = field(default_factory=dict)


@dataclass
class WaterMesh:
    """Waterbody Surface Polygon."""

    osm_id: int | str
    polygon: list[tuple[float, float]]
    water_type: str = "water"
    name: str = ""
    tags: dict[str, str] = field(default_factory=dict)


@dataclass
class ParkMesh:
    """Green Space and Landscape Polygon."""

    osm_id: int | str
    polygon: list[tuple[float, float]]
    park_type: str = "park"
    name: str = ""
    tags: dict[str, str] = field(default_factory=dict)


@dataclass
class TreeInstance:
    """Individual 3D Tree Point Instance."""

    lon: float
    lat: float
    height_m: float = 6.0
    canopy_radius_m: float = 2.5
    tree_type: str = "tree"


@dataclass
class CityModel3D:
    """Master Container for a 3D Procedural City Model."""

    name: str
    bbox: BoundingBox
    buildings: list[BuildingMesh] = field(default_factory=list)
    roads: list[RoadMesh] = field(default_factory=list)
    waterbodies: list[WaterMesh] = field(default_factory=list)
    parks: list[ParkMesh] = field(default_factory=list)
    trees: list[TreeInstance] = field(default_factory=list)
    theme: ThemePalette = field(default_factory=lambda: get_theme("Editorial Paper"))
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def building_count(self) -> int:
        return len(self.buildings)

    @property
    def road_count(self) -> int:
        return len(self.roads)

    @property
    def total_road_km(self) -> float:
        total_m = 0.0
        for r in self.roads:
            pts = r.centerline
            for i in range(len(pts) - 1):
                lon1, lat1 = pts[i]
                lon2, lat2 = pts[i + 1]
                # Haversine distance
                dlat = math.radians(lat2 - lat1)
                dlon = math.radians(lon2 - lon1)
                a = (
                    math.sin(dlat / 2.0) ** 2
                    + math.cos(math.radians(lat1))
                    * math.cos(math.radians(lat2))
                    * math.sin(dlon / 2.0) ** 2
                )
                c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
                total_m += 6371000.0 * c
        return total_m / 1000.0

    @property
    def tree_count(self) -> int:
        return len(self.trees)

    def summary(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "theme": self.theme.name,
            "bbox": self.bbox.to_tuple(),
            "building_count": self.building_count,
            "road_count": self.road_count,
            "total_road_km": round(self.total_road_km, 2),
            "waterbody_count": len(self.waterbodies),
            "park_count": len(self.parks),
            "tree_count": self.tree_count,
        }

    def to_html(self, output_path: str | None = None, title: str | None = None) -> str:
        """Export city model to a standalone 60 FPS Three.js 3D WebGL HTML bundle."""
        from .bundler import bundle_city_to_html

        html_str = bundle_city_to_html(self, title=title or self.name)
        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html_str)
        return html_str

    def to_glb(self, output_path: str) -> None:
        """Export 3D city scene into binary glTF 2.0 (.glb) for Blender, Unity, and Unreal."""
        from .exporters import export_to_glb

        export_to_glb(self, output_path)

    def to_obj(self, output_path: str) -> None:
        """Export 3D city mesh into Wavefront OBJ + MTL format."""
        from .exporters import export_to_obj

        export_to_obj(self, output_path)

    def to_geojson(self, output_path: str | None = None) -> dict[str, Any]:
        """Export city layers into standard 3D GeoJSON FeatureCollection."""
        from .exporters import export_to_geojson_3d

        return export_to_geojson_3d(self, output_path=output_path)

    def to_dxf(self, output_path: str) -> None:
        """Export 3D building outlines and roads into AutoCAD DXF format."""
        from .exporters import export_to_dxf_3d

        export_to_dxf_3d(self, output_path)

    def _repr_html_(self) -> str:
        """Rich interactive HTML representation for Jupyter Notebooks & Google Colab."""
        from .bundler import bundle_city_to_html

        bundle_str = bundle_city_to_html(self, title=self.name)
        import html

        escaped = html.escape(bundle_str)
        return f'<iframe srcdoc="{escaped}" style="width:100%; height:550px; border:1px solid #30363d; border-radius:8px;" frameborder="0"></iframe>'

    def show(self, width: str = "100%", height: int = 550) -> Any:
        """Display 3D interactive viewer in Jupyter Notebook."""
        try:
            from IPython.display import HTML, display

            display(HTML(self._repr_html_()))
        except ImportError:
            pass


# Highway width mapping dictionary (in meters)
_HIGHWAY_WIDTHS = {
    "motorway": 14.0,
    "trunk": 12.0,
    "primary": 9.0,
    "secondary": 7.5,
    "tertiary": 6.0,
    "residential": 5.0,
    "living_street": 4.0,
    "service": 3.5,
    "pedestrian": 4.5,
    "footway": 2.0,
    "cycleway": 2.2,
    "path": 1.8,
    "steps": 2.0,
}


def _parse_height(tags: dict[str, str], default_levels: int = 3) -> tuple[float, float, int]:
    """Calculate building height, min_height, and levels from OSM tags."""
    levels = default_levels
    if "building:levels" in tags:
        try:
            levels = max(1, int(float(tags["building:levels"])))
        except (ValueError, TypeError):
            pass

    # Height in meters (levels * 3.2m per floor)
    height_m = levels * 3.2
    if "height" in tags:
        try:
            val_str = tags["height"].lower().replace("m", "").strip()
            height_m = max(2.5, float(val_str))
        except (ValueError, TypeError):
            pass

    min_height_m = 0.0
    if "min_height" in tags:
        try:
            val_str = tags["min_height"].lower().replace("m", "").strip()
            min_height_m = float(val_str)
        except (ValueError, TypeError):
            pass
    elif "building:min_level" in tags:
        try:
            min_levels = int(float(tags["building:min_level"]))
            min_height_m = min_levels * 3.2
        except (ValueError, TypeError):
            pass

    return height_m, min_height_m, levels


def _parse_roof_shape(tags: dict[str, str]) -> str:
    """Normalize roof shape tag."""
    shape = tags.get("roof:shape", "flat").lower().strip()
    valid_shapes = {"flat", "gabled", "hipped", "mansard", "pyramidal", "dome", "skillion"}
    return shape if shape in valid_shapes else "flat"


def generate_3d_city(
    osm_data: dict[str, Any],
    bbox: BoundingBox | None = None,
    theme: str = "Editorial Paper",
    name: str = "3D City Model",
    default_levels: int = 3,
) -> CityModel3D:
    """Parse raw Overpass OSM elements into a 3D City Model."""
    palette = get_theme(theme)

    # 1. Index Nodes: id -> (lon, lat)
    nodes: dict[int, tuple[float, float]] = {}
    elements = osm_data.get("elements", [])

    for el in elements:
        if el.get("type") == "node" and "lon" in el and "lat" in el:
            nodes[el["id"]] = (float(el["lon"]), float(el["lat"]))

    # 2. Extract Geometry Meshes
    buildings: list[BuildingMesh] = []
    roads: list[RoadMesh] = []
    waterbodies: list[WaterMesh] = []
    parks: list[ParkMesh] = []
    trees: list[TreeInstance] = []

    min_lon, min_lat, max_lon, max_lat = 180.0, 90.0, -180.0, -90.0

    def update_bounds(coords: list[tuple[float, float]]) -> None:
        nonlocal min_lon, min_lat, max_lon, max_lat
        for lon, lat in coords:
            if lon < min_lon:
                min_lon = lon
            if lon > max_lon:
                max_lon = lon
            if lat < min_lat:
                min_lat = lat
            if lat > max_lat:
                max_lat = lat

    for el in elements:
        el_type = el.get("type")
        tags = el.get("tags", {})
        osm_id = el.get("id", 0)

        # Trees from single nodes
        if el_type == "node":
            if tags.get("natural") == "tree":
                lon, lat = float(el["lon"]), float(el["lat"])
                trees.append(TreeInstance(lon=lon, lat=lat, height_m=6.0, canopy_radius_m=2.5))
                update_bounds([(lon, lat)])
            continue

        if el_type == "way":
            way_nodes = el.get("nodes", [])
            coords = [nodes[nid] for nid in way_nodes if nid in nodes]
            if len(coords) < 2:
                continue

            update_bounds(coords)

            # Building
            if "building" in tags:
                h, min_h, lvls = _parse_height(tags, default_levels=default_levels)
                roof_shape = _parse_roof_shape(tags)
                b_type = tags.get("building", "yes")
                buildings.append(
                    BuildingMesh(
                        osm_id=osm_id,
                        footprint=coords,
                        height_m=h,
                        min_height_m=min_h,
                        levels=lvls,
                        roof_shape=roof_shape,
                        roof_height_m=2.5 if roof_shape != "flat" else 0.0,
                        wall_color=tags.get("building:colour"),
                        roof_color=tags.get("roof:colour"),
                        building_type=b_type,
                        tags=tags,
                    )
                )

            # Road / Highway
            elif "highway" in tags:
                hw = tags["highway"]
                width = _HIGHWAY_WIDTHS.get(hw, 5.0)
                lanes = 1
                if "lanes" in tags:
                    try:
                        lanes = int(float(tags["lanes"]))
                        width = max(width, lanes * 3.5)
                    except (ValueError, TypeError):
                        pass

                roads.append(
                    RoadMesh(
                        osm_id=osm_id,
                        centerline=coords,
                        width_m=width,
                        highway_type=hw,
                        lanes=lanes,
                        name=tags.get("name", ""),
                        surface=tags.get("surface", "asphalt"),
                        is_bridge=tags.get("bridge") in ("yes", "true", "1"),
                        is_tunnel=tags.get("tunnel") in ("yes", "true", "1"),
                        tags=tags,
                    )
                )

            # Water
            elif tags.get("natural") == "water" or "waterway" in tags:
                waterbodies.append(
                    WaterMesh(
                        osm_id=osm_id,
                        polygon=coords,
                        water_type=tags.get("natural", tags.get("waterway", "water")),
                        name=tags.get("name", ""),
                        tags=tags,
                    )
                )

            # Parks / Greenery
            elif tags.get("leisure") == "park" or tags.get("landuse") in (
                "grass",
                "forest",
                "meadow",
                "village_green",
            ):
                parks.append(
                    ParkMesh(
                        osm_id=osm_id,
                        polygon=coords,
                        park_type=tags.get("leisure", tags.get("landuse", "park")),
                        name=tags.get("name", ""),
                        tags=tags,
                    )
                )

    resolved_bbox = bbox
    if resolved_bbox is None:
        if min_lon > max_lon:
            min_lon, min_lat, max_lon, max_lat = 0.0, 0.0, 0.01, 0.01
        resolved_bbox = BoundingBox(
            min_lon=min_lon, min_lat=min_lat, max_lon=max_lon, max_lat=max_lat
        )

    return CityModel3D(
        name=name,
        bbox=resolved_bbox,
        buildings=buildings,
        roads=roads,
        waterbodies=waterbodies,
        parks=parks,
        trees=trees,
        theme=palette,
        metadata={"generator": "osm2threejs-sdk v0.1.0"},
    )
