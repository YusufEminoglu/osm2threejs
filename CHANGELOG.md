# Changelog

All notable changes to this project will be documented in this file.

## [0.9.0] - 2026-08-30

### Added
- **Parametric Suspension & Cable-Stayed Bridge Mesh Generator (`procedural_bridge_piers_cables.py`)**: Added `generate_3d_suspension_bridge_mesh` with pylon towers, catenary main cables, and vertical hanger suspenders.
- **3D Screen-Space Landmark & POI Callout Labels (`interactive_poi_callout_labels.py`)**: Added `generate_3d_poi_callouts` producing interactive billboard pins and vertical leader lines.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.8.0] - 2026-08-30

### Added
- **3D Subsurface Tunnel Tube & Portal Builder (`tunnel_subsurface_builder.py`)**: Added `generate_3d_tunnel_mesh` creating underground horseshoe tubes and road deck alignments.
- **Dynamic Multi-Level of Detail (LOD) Manager (`billboard_lod_manager.py`)**: Added `generate_lod_building_levels` with 3-tier geometric lods and far-field 2.5D billboard impostors.

## [0.7.0] - 2026-08-30

### Added
- **Procedural Street Furniture Instancer (`street_furniture_instancer.py`)**: Added `instantiate_street_furniture` placing streetlights, benches, fire hydrants, and waste bins along sidewalks.
- **3D Atmospheric Weather Particle FX (`weather_particle_fx.py`)**: Added `generate_weather_particle_system` with dynamic rain, heavy storm, snow, and fog particle velocity vectors.

## [0.6.0] - 2026-08-30

### Added
- **3D Procedural Traffic Vehicle Flow Simulator (`traffic_mesh_simulator.py`)**: Added `generate_traffic_flow_geometry` placing directional vehicles along 3D road network splines.
- **3D Solar Ray-Traced Ground Shadow Baking (`shadow_caster_baking.py`)**: Added `bake_static_building_shadows` casting geometric occlusion shadow polygons from building prisms.

## [0.5.0] - 2026-08-30

### Added
- **3D Animated Water Surface & Gerstner Waves (`water_mesh_builder.py`)**: Added `generate_animated_water_mesh` with directional wave displacement and normal vectors.
- **Cinematic Orbit & Flythrough Camera Director (`camera_director.py`)**: Added `generate_cinematic_flythrough_path` generating smooth 3D camera keyframe tracks.

## [0.4.0] - 2026-08-30

### Added
- **Procedural 3D Tree Canopy & Vegetation Generator (`vegetation_generator.py`)**: Added `generate_procedural_tree_mesh` and `generate_forest_canopy_mesh` (Broadleaf, Conifer, Palm, Columnar, Shrub).
- **Volumetric Building Thermal Envelope & Heat Loss (`thermal_envelope.py`)**: Added `compute_building_thermal_loss` simulating transmission heat loss, cooling load, and energy performance ratings.
- **3D Road Geometry, Bridges & Overpasses (`road_3d_builder.py`)**: Added `generate_3d_road_mesh` with bridge decks and pier placement.
- **City Day/Night Lighting Rig (`lighting_rig.py`)**: Added `generate_night_city_effects` with automatic streetlamp placements along road polylines.

## [0.2.0] - 2026-08-30

### Added
- **Parametric Procedural 3D Architectural Roof Topologies (`roof_generator.py`)**:
  - `generate_roof_mesh`: Generates 3D vertices, triangular faces, and surface area for 6 roof geometries: `FLAT`, `GABLED` (duo-pitch), `HIPPED` (quad-pitch), `PYRAMIDAL` (central apex), `MANSARD` (dual-pitch curb), and `SKILLION` (monopitch shed).
- **Dynamic 3D Solar Shadow & Rooftop Irradiance Simulator (`solar_shadow.py`)**:
  - `calculate_solar_position`: High-precision solar azimuth and elevation calculation from datetime and coordinates.
  - `project_building_shadow`: 3D shadow vector casting onto ground plane.
  - `compute_rooftop_solar_potential`: Annual rooftop photovoltaic (PV) solar potential estimation (kWh/m² and MWh yield) across 3D city buildings.

## [0.1.0] - 2026-08-26

### Added
- Initial public release of `osm2threejs`.
- Procedural 3D building extrusions from OpenStreetMap tags (`height`, `building:levels`, `min_height`).
- 6 Procedural Roof Geometries: Flat, Gabled, Hipped, Mansard, Pyramidal, Dome.
- 12 Curated Visual Themes: Editorial Paper, Cyberpunk Neon, Blueprint, Anime Pastel, Dark Glow, Monochrome Clay, Warm Sand & Slate, Teal & Salmon, Light Purple & Black, Tinted Gray Teal, Cartoon, Realistic Satellite.
- Multi-format 3D Exporters: Standalone Three.js 60 FPS HTML, Binary glTF 2.0 (.glb), Wavefront OBJ + MTL, 3D GeoJSON (PolygonZ/LineStringZ), AutoCAD DXF 3D.
- Interactive Jupyter Notebook / Google Colab widget support (`city.show()`, `_repr_html_()`).
- Command Line Interface (CLI): `osm2threejs build`, `osm2threejs themes`, `osm2threejs geocode`.
- Smart disk caching and automatic multi-mirror failover for Overpass queries.
