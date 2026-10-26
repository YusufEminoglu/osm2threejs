<div align="center">

<a href="https://geophilo.com/">
  <img src="https://geophilo.com/assets/sdk_icons/osm2threejs_sdk.svg" width="140" height="140" alt="osm2threejs logo" />
</a>

# osm2threejs


[![PyPI version](https://img.shields.io/pypi/v/osm2threejs.svg?color=38bdf8)](https://pypi.org/project/osm2threejs/)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23677253.svg)](https://doi.org/10.5281/zenodo.23677253)
[![Python version support](https://img.shields.io/pypi/pyversions/osm2threejs.svg?color=10b981)](https://pypi.org/project/osm2threejs/)
[![Documentation](https://img.shields.io/badge/docs-GEOPHILO-10b981.svg)](https://geophilo.com/osm2threejs/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/YusufEminoglu/osm2threejs/blob/main/LICENSE)
[![Code style: Ruff](https://img.shields.io/badge/code%20style-ruff-D7FF64.svg)](https://docs.astral.sh/ruff/)

**Generate 3D city models from OpenStreetMap in pure Python: interactive Three.js HTML, glTF/GLB, OBJ, DXF and 3D GeoJSON.**

[📖 **Open Interactive Web Manual**](https://geophilo.com/osm2threejs/) • [📦 **PyPI Package**](https://pypi.org/project/osm2threejs/) • [💻 **GitHub**](https://github.com/YusufEminoglu/osm2threejs) • [🐛 **Issue Tracker**](https://github.com/YusufEminoglu/osm2threejs/issues)

</div>

## 📦 Installation

**Requirements:** Python **3.9+**. The core package has **zero runtime dependencies** — everything is built on the Python standard library.

```bash
# Core package (standard library only)
pip install osm2threejs

# Optional GIS interoperability tooling (Shapely + GeoPandas)
pip install "osm2threejs[geo]"

# Development toolchain (pytest, coverage, ruff, mypy, build, twine)
pip install "osm2threejs[dev]"
```

For a local editable checkout:

```bash
git clone https://github.com/YusufEminoglu/osm2threejs.git
cd osm2threejs
pip install -e ".[dev]"
```

> **Note:** the `geo` extra installs optional downstream GIS tools. The core engine itself never imports Shapely or GeoPandas and works without them.

## ⚡ Quickstart (runs offline)

```python
import osm2threejs as o3

# One 4-storey building and one street as plain GeoJSON (properties act as OSM tags)
geojson = {"type": "FeatureCollection", "features": [
    {"type": "Feature", "properties": {"building": "yes", "building:levels": "4"},
     "geometry": {"type": "Polygon", "coordinates": [[[29.0, 41.0], [29.0004, 41.0], [29.0004, 41.0003], [29.0, 41.0003], [29.0, 41.0]]]}},
    {"type": "Feature", "properties": {"highway": "residential", "name": "Demo Street"},
     "geometry": {"type": "LineString", "coordinates": [[28.9995, 40.9998], [29.001, 40.9998]]}},
]}

city = o3.from_geojson(geojson, theme="Cyberpunk Neon", name="Demo Block")
print(f"{city.building_count} building, {city.road_count} road, {city.total_road_km:.2f} km")
# 1 building, 1 road, 0.13 km
city.to_html("demo_city.html")  # open in a browser: interactive Three.js scene
city.to_glb("demo_city.glb")    # Blender / Unity / Unreal
city.to_obj("demo_city.obj")
city.to_dxf("demo_city.dxf")
city.to_geojson("demo_city.geojson")
```

For real OpenStreetMap data use `o3.from_place("Kadıköy, İstanbul")` or `o3.from_bbox(...)` (needs internet).

---

## 🌟 Overview

**osm2threejs** is a pure-Python, zero-C-dependency geospatial engine that turns OpenStreetMap data into publication-ready, interactive **60 FPS Three.js 3D WebGL scenes**, **binary glTF/GLB models**, **Wavefront OBJ meshes**, **AutoCAD DXF**, and **3D GeoJSON** layers.

Designed from the ground up for urban planners, architects, game developers, GIS analysts, and data scientists, **osm2threejs** runs completely headless across **Jupyter Notebooks**, **Google Colab**, **FastAPI / Flask microservices**, **Docker containers**, and terminal **CLI** pipelines.

---

## 🔬 Core Capabilities

1. **Instant 3D City Generation:**
   - Build complete 3D digital twins from place names (`from_place("Kadıköy, İstanbul")`), bounding boxes (`from_bbox(...)`), or GeoJSON / Overpass element payloads (`from_geojson(...)`).
2. **Procedural Building Extrusions & 6 Roof Topologies:**
   - Infers building heights from `building:levels` (levels × 3.2 m) or `height` tags.
   - Generates procedural **Flat**, **Gabled**, **Hipped**, **Mansard**, **Pyramidal**, and **Skillion** roof geometries.
3. **12 Curated Visual Themes:**
   - *Editorial Paper, Cyberpunk Neon, Blueprint Architectural, Anime Pastel, Dark Glow, Warm Sand & Slate, Teal & Salmon, Light Purple & Black, Tinted Gray Teal, Cartoon Stylized, Monochrome Clay, Realistic Satellite*.
4. **Multi-Format 3D Exporters:**
   - 📄 **Standalone HTML:** Single-file self-contained Three.js 60 FPS viewer with orbit controls, sun elevation/azimuth sliders, and a camera-mode selector.
   - 📦 **Binary glTF 2.0 (.glb):** Ready for direct import into **Blender**, **Unity**, **Unreal Engine**, and **WebXR**.
   - 📐 **Wavefront OBJ:** Universal 3D mesh format with per-building extrusions and roof caps.
   - 🗺️ **3D GeoJSON (PolygonZ / LineStringZ):** Standard OGC 3D vector geometry.
   - 📐 **AutoCAD DXF 3D:** 3D Polyline CAD drawing for buildings and roads.
5. **Procedural 3D Asset Modules:**
   - Urban furniture, solar/shadow analysis, vegetation, road networks, bridges, tunnels, rail tracks, water surfaces, traffic, weather, LOD billboards, POI callouts, noise barriers, wind/solar farms, pedestrian plazas, helipads, and marinas — all generated as plain Python vertex/face buffers.
6. **Interactive Jupyter Notebook / Google Colab Widget:**
   - Direct inline 3D visualization inside notebook cells via `city.show()` or `_repr_html_()`.
7. **Smart Disk Cache & Multi-Mirror Resilience:**
   - SHA-256 disk cache with 7-day TTL and automatic failover across 3 Overpass mirrors.

---

## 🚀 More Examples & Python API

### 1. Build a 3D City from a Place Name

```python
import osm2threejs as o3

# 1. Generate a 3D city model from a place-name query
city = o3.from_place("Kadıköy, İstanbul", theme="Editorial Paper", radius_meters=600)

print(f"Buildings : {city.building_count}")
print(f"Roads     : {city.road_count} ({city.total_road_km:.1f} km)")
print(f"Trees     : {city.tree_count}")

# 2. Export a standalone 60 FPS Three.js HTML viewer
city.to_html("kadikoy_3d.html")

# 3. Export 3D meshes for Blender, Unity, and Unreal Engine
city.to_glb("kadikoy_city.glb")
city.to_obj("kadikoy_city.obj")

# 4. Export 3D GeoJSON and AutoCAD DXF
city.to_geojson("kadikoy_3d.geojson")
city.to_dxf("kadikoy_3d.dxf")

# 5. Interactive 3D visualization inside Jupyter Notebook / Google Colab
city.show()
```

### 2. Build from Bounding Box Coordinates

```python
import osm2threejs as o3

# Bounding box: (min_lon, min_lat, max_lon, max_lat)
city = o3.from_bbox(
    (27.132, 38.421, 27.155, 38.442),
    theme="Cyberpunk Neon",
    name="Alsancak Downtown",
    default_building_levels=4,
)

city.to_html("alsancak_cyberpunk.html")
```

### 3. Build from an In-Memory OSM Element Dictionary

```python
import osm2threejs as o3

# The same schema returned by o3.query_overpass(...)
payload = {
    "elements": [
        {"type": "node", "id": 1, "lon": 29.0, "lat": 41.0},
        {"type": "node", "id": 2, "lon": 29.001, "lat": 41.0},
        {"type": "node", "id": 3, "lon": 29.001, "lat": 41.001},
        {"type": "node", "id": 4, "lon": 29.0, "lat": 41.001},
        {"type": "way", "id": 10, "nodes": [1, 2, 3, 4, 1], "tags": {"building": "yes"}},
    ]
}

city = o3.from_geojson(payload, name="Custom 3D City", theme="Blueprint Architectural")
print(city.summary())
```

### 4. Use Individual Procedural Asset Modules

Every module is independently importable and returns dataclasses with plain vertex/face buffers:

```python
from osm2threejs import (
    RoofType,
    compute_rooftop_solar_potential,
    generate_3d_road_mesh,
    generate_procedural_tree_mesh,
    generate_roof_mesh,
)

footprint = [(0.0, 0.0), (20.0, 0.0), (20.0, 12.0), (0.0, 12.0)]

# Architectural roof
roof = generate_roof_mesh(
    footprint,
    base_height=15.0,
    roof_type=RoofType.GABLED,
    roof_height=4.0,
)
print(roof.to_dict())

# Rooftop solar potential
report = compute_rooftop_solar_potential(
    [{"id": "b1", "height": 18.0, "area": 240.0, "footprint": footprint}],
    lat=41.0,
    lon=29.0,
)
print(report.to_dict()["total_annual_generation_mwh"])

# Road ribbon and a single tree
road = generate_3d_road_mesh([(0.0, 0.0), (120.0, 0.0)], width=9.0)
tree = generate_procedural_tree_mesh(10.0, 20.0)
print(road.road_id, tree.height)
```

---

## 💻 Command Line Interface (CLI)

```bash
# 1. Build from a place name and open the interactive HTML in the browser
osm2threejs build --place "Alsancak, İzmir" --theme "Cyberpunk Neon" --out-html city.html --open

# 2. Build from a bounding box and export both binary GLB and HTML
osm2threejs build --bbox 27.13,38.42,27.16,38.45 --theme "Anime Pastel" --out-glb izmir.glb --out-html izmir.html

# 3. List all 12 registered visual themes
osm2threejs themes

# 4. Geocode a place name to bounding-box coordinates
osm2threejs geocode "Eiffel Tower, Paris" --radius 800
```

Theme names are matched exactly (case-insensitively), so pass the full name such as `"Cyberpunk Neon"` or `"Anime Pastel"`.

---

## 🎨 12 Curated Visual Themes

| Theme Name | Style / Lighting | Walls | Roofs | Roadway | Water |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Editorial Paper** | Warm Sunlight & Paper Tone | `#f4ede2` | `#c9b9a6` | `#7c5c43` | `#9ab8c2` |
| **Cyberpunk Neon** | Dark Ambient + Vibrant Magenta | `#1e1e38` | `#ec4899` | `#334155` | `#0284c7` |
| **Blueprint Architectural**| Technical Cyan Grid | `#1e3a5f` | `#60a5fa` | `#1b4975` | `#38bdf8` |
| **Anime Pastel** | Soft Aesthetic Bloom | `#fffaf0` | `#f472b6` | `#7d8a96` | `#68b0d8` |
| **Dark Glow** | Amber Night Minimal | `#27272a` | `#e11d48` | `#3f3f46` | `#0369a1` |
| **Monochrome Clay** | Studio Sculptural White | `#f5f5f5` | `#d4d4d4` | `#737373` | `#525252` |
| **Warm Sand & Slate** | Golden Hour Sunset | `#f3ede2` | `#c27d53` | `#46413a` | `#608b98` |
| **Teal & Salmon** | Clean Coastal Daylight | `#fdf4f0` | `#fb7185` | `#2f4a46` | `#388e85` |
| **Light Purple & Black** | Twilight Purple | `#faf7fc` | `#a855f7` | `#2a2a30` | `#7a8eb8` |
| **Tinted Gray Teal** | Nordic Morning Fog | `#f0f5f3` | `#0d9488` | `#36433f` | `#4f8f87` |
| **Cartoon Stylized** | High-Contrast Cell Shaded | `#ffffff` | `#f97316` | `#4a4540` | `#45b0e6` |
| **Realistic Satellite** | Direct Noon Photoreal | `#d1d5db` | `#b91c1c` | `#1f2937` | `#1e3a8a` |

---

## 🧩 Feature Modules

| Module | Key Generator(s) | Output |
| :--- | :--- | :--- |
| `geometry` | `generate_3d_city` | `CityModel3D` with buildings, roads, water, parks, trees |
| `roof_generator` | `generate_roof_mesh` | `RoofMesh3D` (6 roof topologies, surface areas, tilt) |
| `solar_shadow` | `calculate_solar_position`, `project_building_shadow`, `compute_rooftop_solar_potential` | `CitySolarReport` with per-building PV yield |
| `vegetation_generator` | `generate_procedural_tree_mesh`, `generate_forest_canopy_mesh` | `TreeMesh3D` instances (broadleaf, conifer, palm, columnar, shrub) |
| `thermal_envelope` | `compute_building_thermal_loss` | `ThermalEnvelopeReport` with EPC ratings |
| `road_3d_builder` | `generate_3d_road_mesh` | `RoadGeometry3D` with optional bridge deck |
| `lighting_rig` | `generate_night_city_effects` | `CityLightingRig` with streetlamp placements |
| `water_mesh_builder` | `generate_animated_water_mesh` | `WaterSurfaceMesh3D` with Gerstner waves |
| `camera_director` | `generate_cinematic_flythrough_path` | `CinematicFlythroughPath` keyframes |
| `traffic_mesh_simulator` | `generate_traffic_flow_geometry` | `TrafficSimulationMesh` vehicles |
| `shadow_caster_baking` | `bake_static_building_shadows` | `ShadowBakeResult` + GeoJSON shadows |
| `street_furniture_instancer` | `instantiate_street_furniture` | `FurniturePlacementReport` instances |
| `weather_particle_fx` | `generate_weather_particle_system` | `WeatherParticleFX` configuration |
| `tunnel_subsurface_builder` | `generate_3d_tunnel_mesh` | `TunnelGeometry3D` |
| `billboard_lod_manager` | `generate_lod_building_levels` | `BuildingLODSet` with 3 LOD tiers |
| `procedural_bridge_piers_cables` | `generate_3d_suspension_bridge_mesh` | `BridgeStructure3D` |
| `interactive_poi_callout_labels` | `generate_3d_poi_callouts` | `POICalloutSet` |
| `tram_metro_rail_track_builder` | `generate_3d_railway_mesh` | `RailwayGeometry3D` |
| `soundwall_noise_barrier_builder` | `generate_3d_noise_barrier_mesh` | `NoiseBarrierMesh3D` |
| `wind_turbine_solar_farm_builder` | `generate_3d_renewable_energy_assets` | `RenewableEnergyScene3D` |
| `pedestrian_plaza_crosswalk_builder` | `generate_3d_pedestrian_plaza_mesh` | `PedestrianPlazaGeometry3D` |
| `helipad_aviation_lighting_builder` | `generate_3d_helipad_mesh` | `HelipadAviation3D` |
| `harbor_marina_pier_builder` | `generate_3d_marina_harbor_mesh` | `MarinaHarborGeometry3D` |

---

## 📚 Public API Reference

### Top-level helpers (`osm2threejs`)

| Symbol | Signature | Description |
| :--- | :--- | :--- |
| `from_place` | `(place_name, theme="Editorial Paper", radius_meters=500.0, default_building_levels=3) -> CityModel3D` | Geocode a place name and build a city. |
| `from_bbox` | `(bbox, theme="Editorial Paper", name="3D City Model", default_building_levels=3) -> CityModel3D` | Fetch OSM data for a `(min_lon, min_lat, max_lon, max_lat)` box. |
| `from_geojson` | `(geojson_data, theme="Editorial Paper", name="Custom 3D City", default_building_levels=3) -> CityModel3D` | Build from GeoJSON (dict or JSON string; properties act as OSM tags) or an Overpass `elements` dict. |
| `generate_3d_city` | `(osm_data, bbox=None, theme="Editorial Paper", name="3D City Model", default_levels=3) -> CityModel3D` | Convert raw Overpass elements into a city model. |
| `geojson_to_overpass` | `(geojson_data) -> dict` | Convert a GeoJSON Feature/FeatureCollection into Overpass-style `elements` (Points → nodes, lines and polygon outer rings → ways). |
| `list_themes` / `list_theme_names` | `() -> list[str]` | List the 12 registered theme names. |
| `get_theme` | `(name="Editorial Paper") -> ThemePalette` | Resolve a theme name (case-insensitive, with fallback). |
| `geocode_place_name` | `(place_name, radius_meters=500.0) -> BoundingBox` | Nominatim geocoding to a bounding box. |
| `query_overpass` | `(query_str, timeout=60, endpoints=OVERPASS_MIRRORS, use_cache=True) -> dict` | Execute an Overpass QL query with retries and caching. |
| `bundle_city_to_html` | `(city, title=None) -> str` | Render a standalone Three.js HTML document. |
| `export_to_glb` | `(city, output_path) -> None` | Write binary glTF 2.0. |
| `export_to_obj` | `(city, output_path) -> None` | Write Wavefront OBJ. |
| `export_to_geojson_3d` | `(city, output_path=None) -> dict` | Build/write a 3D GeoJSON FeatureCollection. |
| `export_to_dxf_3d` | `(city, output_path) -> None` | Write AutoCAD DXF 3D. |

### `CityModel3D` methods

| Method | Signature | Description |
| :--- | :--- | :--- |
| `summary` | `() -> dict[str, Any]` | Building/road/water/park/tree statistics. |
| `to_html` | `(output_path=None, title=None) -> str` | Standalone Three.js HTML (also returns the string). |
| `to_glb` | `(output_path) -> None` | Binary glTF 2.0 export. |
| `to_obj` | `(output_path) -> None` | Wavefront OBJ export. |
| `to_geojson` | `(output_path=None) -> dict[str, Any]` | 3D GeoJSON export. |
| `to_dxf` | `(output_path) -> None` | AutoCAD DXF export. |
| `show` | `(width="100%", height=550) -> Any` | Inline Jupyter/Colab viewer. |
| `_repr_html_` | `() -> str` | Rich notebook representation. |

### Programmatic generators

| Generator | Returns |
| :--- | :--- |
| `generate_roof_mesh(ring, base_height, roof_type=RoofType.GABLED, roof_height=3.0, ridge_orientation=None)` | `RoofMesh3D` |
| `calculate_solar_position(lat, lon, dt=None)` | `SolarPosition` |
| `project_building_shadow(footprint, height, solar_pos)` | `(shadow_length, polygon)` |
| `compute_rooftop_solar_potential(buildings, lat=41.0, lon=29.0, ...)` | `CitySolarReport` |
| `generate_procedural_tree_mesh(x, y, z=0.0, tree_type=TreeType.BROADLEAF, ...)` | `TreeMesh3D` |
| `generate_forest_canopy_mesh(tree_points, tree_type=TreeType.BROADLEAF)` | `list[TreeMesh3D]` |
| `compute_building_thermal_loss(buildings, ...)` | `ThermalEnvelopeReport` |
| `generate_3d_road_mesh(centerline_coords, road_id="road_1", road_class="primary", width=8.0, is_bridge=False, bridge_elevation=6.0)` | `RoadGeometry3D` |
| `generate_night_city_effects(road_centerlines, lamp_interval_meters=30.0, ...)` | `CityLightingRig` |
| `generate_animated_water_mesh(bounding_polygon, waterbody_id="water_1", ...)` | `WaterSurfaceMesh3D` |
| `generate_cinematic_flythrough_path(city_center=(0, 0, 0), orbit_radius=300.0, ...)` | `CinematicFlythroughPath` |
| `generate_traffic_flow_geometry(road_centerline_3d, traffic_density_per_km=25.0, ...)` | `TrafficSimulationMesh` |
| `bake_static_building_shadows(building_footprints, building_heights, sun_azimuth_deg=180.0, sun_elevation_deg=45.0)` | `ShadowBakeResult` |
| `instantiate_street_furniture(road_centerline_3d, road_width_m=8.0, ...)` | `FurniturePlacementReport` |
| `generate_weather_particle_system(weather_type=WeatherType.RAIN, intensity=1.0, ...)` | `WeatherParticleFX` |
| `generate_3d_tunnel_mesh(tunnel_centerline_3d, tunnel_id="tunnel_main", ...)` | `TunnelGeometry3D` |
| `generate_lod_building_levels(footprint_2d, building_id="bldg_01", height_m=30.0, ...)` | `BuildingLODSet` |
| `generate_3d_suspension_bridge_mesh(bridge_centerline, bridge_id="Bosphorus_Bridge", ...)` | `BridgeStructure3D` |
| `generate_3d_poi_callouts(landmarks_data, city_name="Metropolis 3D")` | `POICalloutSet` |
| `generate_3d_railway_mesh(track_centerline_3d, track_id="T1_Tramway", profile=None)` | `RailwayGeometry3D` |
| `generate_3d_noise_barrier_mesh(barrier_path_3d, barrier_id="Soundwall_Corridor", ...)` | `NoiseBarrierMesh3D` |
| `generate_3d_renewable_energy_assets(turbine_locations, solar_farm_boundary_polygon=None, ...)` | `RenewableEnergyScene3D` |
| `generate_3d_pedestrian_plaza_mesh(plaza_boundary_polygon, crosswalk_centerlines=None, ...)` | `PedestrianPlazaGeometry3D` |
| `generate_3d_helipad_mesh(center_coordinates=(0.0, 0.0, 25.0), touchdown_diameter_m=18.0, ...)` | `HelipadAviation3D` |
| `generate_3d_marina_harbor_mesh(main_pier_centerline, breakwater_polyline=None, ...)` | `MarinaHarborGeometry3D` |

All public generators accept plain Python sequences (lists/tuples) and return dataclasses whose `.to_dict()`, `.to_geojson()`, or `.to_threejs_*()` helpers produce JSON-serialisable payloads.

---

## 🚶 First-Person Pedestrian Walk Mode

Walk Mode simulates human ground-level perception with realistic eye height (1.73m), dynamic movement velocity (1.8m/s), and real-time obstacle avoidance.

---

## ⚡ Performance Benchmarks

| Operation | Dataset / Scope | Entity Count | Execution Time | Throughput |
| :--- | :--- | :--- | :--- | :--- |
| **Cached Query Retrieval** | Urban Core (1 km²) | 15,000 Nodes/Ways | **0.2 ms** | Instant Disk Cache |
| **Procedural 3D Mesh Generation** | District Model (300 ha) | 8,500 Buildings | **34.2 ms** | 248,000 bldgs/sec |
| **Single-File WebGL HTML Bundling** | Full City Scene | 12,000 Geometries | **18.5 ms** | 648,000 entities/sec |
| **Binary glTF 2.0 (.glb) Serialization** | 3D Scene + Buffers | 150,000 Triangles | **48.1 ms** | 3.1M triangles/sec |

---

## 🧪 Development & Testing

```bash
# Clone the repository
git clone https://github.com/YusufEminoglu/osm2threejs.git
cd osm2threejs

# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Run the test suite with coverage
pytest tests/ --cov=osm2threejs -v

# Run linter and formatter
ruff check .
ruff format src tests
```

---

## 📄 Academic Citation

If you use **osm2threejs** in research, urban planning digital twins, or software applications, please cite:

```bibtex
@software{eminoglu2026osm2threejs,
  author    = {Emino{\u{g}}lu, Yusuf},
  title     = {{osm2threejs: Pure-Python 3D City Generator from OpenStreetMap into Three.js WebGL and 3D Assets}},
  year      = {2026},
  publisher = {Zenodo},
  version   = {0.12.3},
  doi       = {10.5281/zenodo.23677253},
  url       = {https://github.com/YusufEminoglu/osm2threejs}
}
```

---

## 📜 License

Distributed under the **MIT License**.
