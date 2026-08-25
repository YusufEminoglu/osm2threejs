# -*- coding: utf-8 -*-
"""Standalone Single-File Three.js WebGL 3D HTML Bundler for osm2threejs."""

from __future__ import annotations

import json
import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .geometry import CityModel3D


class StandaloneHtmlBundler:
    """Builds self-contained 60 FPS Three.js 3D WebGL HTML documents."""

    @staticmethod
    def build_html(city: CityModel3D, title: str | None = None) -> str:
        center_lon, center_lat = city.bbox.center
        cos_lat = math.cos(math.radians(center_lat))
        m_per_deg_lat = 111132.0
        m_per_deg_lon = 111132.0 * cos_lat

        # Project coordinates to local metric XY (origin at center)
        def to_local_xy(coords: list[tuple[float, float]]) -> list[list[float]]:
            return [
                [
                    round((lon - center_lon) * m_per_deg_lon, 2),
                    round((lat - center_lat) * m_per_deg_lat, 2),
                ]
                for lon, lat in coords
            ]

        # Prepare JSON payload for the embedded WebGL engine
        buildings_data = [
            {
                "id": b.osm_id,
                "poly": to_local_xy(b.footprint),
                "h": round(b.height_m, 1),
                "min_h": round(b.min_height_m, 1),
                "levels": b.levels,
                "roof": b.roof_shape,
                "roof_h": round(b.roof_height_m, 1),
                "wallColor": b.wall_color,
                "roofColor": b.roof_color,
                "type": b.building_type,
            }
            for b in city.buildings
        ]

        roads_data = [
            {
                "id": r.osm_id,
                "line": to_local_xy(r.centerline),
                "width": round(r.width_m, 1),
                "hw": r.highway_type,
                "lanes": r.lanes,
                "name": r.name,
                "bridge": r.is_bridge,
                "tunnel": r.is_tunnel,
            }
            for r in city.roads
        ]

        water_data = [
            {"id": w.osm_id, "poly": to_local_xy(w.polygon), "type": w.water_type, "name": w.name}
            for w in city.waterbodies
        ]

        parks_data = [
            {"id": p.osm_id, "poly": to_local_xy(p.polygon), "type": p.park_type, "name": p.name}
            for p in city.parks
        ]

        trees_data = [
            {
                "x": round((t.lon - center_lon) * m_per_deg_lon, 2),
                "y": round((t.lat - center_lat) * m_per_deg_lat, 2),
                "h": round(t.height_m, 1),
                "r": round(t.canopy_radius_m, 1),
            }
            for t in city.trees
        ]

        scene_payload = {
            "name": title or city.name,
            "theme": city.theme.to_dict(),
            "bbox": city.bbox.to_tuple(),
            "center": [center_lon, center_lat],
            "buildings": buildings_data,
            "roads": roads_data,
            "water": water_data,
            "parks": parks_data,
            "trees": trees_data,
            "counts": city.summary(),
        }

        payload_json = json.dumps(scene_payload)

        return rf"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>{title or city.name} — 3D City Model (osm2threejs)</title>
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body, html {{ width: 100%; height: 100%; overflow: hidden; background: {city.theme.background_color}; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; color: #fff; }}
#webgl-canvas {{ width: 100%; height: 100%; display: block; }}

/* HUD UI */
#hud-top {{
  position: absolute; top: 16px; left: 16px;
  background: rgba(15, 23, 42, 0.85); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
  padding: 12px 18px; border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5); pointer-events: auto; z-index: 10;
}}
.brand-title {{ font-size: 1.15rem; font-weight: 700; background: linear-gradient(135deg, #38bdf8, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
.brand-sub {{ font-size: 0.78rem; color: #94a3b8; margin-top: 2px; }}

#hud-controls {{
  position: absolute; top: 16px; right: 16px;
  background: rgba(15, 23, 42, 0.85); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
  padding: 14px; border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5); width: 240px; font-size: 0.82rem; z-index: 10;
}}
.ctrl-row {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }}
.ctrl-row label {{ color: #cbd5e1; font-weight: 500; }}
.slider {{ width: 100px; accent-color: #38bdf8; }}
.btn {{ background: #1e293b; color: #e2e8f0; border: 1px solid rgba(255,255,255,0.15); padding: 5px 10px; border-radius: 6px; cursor: pointer; font-size: 0.78rem; width: 100%; transition: all 0.2s; }}
.btn:hover {{ background: #38bdf8; color: #090d16; font-weight: 600; }}

#stats-box {{
  position: absolute; bottom: 16px; left: 16px;
  background: rgba(15, 23, 42, 0.75); backdrop-filter: blur(8px);
  padding: 8px 14px; border-radius: 8px; font-size: 0.75rem; color: #94a3b8; border: 1px solid rgba(255,255,255,0.08);
}}
#stats-box span {{ color: #38bdf8; font-weight: 600; }}

#crosshair {{
  position: absolute; top: 50%; left: 50%; width: 8px; height: 8px;
  background: rgba(255, 255, 255, 0.8); border-radius: 50%;
  transform: translate(-50%, -50%); display: none; pointer-events: none;
}}
</style>
<!-- Three.js + OrbitControls CDN -->
<script src="https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.160.0/examples/js/controls/OrbitControls.js"></script>
</head>
<body>

<div id="hud-top">
  <div class="brand-title">{title or city.name}</div>
  <div class="brand-sub">osm2threejs &middot; 3D Procedural Engine &middot; Theme: {city.theme.name}</div>
</div>

<div id="hud-controls">
  <div class="ctrl-row">
    <label>Sun Altitude:</label>
    <input type="range" id="sunAltitude" class="slider" min="5" max="85" value="45">
  </div>
  <div class="ctrl-row">
    <label>Sun Azimuth:</label>
    <input type="range" id="sunAzimuth" class="slider" min="0" max="360" value="135">
  </div>
  <div class="ctrl-row">
    <label>Camera Mode:</label>
    <select id="camMode" class="btn" style="width:110px;padding:3px;">
      <option value="orbit">Orbit (3D Orbit)</option>
      <option value="walk">First-Person Walk</option>
    </select>
  </div>
  <div style="margin-top:8px; display:flex; gap:6px;">
    <button id="resetCamBtn" class="btn">Reset View</button>
  </div>
</div>

<div id="stats-box">
  Buildings: <span>{city.building_count}</span> &middot; Roads: <span>{city.road_count}</span> ({city.total_road_km:.1f} km) &middot; Trees: <span>{city.tree_count}</span>
</div>

<div id="crosshair"></div>
<canvas id="webgl-canvas"></canvas>

<script>
const SCENE_DATA = {payload_json};
const THEME = SCENE_DATA.theme;

// 1. Initialize Three.js Scene, Camera & Renderer
const canvas = document.getElementById("webgl-canvas");
const scene = new THREE.Scene();
scene.background = new THREE.Color(THEME.backgroundColor);
scene.fog = new THREE.FogExp2(THEME.fogColor, THEME.fogDensity);

const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 1, 10000);
camera.position.set(0, 350, 450);

const renderer = new THREE.WebGLRenderer({{ canvas: canvas, antialias: true, alpha: false, powerPreference: "high-performance" }});
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;

const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.05;
controls.maxPolarAngle = Math.PI / 2 - 0.02; // Prevent going below ground

// 2. Lighting & Sun
const ambientLight = new THREE.AmbientLight(0xffffff, 0.45);
scene.add(ambientLight);

const sunLight = new THREE.DirectionalLight(0xfff5e6, 1.2);
sunLight.castShadow = true;
sunLight.shadow.mapSize.width = 2048;
sunLight.shadow.mapSize.height = 2048;
sunLight.shadow.camera.near = 10;
sunLight.shadow.camera.far = 2500;
const d = 500;
sunLight.shadow.camera.left = -d;
sunLight.shadow.camera.right = d;
sunLight.shadow.camera.top = d;
sunLight.shadow.camera.bottom = -d;
sunLight.shadow.bias = -0.0005;
scene.add(sunLight);

function updateSun(altDeg, azDeg) {{
  const phi = (90 - altDeg) * (Math.PI / 180);
  const theta = azDeg * (Math.PI / 180);
  const r = 800;
  sunLight.position.set(r * Math.sin(phi) * Math.cos(theta), r * Math.cos(phi), r * Math.sin(phi) * Math.sin(theta));
}}
updateSun(45, 135);

// 3. Materials
const wallMat = new THREE.MeshStandardMaterial({{ color: THEME.buildingWallColor, roughness: 0.7, metalness: 0.1 }});
const roofMat = new THREE.MeshStandardMaterial({{ color: THEME.buildingRoofColor, roughness: 0.6, metalness: 0.15 }});
const roadMat = new THREE.MeshStandardMaterial({{ color: THEME.roadColor, roughness: 0.85, metalness: 0.05 }});
const parkMat = new THREE.MeshStandardMaterial({{ color: THEME.parkColor, roughness: 0.9, metalness: 0.0 }});
const waterMat = new THREE.MeshStandardMaterial({{ color: THEME.waterColor, roughness: 0.1, metalness: 0.8, transparent: true, opacity: 0.85 }});
const islandMat = new THREE.MeshStandardMaterial({{ color: THEME.islandColor, roughness: 0.8 }});

// 4. Ground Island Platform
const islandGeo = new THREE.CylinderGeometry(600, 610, 8, 64);
const islandMesh = new THREE.Mesh(islandGeo, islandMat);
islandMesh.position.y = -4;
islandMesh.receiveShadow = true;
scene.add(islandMesh);

// 5. Build Parks & Greenery
SCENE_DATA.parks.forEach(p => {{
  if (p.poly.length < 3) return;
  const shape = new THREE.Shape();
  shape.moveTo(p.poly[0][0], -p.poly[0][1]);
  for (let i = 1; i < p.poly.length; i++) {{
    shape.lineTo(p.poly[i][0], -p.poly[i][1]);
  }}
  const geo = new THREE.ShapeGeometry(shape);
  const mesh = new THREE.Mesh(geo, parkMat);
  mesh.rotation.x = -Math.PI / 2;
  mesh.position.y = 0.2;
  mesh.receiveShadow = true;
  scene.add(mesh);
}});

// 6. Build Waterbodies
SCENE_DATA.water.forEach(w => {{
  if (w.poly.length < 3) return;
  const shape = new THREE.Shape();
  shape.moveTo(w.poly[0][0], -w.poly[0][1]);
  for (let i = 1; i < w.poly.length; i++) {{
    shape.lineTo(w.poly[i][0], -w.poly[i][1]);
  }}
  const geo = new THREE.ShapeGeometry(shape);
  const mesh = new THREE.Mesh(geo, waterMat);
  mesh.rotation.x = -Math.PI / 2;
  mesh.position.y = 0.1;
  scene.add(mesh);
}});

// 7. Build Roads
SCENE_DATA.roads.forEach(r => {{
  if (r.line.length < 2) return;
  const curvePts = r.line.map(pt => new THREE.Vector3(pt[0], 0.3, pt[1]));
  const curve = new THREE.CatmullRomCurve3(curvePts);
  const tubeGeo = new THREE.TubeGeometry(curve, r.line.length * 2, r.width / 2.0, 4, false);
  const mesh = new THREE.Mesh(tubeGeo, roadMat);
  mesh.receiveShadow = true;
  scene.add(mesh);
}});

// 8. Build Buildings (Extrusions & Roofs)
SCENE_DATA.buildings.forEach(b => {{
  if (b.poly.length < 3) return;
  const shape = new THREE.Shape();
  shape.moveTo(b.poly[0][0], -b.poly[0][1]);
  for (let i = 1; i < b.poly.length; i++) {{
    shape.lineTo(b.poly[i][0], -b.poly[i][1]);
  }}

  const extrudeSettings = {{
    depth: b.h,
    bevelEnabled: false
  }};

  const geo = new THREE.ExtrudeGeometry(shape, extrudeSettings);
  const mat = b.wallColor ? new THREE.MeshStandardMaterial({{ color: b.wallColor, roughness: 0.7 }}) : wallMat;
  const mesh = new THREE.Mesh(geo, mat);
  mesh.rotation.x = -Math.PI / 2;
  mesh.position.y = b.min_h;
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  scene.add(mesh);

  // Roof cap if roof color exists or gabled
  if (b.roof !== "flat" || b.roofColor) {{
    const roofCapGeo = new THREE.ShapeGeometry(shape);
    const rMat = b.roofColor ? new THREE.MeshStandardMaterial({{ color: b.roofColor, roughness: 0.5 }}) : roofMat;
    const roofMesh = new THREE.Mesh(roofCapGeo, rMat);
    roofMesh.rotation.x = -Math.PI / 2;
    roofMesh.position.y = b.h + b.min_h + 0.05;
    roofMesh.castShadow = true;
    scene.add(roofMesh);
  }}
}});

// 9. Build Trees (Instanced Foliage)
if (SCENE_DATA.trees.length > 0) {{
  const trunkGeo = new THREE.CylinderGeometry(0.3, 0.5, 3, 6);
  const leavesGeo = new THREE.ConeGeometry(2.2, 5, 6);
  const trunkMat = new THREE.MeshStandardMaterial({{ color: "#5c4033", roughness: 0.9 }});
  const leavesMat = new THREE.MeshStandardMaterial({{ color: "#2d6a4f", roughness: 0.8 }});

  SCENE_DATA.trees.forEach(t => {{
    const trunk = new THREE.Mesh(trunkGeo, trunkMat);
    trunk.position.set(t.x, 1.5, t.y);
    trunk.castShadow = true;
    scene.add(trunk);

    const leaves = new THREE.Mesh(leavesGeo, leavesMat);
    leaves.position.set(t.x, 4.5, t.y);
    leaves.castShadow = true;
    scene.add(leaves);
  }});
}}

// 10. Animation Loop
function animate() {{
  requestAnimationFrame(animate);
  controls.update();
  renderer.render(scene, camera);
}}
animate();

// 11. Window Resize
window.addEventListener("resize", () => {{
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
}});

// 12. UI Event Listeners
document.getElementById("sunAltitude").addEventListener("input", (e) => {{
  updateSun(parseFloat(e.target.value), parseFloat(document.getElementById("sunAzimuth").value));
}});
document.getElementById("sunAzimuth").addEventListener("input", (e) => {{
  updateSun(parseFloat(document.getElementById("sunAltitude").value), parseFloat(e.target.value));
}});
document.getElementById("resetCamBtn").addEventListener("click", () => {{
  camera.position.set(0, 350, 450);
  controls.target.set(0, 0, 0);
}});
</script>
</body>
</html>
"""


def bundle_city_to_html(city: CityModel3D, title: str | None = None) -> str:
    """Convenience wrapper for StandaloneHtmlBundler."""
    return StandaloneHtmlBundler.build_html(city, title=title)
