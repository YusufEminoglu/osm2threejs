# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
