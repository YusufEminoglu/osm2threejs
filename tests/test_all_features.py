# -*- coding: utf-8 -*-
"""Comprehensive test suite for osm2threejs."""

import os
import tempfile
import unittest

from osm2threejs import (
    BoundingBox,
    generate_3d_city,
    get_theme,
    list_themes,
)
from osm2threejs.cli import main as cli_main


def fixture_osm_data() -> dict:
    """Synthetic OSM Overpass response for reliable headless tests."""
    return {
        "elements": [
            # 1. Nodes
            {"type": "node", "id": 1, "lon": 27.110, "lat": 38.410},
            {"type": "node", "id": 2, "lon": 27.112, "lat": 38.410},
            {"type": "node", "id": 3, "lon": 27.112, "lat": 38.412},
            {"type": "node", "id": 4, "lon": 27.110, "lat": 38.412},
            # Road nodes
            {"type": "node", "id": 10, "lon": 27.108, "lat": 38.408},
            {"type": "node", "id": 11, "lon": 27.115, "lat": 38.415},
            # Park nodes
            {"type": "node", "id": 20, "lon": 27.113, "lat": 38.413},
            {"type": "node", "id": 21, "lon": 27.115, "lat": 38.413},
            {"type": "node", "id": 22, "lon": 27.115, "lat": 38.415},
            {"type": "node", "id": 23, "lon": 27.113, "lat": 38.415},
            # Water nodes
            {"type": "node", "id": 30, "lon": 27.105, "lat": 38.405},
            {"type": "node", "id": 31, "lon": 27.107, "lat": 38.405},
            {"type": "node", "id": 32, "lon": 27.107, "lat": 38.407},
            # Tree node
            {"type": "node", "id": 40, "lon": 27.111, "lat": 38.411, "tags": {"natural": "tree"}},
            # 2. Building Way
            {
                "type": "way",
                "id": 101,
                "nodes": [1, 2, 3, 4, 1],
                "tags": {
                    "building": "apartments",
                    "building:levels": "6",
                    "roof:shape": "gabled",
                    "building:colour": "#e2e8f0",
                },
            },
            # 3. Highway Way
            {
                "type": "way",
                "id": 102,
                "nodes": [10, 11],
                "tags": {
                    "highway": "primary",
                    "lanes": "2",
                    "name": "Atatürk Caddesi",
                },
            },
            # 4. Park Way
            {
                "type": "way",
                "id": 103,
                "nodes": [20, 21, 22, 23, 20],
                "tags": {"leisure": "park", "name": "Kültürpark"},
            },
            # 5. Water Way
            {
                "type": "way",
                "id": 104,
                "nodes": [30, 31, 32, 30],
                "tags": {"natural": "water", "name": "İzmir Körfezi"},
            },
        ]
    }


class TestOsm2ThreeJs(unittest.TestCase):
    def test_theme_catalog(self) -> None:
        themes = list_themes()
        self.assertEqual(len(themes), 12)
        self.assertIn("Editorial Paper", themes)
        self.assertIn("Cyberpunk Neon", themes)
        self.assertIn("Blueprint Architectural", themes)
        self.assertIn("Anime Pastel", themes)

        t = get_theme("Cyberpunk Neon")
        self.assertEqual(t.name, "Cyberpunk Neon")
        self.assertTrue(t.island_color.startswith("#"))
        self.assertTrue(t.road_color.startswith("#"))

    def test_bounding_box(self) -> None:
        b = BoundingBox(min_lon=27.1, min_lat=38.4, max_lon=27.2, max_lat=38.5)
        self.assertEqual(b.center, (27.15, 38.45))
        self.assertIn("38.400000,27.100000,38.500000,27.200000", b.overpass_bbox)

    def test_procedural_generation(self) -> None:
        data = fixture_osm_data()
        city = generate_3d_city(data, theme="Editorial Paper", name="Test Izmir")

        self.assertEqual(city.name, "Test Izmir")
        self.assertEqual(city.building_count, 1)
        self.assertEqual(city.road_count, 1)
        self.assertEqual(len(city.parks), 1)
        self.assertEqual(len(city.waterbodies), 1)
        self.assertEqual(city.tree_count, 1)

        b = city.buildings[0]
        self.assertEqual(b.levels, 6)
        self.assertAlmostEqual(b.height_m, 6 * 3.2, places=1)
        self.assertEqual(b.roof_shape, "gabled")

        summary = city.summary()
        self.assertEqual(summary["building_count"], 1)
        self.assertGreater(summary["total_road_km"], 0.0)

    def test_html_bundling_and_jupyter_repr(self) -> None:
        data = fixture_osm_data()
        city = generate_3d_city(data, theme="Cyberpunk Neon")

        html_str = city.to_html(title="Cyber City")
        self.assertIn("Cyber City", html_str)
        self.assertIn("three.min.js", html_str)
        self.assertIn("OrbitControls", html_str)
        self.assertIn("SCENE_DATA", html_str)

        # Jupyter repr
        j_repr = city._repr_html_()
        self.assertIn("<iframe", j_repr)

    def test_exporters(self) -> None:
        data = fixture_osm_data()
        city = generate_3d_city(data, theme="Blueprint Architectural")

        with tempfile.TemporaryDirectory() as td:
            # 1. HTML
            html_p = os.path.join(td, "city.html")
            city.to_html(html_p)
            self.assertTrue(os.path.isfile(html_p))
            self.assertGreater(os.path.getsize(html_p), 1000)

            # 2. GLB
            glb_p = os.path.join(td, "city.glb")
            city.to_glb(glb_p)
            self.assertTrue(os.path.isfile(glb_p))
            with open(glb_p, "rb") as f:
                header = f.read(4)
                self.assertEqual(header, b"glTF")

            # 3. OBJ
            obj_p = os.path.join(td, "city.obj")
            city.to_obj(obj_p)
            self.assertTrue(os.path.isfile(obj_p))
            with open(obj_p, "r", encoding="utf-8") as f:
                content = f.read()
                self.assertIn("v ", content)
                self.assertIn("f ", content)

            # 4. GeoJSON
            geojson_p = os.path.join(td, "city.geojson")
            fc = city.to_geojson(geojson_p)
            self.assertTrue(os.path.isfile(geojson_p))
            self.assertEqual(fc["type"], "FeatureCollection")
            self.assertEqual(len(fc["features"]), 5)

            # 5. DXF
            dxf_p = os.path.join(td, "city.dxf")
            city.to_dxf(dxf_p)
            self.assertTrue(os.path.isfile(dxf_p))
            with open(dxf_p, "r", encoding="utf-8") as f:
                self.assertIn("AC1009", f.read())

    def test_cli_subcommands(self) -> None:
        # CLI themes
        res1 = cli_main(["themes"])
        self.assertEqual(res1, 0)


if __name__ == "__main__":
    unittest.main()
