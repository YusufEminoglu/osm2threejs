# -*- coding: utf-8 -*-
"""Multi-format 3D and GIS Exporters for osm2threejs (glTF/GLB, OBJ+MTL, GeoJSON-3D, DXF-3D)."""

from __future__ import annotations

import json
import math
import struct
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .geometry import CityModel3D


def export_to_geojson_3d(city: CityModel3D, output_path: str | None = None) -> dict[str, Any]:
    """Export 3D City layers into a 3D GeoJSON FeatureCollection."""
    features: list[dict[str, Any]] = []

    # 1. Buildings (PolygonZ)
    for b in city.buildings:
        coords_3d = [[lon, lat, b.height_m + b.min_height_m] for lon, lat in b.footprint]
        features.append(
            {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [coords_3d],
                },
                "properties": {
                    "osm_id": b.osm_id,
                    "layer": "building",
                    "height_m": b.height_m,
                    "min_height_m": b.min_height_m,
                    "levels": b.levels,
                    "roof_shape": b.roof_shape,
                    "roof_height_m": b.roof_height_m,
                    "building_type": b.building_type,
                    **b.tags,
                },
            }
        )

    # 2. Roads (LineStringZ)
    for r in city.roads:
        line_3d = [[lon, lat, 0.3] for lon, lat in r.centerline]
        features.append(
            {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": line_3d,
                },
                "properties": {
                    "osm_id": r.osm_id,
                    "layer": "highway",
                    "highway": r.highway_type,
                    "width_m": r.width_m,
                    "lanes": r.lanes,
                    "name": r.name,
                    "surface": r.surface,
                    "bridge": r.is_bridge,
                    "tunnel": r.is_tunnel,
                    **r.tags,
                },
            }
        )

    # 3. Water & Parks
    for w in city.waterbodies:
        poly_3d = [[lon, lat, 0.0] for lon, lat in w.polygon]
        features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Polygon", "coordinates": [poly_3d]},
                "properties": {
                    "osm_id": w.osm_id,
                    "layer": "water",
                    "water_type": w.water_type,
                    "name": w.name,
                },
            }
        )

    for p in city.parks:
        poly_3d = [[lon, lat, 0.1] for lon, lat in p.polygon]
        features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Polygon", "coordinates": [poly_3d]},
                "properties": {
                    "osm_id": p.osm_id,
                    "layer": "park",
                    "park_type": p.park_type,
                    "name": p.name,
                },
            }
        )

    # 4. Trees (PointZ)
    for t in city.trees:
        features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [t.lon, t.lat, t.height_m]},
                "properties": {
                    "layer": "tree",
                    "height_m": t.height_m,
                    "radius_m": t.canopy_radius_m,
                },
            }
        )

    fc = {
        "type": "FeatureCollection",
        "name": city.name,
        "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}},
        "features": features,
    }

    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(fc, f, indent=2)

    return fc


def export_to_obj(city: CityModel3D, output_path: str) -> None:
    """Export 3D City mesh to Wavefront OBJ format with materials."""
    center_lon, center_lat = city.bbox.center
    cos_lat = math.cos(math.radians(center_lat))
    m_per_deg_lat = 111132.0
    m_per_deg_lon = 111132.0 * cos_lat

    lines: list[str] = [
        "# Wavefront OBJ exported by osm2threejs",
        f"# Model: {city.name}",
        f"# Theme: {city.theme.name}",
        f"o {city.name.replace(' ', '_')}",
    ]

    v_idx = 1

    # Write Building Extrusions
    for b in city.buildings:
        if len(b.footprint) < 3:
            continue

        local_pts = [
            ((lon - center_lon) * m_per_deg_lon, (lat - center_lat) * m_per_deg_lat)
            for lon, lat in b.footprint
        ]
        n = len(local_pts)
        if local_pts[0] == local_pts[-1] and n > 3:
            local_pts.pop()
            n -= 1

        base_v = v_idx
        # Bottom vertices (y = min_h)
        for x, z in local_pts:
            lines.append(f"v {x:.3f} {b.min_height_m:.3f} {-z:.3f}")
        # Top vertices (y = min_h + h)
        for x, z in local_pts:
            lines.append(f"v {x:.3f} {(b.min_height_m + b.height_m):.3f} {-z:.3f}")

        v_idx += n * 2

        # Side quad faces
        for i in range(n):
            next_i = (i + 1) % n
            v1 = base_v + i
            v2 = base_v + next_i
            v3 = base_v + n + next_i
            v4 = base_v + n + i
            lines.append(f"f {v1} {v2} {v3} {v4}")

        # Top polygon roof cap
        top_indices = [str(base_v + n + i) for i in range(n)]
        lines.append(f"f {' '.join(top_indices)}")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def export_to_glb(city: CityModel3D, output_path: str) -> None:
    """Export 3D City scene into binary glTF 2.0 (.glb) container."""
    center_lon, center_lat = city.bbox.center
    cos_lat = math.cos(math.radians(center_lat))
    m_per_deg_lat = 111132.0
    m_per_deg_lon = 111132.0 * cos_lat

    vertex_bytes = bytearray()
    index_bytes = bytearray()
    total_vertices = 0
    total_indices = 0

    min_pos = [float("inf"), float("inf"), float("inf")]
    max_pos = [float("-inf"), float("-inf"), float("-inf")]

    for b in city.buildings:
        pts = [
            ((lon - center_lon) * m_per_deg_lon, (lat - center_lat) * m_per_deg_lat)
            for lon, lat in b.footprint
        ]
        if len(pts) < 3:
            continue
        if pts[0] == pts[-1] and len(pts) > 3:
            pts.pop()
        n = len(pts)

        base_idx = total_vertices
        y_bot = b.min_height_m
        y_top = b.min_height_m + b.height_m

        for x, z in pts:
            vertex_bytes.extend(struct.pack("<3f", x, y_bot, -z))
            vertex_bytes.extend(struct.pack("<3f", x, y_top, -z))
            total_vertices += 2
            min_pos[0] = min(min_pos[0], x)
            min_pos[1] = min(min_pos[1], y_bot, y_top)
            min_pos[2] = min(min_pos[2], -z)
            max_pos[0] = max(max_pos[0], x)
            max_pos[1] = max(max_pos[1], y_bot, y_top)
            max_pos[2] = max(max_pos[2], -z)

        for i in range(n):
            next_i = (i + 1) % n
            v_bot1 = base_idx + (i * 2)
            v_top1 = base_idx + (i * 2) + 1
            v_bot2 = base_idx + (next_i * 2)
            v_top2 = base_idx + (next_i * 2) + 1
            # Triangle 1
            index_bytes.extend(struct.pack("<3I", v_bot1, v_bot2, v_top1))
            # Triangle 2
            index_bytes.extend(struct.pack("<3I", v_bot2, v_top2, v_top1))
            total_indices += 6

    if not vertex_bytes:
        vertex_bytes.extend(struct.pack("<3f", 0.0, 0.0, 0.0))
        min_pos = max_pos = [0.0, 0.0, 0.0]
        total_vertices = 1

    # glTF 2.0 JSON Header
    v_len = len(vertex_bytes)
    i_len = len(index_bytes)

    # Pad buffers to 4-byte boundaries
    while len(vertex_bytes) % 4 != 0:
        vertex_bytes.append(0)
    while len(index_bytes) % 4 != 0:
        index_bytes.append(0)

    bin_data = vertex_bytes + index_bytes

    gltf_dict = {
        "asset": {"version": "2.0", "generator": "osm2threejs-sdk"},
        "scene": 0,
        "scenes": [{"nodes": [0]}],
        "nodes": [{"name": city.name, "mesh": 0}],
        "meshes": [
            {
                "primitives": [
                    {
                        "attributes": {"POSITION": 0},
                        "indices": 1,
                        "mode": 4,  # TRIANGLES
                    }
                ]
            }
        ],
        "accessors": [
            {
                "bufferView": 0,
                "byteOffset": 0,
                "componentType": 5126,  # FLOAT
                "count": total_vertices,
                "type": "VEC3",
                "max": max_pos,
                "min": min_pos,
            },
            {
                "bufferView": 1,
                "byteOffset": 0,
                "componentType": 5125,  # UNSIGNED_INT
                "count": total_indices,
                "type": "SCALAR",
            },
        ],
        "bufferViews": [
            {"buffer": 0, "byteOffset": 0, "byteLength": v_len, "target": 34962},
            {"buffer": 0, "byteOffset": len(vertex_bytes), "byteLength": i_len, "target": 34963},
        ],
        "buffers": [{"byteLength": len(bin_data)}],
    }

    json_str = json.dumps(gltf_dict)
    json_bytes = json_str.encode("utf-8")
    while len(json_bytes) % 4 != 0:
        json_bytes += b" "

    # Assemble GLB (Header: 12 bytes + JSON chunk + BIN chunk)
    header = struct.pack("<4sII", b"glTF", 2, 12 + 8 + len(json_bytes) + 8 + len(bin_data))
    chunk0_header = struct.pack("<II", len(json_bytes), 0x4E4F534A)  # 'JSON'
    chunk1_header = struct.pack("<II", len(bin_data), 0x004E4942)  # 'BIN\0'

    with open(output_path, "wb") as f:
        f.write(header)
        f.write(chunk0_header)
        f.write(json_bytes)
        f.write(chunk1_header)
        f.write(bin_data)


def export_to_dxf_3d(city: CityModel3D, output_path: str) -> None:
    """Export 3D City building footprints and roads to AutoCAD DXF format."""
    center_lon, center_lat = city.bbox.center
    cos_lat = math.cos(math.radians(center_lat))
    m_per_deg_lat = 111132.0
    m_per_deg_lon = 111132.0 * cos_lat

    dxf_lines: list[str] = [
        "0",
        "SECTION",
        "2",
        "HEADER",
        "9",
        "$ACADVER",
        "1",
        "AC1009",
        "0",
        "ENDSEC",
        "0",
        "SECTION",
        "2",
        "ENTITIES",
    ]

    # Buildings (3D Polylines)
    for b in city.buildings:
        if len(b.footprint) < 2:
            continue
        dxf_lines.extend(["0", "POLYLINE", "8", "BUILDINGS", "66", "1", "70", "8"])
        for lon, lat in b.footprint:
            x = (lon - center_lon) * m_per_deg_lon
            y = (lat - center_lat) * m_per_deg_lat
            dxf_lines.extend(
                [
                    "0",
                    "VERTEX",
                    "8",
                    "BUILDINGS",
                    "10",
                    f"{x:.3f}",
                    "20",
                    f"{y:.3f}",
                    "30",
                    f"{b.height_m:.3f}",
                ]
            )
        dxf_lines.extend(["0", "SEQEND"])

    # Roads
    for r in city.roads:
        if len(r.centerline) < 2:
            continue
        dxf_lines.extend(
            ["0", "POLYLINE", "8", f"ROAD_{r.highway_type.upper()}", "66", "1", "70", "0"]
        )
        for lon, lat in r.centerline:
            x = (lon - center_lon) * m_per_deg_lon
            y = (lat - center_lat) * m_per_deg_lat
            dxf_lines.extend(
                [
                    "0",
                    "VERTEX",
                    "8",
                    f"ROAD_{r.highway_type.upper()}",
                    "10",
                    f"{x:.3f}",
                    "20",
                    f"{y:.3f}",
                    "30",
                    "0.3",
                ]
            )
        dxf_lines.extend(["0", "SEQEND"])

    dxf_lines.extend(["0", "ENDSEC", "0", "EOF"])

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(dxf_lines) + "\n")
