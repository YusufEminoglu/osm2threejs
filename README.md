<p align="center">
  <img src="https://geophilo.com/assets/sdk_icons/osm2threejs_sdk.svg" alt="An OpenStreetMap study area rising into a procedural 3D city and recolouring through curated looks as the sun crosses the sky" width="100%">
</p>

<div align="center">

<a href="https://geophilo.com/">
  <img src="https://geophilo.com/assets/sdk_icons/osm2threejs_sdk.svg" width="140" height="140" alt="osm2threejs logo" />
</a>

# osm2threejs


[![PyPI version](https://img.shields.io/pypi/v/osm2threejs.svg?color=38bdf8)](https://pypi.org/project/osm2threejs/)
[![Python version support](https://img.shields.io/pypi/pyversions/osm2threejs.svg?color=10b981)](https://pypi.org/project/osm2threejs/)
[![Documentation](https://img.shields.io/badge/docs-GEOPHILO-10b981.svg)](https://geophilo.com/osm2threejs/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Code style: Ruff](https://img.shields.io/badge/code%20style-ruff-D7FF64.svg)](https://docs.astral.sh/ruff/)

**Pure-Python Headless 3D City Generator from OpenStreetMap into Three.js WebGL & 3D Assets.**

[📖 **Open Interactive Web Manual**](https://geophilo.com/osm2threejs/) • [📦 **PyPI Package**](https://pypi.org/project/osm2threejs/) • [🐛 **Issue Tracker**](https://gitlab.com/geospacephilo/osm2threejs/-/issues)

</div>

---

## 🌟 Overview

**osm2threejs** is a pure-Python, zero-C-dependency geospatial engine that turns OpenStreetMap data into publication-ready, interactive **60 FPS Three.js 3D WebGL scenes**, **binary glTF/GLB models**, **Wavefront OBJ meshes**, **AutoCAD DXF**, and **3D GeoJSON** layers.

Designed from the ground up for urban planners, architects, game developers, GIS analysts, and data scientists, **osm2threejs** runs completely headless across **Jupyter Notebooks**, **Google Colab**, **FastAPI / Flask microservices**, **Docker containers**, and terminal **CLI** pipelines.

<p align="center">
  <img src="https://geophilo.com/assets/sdk_icons/osm2threejs_sdk.svg" alt="osm2threejs export pipeline from Overpass to GeoJSON and Three.js 3D models" width="100%">
</p>

---

## 🔬 Core Capabilities

1. **Instant 3D City Generation:**
   - Build complete 3D digital twins from place names (`from_place("Kadıköy, İstanbul")`) or bounding boxes (`from_bbox(...)`).
2. **Procedural Building Extrusions & 6 Roof Topologies:**
   - Inferences building heights from `building:levels` ($levels \times 3.2\text{m}$) or `height` tags.
   - Generates procedural **Flat**, **Gabled**, **Hipped**, **Mansard**, **Pyramidal**, and **Dome** roof geometries.
3. **12 Curated Visual Themes:**
   - *Editorial Paper, Cyberpunk Neon, Blueprint Architectural, Anime Pastel, Dark Glow, Warm Sand & Slate, Teal & Salmon, Light Purple & Black, Tinted Gray Teal, Cartoon Stylized, Monochrome Clay, Realistic Satellite*.
4. **Multi-Format 3D Exporters:**
   - 📄 **Standalone HTML:** Single-file self-contained Three.js 60 FPS viewer with orbit/walk controls, sun elevation slider, and weather effects.
   - 📦 **Binary glTF 2.0 (.glb):** Ready for direct import into **Blender**, **Unity**, **Unreal Engine**, and **WebXR**.
   - 📐 **Wavefront OBJ + MTL:** Universal 3D mesh format.
   - 🗺️ **3D GeoJSON (PolygonZ / LineStringZ):** Standard OGC 3D vector geometry.
   - 📐 **AutoCAD DXF 3D:** 3D Polyline / 3DFace CAD drawing.
5. **First-Person Pedestrian Walk Mode:**
   - True 1.73m human eye-level navigation with real-time collision detection and keyboard WASD controls.
6. **Interactive Jupyter Notebook / Google Colab Widget:**
   - Direct inline 3D visualization inside notebook cells via `city.show()` or `_repr_html_()`.
7. **Smart Disk Cache & Multi-Mirror Resilience:**
   - SHA-256 disk cache with 7-day TTL and automatic failover across 3 Overpass mirrors.

---

## 📦 Installation

```bash
pip install osm2threejs
```

---

## 🚀 Quickstart & Python API

### 1. Build a 3D City from a Place Name

```python
import osm2threejs as o3

# 1. Generate 3D City Model from place name query
city = o3.from_place("Kadıköy, İstanbul", theme="Editorial Paper", radius_meters=600)

print(f"Buildings : {city.building_count}")
print(f"Roads     : {city.road_count} ({city.total_road_km:.1f} km)")
print(f"Trees     : {city.tree_count}")

# 2. Export Standalone 60 FPS Three.js HTML Viewer (Offline-ready)
city.to_html("kadikoy_3d.html")

# 3. Export 3D Mesh for Blender, Unity, and Unreal Engine
city.to_glb("kadikoy_city.glb")
city.to_obj("kadikoy_city.obj")

# 4. Export 3D GeoJSON & AutoCAD DXF
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
)

city.to_html("alsancak_cyberpunk.html")
```

---

## 💻 Command Line Interface (CLI)

```bash
# 1. Build from place name and open interactive HTML in browser
osm2threejs build --place "Alsancak, İzmir" --theme cyberpunk --out-html city.html --open

# 2. Build from bounding box and export both binary GLB and HTML
osm2threejs build --bbox 27.13,38.42,27.16,38.45 --theme anime --out-glb izmir.glb --out-html izmir.html

# 3. List all 12 registered visual themes
osm2threejs themes

# 4. Geocode place name to bounding box coordinates
osm2threejs geocode "Eiffel Tower, Paris" --radius 800
```

---

## 🎨 12 Curated Visual Themes

<p align="center">
  <img src="https://geophilo.com/assets/sdk_icons/osm2threejs_sdk.svg" alt="12 Curated Visual Themes Gallery for osm2threejs" width="100%">
</p>

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

## 🚶 First-Person Pedestrian Walk Mode

<p align="center">
  <img src="https://geophilo.com/assets/sdk_icons/osm2threejs_sdk.svg" alt="A 1.85 metre walker moving through the street with the eye height marked at 1.73 metres" width="100%">
</p>

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
git clone https://gitlab.com/geospacephilo/osm2threejs.git
cd osm2threejs

# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Run test suite with coverage
pytest tests/ --cov=osm2threejs -v

# Run linter and formatting
ruff check .
ruff format .
```

---

## 📄 Academic Citation

If you use **osm2threejs** in research, urban planning digital twins, or software applications, please cite:

```bibtex
@software{eminoglu2026osm2threejs,
  author    = {Emino{\u{g}}lu, Yusuf},
  title     = {{osm2threejs: Pure-Python 3D City Generator from OpenStreetMap into Three.js WebGL and 3D Assets}},
  year      = {2026},
  publisher = {PyPI - Python Package Index},
  version   = {0.1.0},
  url       = {https://gitlab.com/geospacephilo/osm2threejs}
}
```

---

## 📜 License

Distributed under the **MIT License**.
