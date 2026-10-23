# -*- coding: utf-8 -*-
"""Public API, edge-case, and error-path tests for osm2threejs."""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from unittest import mock

import osm2threejs as o3
from osm2threejs import (
    BoundingBox,
    CityModel3D,
    RoofType,
    WeatherType,
    fetcher,
    generate_3d_city,
    generate_roof_mesh,
    generate_weather_particle_system,
    get_theme,
)
from osm2threejs.cli import main as cli_main

SIMPLE_OSM_DATA: dict = {
    "elements": [
        {"type": "node", "id": 1, "lon": 27.0, "lat": 38.0},
        {"type": "node", "id": 2, "lon": 27.01, "lat": 38.0},
        {"type": "node", "id": 3, "lon": 27.01, "lat": 38.01},
        {"type": "node", "id": 4, "lon": 27.0, "lat": 38.01},
        {
            "type": "way",
            "id": 100,
            "nodes": [1, 2, 3, 4, 1],
            "tags": {"building": "yes"},
        },
    ]
}


class _FakeResponse:
    """Minimal context-manager stub mimicking ``urllib`` HTTP responses."""

    def __init__(self, body: bytes) -> None:
        self._body = body

    def __enter__(self) -> _FakeResponse:
        return self

    def __exit__(self, *exc_info: object) -> bool:
        return False

    def read(self) -> bytes:
        return self._body


class TestTopLevelApi(unittest.TestCase):
    def test_list_themes_matches_catalog(self) -> None:
        themes = o3.list_themes()
        self.assertEqual(len(themes), 12)
        self.assertEqual(themes, o3.list_theme_names())

    def test_from_geojson_builds_city(self) -> None:
        city = o3.from_geojson(SIMPLE_OSM_DATA, name="Geo City", theme="Dark Glow")
        self.assertIsInstance(city, CityModel3D)
        self.assertEqual(city.name, "Geo City")
        self.assertEqual(city.building_count, 1)
        self.assertEqual(city.theme.name, "Dark Glow")

    def test_from_bbox_with_stubbed_fetch(self) -> None:
        with mock.patch.object(o3.OsmDataFetcher, "fetch_bbox", return_value=SIMPLE_OSM_DATA):
            city = o3.from_bbox((27.0, 38.0, 27.01, 38.01), name="Box City")
        self.assertEqual(city.name, "Box City")
        self.assertEqual(city.bbox.to_tuple(), (27.0, 38.0, 27.01, 38.01))

    def test_from_bbox_accepts_bounding_box_object(self) -> None:
        bbox = BoundingBox(27.0, 38.0, 27.01, 38.01)
        with mock.patch.object(o3.OsmDataFetcher, "fetch_bbox", return_value=SIMPLE_OSM_DATA):
            city = o3.from_bbox(bbox)
        self.assertEqual(city.bbox.to_tuple(), bbox.to_tuple())

    def test_from_place_with_stubbed_geocode(self) -> None:
        bbox = BoundingBox(27.0, 38.0, 27.01, 38.01)
        with (
            mock.patch.object(o3, "geocode_place_name", return_value=bbox),
            mock.patch.object(o3.OsmDataFetcher, "fetch_bbox", return_value=SIMPLE_OSM_DATA),
        ):
            city = o3.from_place("Stub Place", radius_meters=250.0)
        self.assertEqual(city.name, "Stub Place")
        self.assertEqual(city.building_count, 1)

    def test_bounding_box_normalises_reversed_corners(self) -> None:
        b = BoundingBox(min_lon=27.2, min_lat=38.5, max_lon=27.1, max_lat=38.4)
        self.assertEqual(b.to_tuple(), (27.1, 38.4, 27.2, 38.5))
        self.assertEqual(b.center, (27.15, 38.45))
        self.assertEqual(b.overpass_bbox, "38.400000,27.100000,38.500000,27.200000")

    def test_get_theme_fuzzy_and_unknown_fallback(self) -> None:
        self.assertEqual(get_theme("cyberpunk neon").name, "Cyberpunk Neon")
        self.assertEqual(get_theme("No Such Theme").name, "Editorial Paper")

    def test_generate_3d_city_empty_elements_fallback_bbox(self) -> None:
        city = generate_3d_city({"elements": []})
        self.assertEqual(city.building_count, 0)
        self.assertEqual(city.bbox.to_tuple(), (0.0, 0.0, 0.01, 0.01))

    def test_height_tag_parsing_and_roof_normalisation(self) -> None:
        data = {
            "elements": [
                {"type": "node", "id": 1, "lon": 0.0, "lat": 0.0},
                {"type": "node", "id": 2, "lon": 0.001, "lat": 0.0},
                {"type": "node", "id": 3, "lon": 0.001, "lat": 0.001},
                {"type": "node", "id": 4, "lon": 0.0, "lat": 0.001},
                {
                    "type": "way",
                    "id": 9,
                    "nodes": [1, 2, 3, 4, 1],
                    "tags": {
                        "building": "yes",
                        "height": "42 m",
                        "min_height": "6",
                        "roof:shape": "spaceship",
                    },
                },
            ]
        }
        city = generate_3d_city(data)
        b = city.buildings[0]
        self.assertAlmostEqual(b.height_m, 42.0)
        self.assertAlmostEqual(b.min_height_m, 6.0)
        self.assertEqual(b.roof_shape, "flat")
        self.assertGreater(city.bbox.max_lat, city.bbox.min_lat)


class TestWeatherEdgeCases(unittest.TestCase):
    def test_weather_variants_and_string_coercion(self) -> None:
        storm = generate_weather_particle_system("heavy_storm", intensity=2.0)
        self.assertEqual(storm.weather_type, WeatherType.HEAVY_STORM)
        self.assertGreater(storm.particle_count, 25000)
        self.assertIn("wind", storm.to_threejs_config())

        fog = generate_weather_particle_system(WeatherType.FOG)
        self.assertEqual(fog.weather_type, WeatherType.FOG)
        self.assertLess(fog.fall_velocity_ms, 1.0)

        fallback = generate_weather_particle_system("not-a-weather")
        self.assertEqual(fallback.weather_type, WeatherType.RAIN)


class TestRoofEdgeCases(unittest.TestCase):
    def test_flat_roof_and_invalid_type_fallback(self) -> None:
        square = [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)]
        flat = generate_roof_mesh(square, base_height=8.0, roof_type="flat", roof_height=0.0)
        self.assertEqual(flat.roof_type, RoofType.FLAT)
        self.assertEqual(len(flat.faces), 4)

        invalid = generate_roof_mesh(square, base_height=8.0, roof_type="not-a-roof")
        self.assertEqual(invalid.roof_type, RoofType.GABLED)
        self.assertGreater(invalid.area, 0.0)

    def test_degenerate_ring_returns_empty_mesh(self) -> None:
        degenerate = generate_roof_mesh([(0.0, 0.0), (1.0, 1.0)], base_height=5.0)
        self.assertEqual(degenerate.height, 0.0)
        self.assertEqual(degenerate.faces, [])


class TestFetcherPaths(unittest.TestCase):
    def test_build_study_query_contains_bbox(self) -> None:
        query = fetcher.OsmDataFetcher().build_study_query(BoundingBox(1.0, 2.0, 3.0, 4.0))
        self.assertIn("2.000000,1.000000,4.000000,3.000000", query)
        self.assertIn('way["building"]', query)

    def test_cache_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            with mock.patch.object(fetcher, "_get_cache_dir", return_value=td):
                fetcher._save_cached_query("roundtrip", {"elements": []})
                self.assertEqual(fetcher._get_cached_query("roundtrip"), {"elements": []})
                self.assertIsNone(fetcher._get_cached_query("missing-key"))

    def test_query_overpass_success_is_cached(self) -> None:
        resp = _FakeResponse(json.dumps({"elements": []}).encode("utf-8"))
        with tempfile.TemporaryDirectory() as td:
            with (
                mock.patch.object(fetcher, "_get_cache_dir", return_value=td),
                mock.patch.object(fetcher.urllib.request, "urlopen", return_value=resp),
            ):
                data = fetcher.query_overpass("success-query", endpoints=("http://mirror",))
                self.assertEqual(data, {"elements": []})
                self.assertEqual(fetcher._get_cached_query("success-query"), {"elements": []})

    def test_query_overpass_all_mirrors_fail(self) -> None:
        with (
            mock.patch.object(fetcher.urllib.request, "urlopen", side_effect=OSError("down")),
            mock.patch.object(fetcher.time, "sleep", return_value=None),
        ):
            with self.assertRaises(fetcher.OsmFetchError):
                fetcher.query_overpass("fail-query", endpoints=("http://mirror",), use_cache=False)

    def test_geocode_place_name_success(self) -> None:
        resp = _FakeResponse(json.dumps([{"lat": "41.0", "lon": "29.0"}]).encode("utf-8"))
        with mock.patch.object(fetcher.urllib.request, "urlopen", return_value=resp):
            bbox = fetcher.geocode_place_name("Istanbul", radius_meters=1000.0)
        self.assertAlmostEqual(bbox.center[0], 29.0, places=6)
        self.assertAlmostEqual(bbox.center[1], 41.0, places=6)

    def test_geocode_place_name_no_results(self) -> None:
        resp = _FakeResponse(b"[]")
        with mock.patch.object(fetcher.urllib.request, "urlopen", return_value=resp):
            with self.assertRaises(fetcher.OsmFetchError):
                fetcher.geocode_place_name("Nowhere")


class TestCliPaths(unittest.TestCase):
    def test_no_command_returns_zero(self) -> None:
        self.assertEqual(cli_main([]), 0)

    def test_invalid_bbox_returns_error(self) -> None:
        self.assertEqual(cli_main(["build", "--bbox", "1,2,3"]), 1)

    def test_geocode_error_returns_one(self) -> None:
        with mock.patch("osm2threejs.cli.geocode_place_name", side_effect=RuntimeError("boom")):
            self.assertEqual(cli_main(["geocode", "Nowhere"]), 1)

    def test_build_from_bbox_success(self) -> None:
        with (
            mock.patch.object(o3.OsmDataFetcher, "fetch_bbox", return_value=SIMPLE_OSM_DATA),
            tempfile.TemporaryDirectory() as td,
        ):
            out = os.path.join(td, "city.html")
            rc = cli_main(["build", "--bbox", "27.0,38.0,27.01,38.01", "--out-html", out])
            self.assertEqual(rc, 0)
            self.assertTrue(os.path.isfile(out))

    def test_build_from_place_opens_browser(self) -> None:
        stub_city = generate_3d_city(SIMPLE_OSM_DATA, name="Stub")
        with (
            mock.patch("osm2threejs.cli.from_place", return_value=stub_city),
            mock.patch("osm2threejs.cli.webbrowser.open") as open_mock,
            tempfile.TemporaryDirectory() as td,
        ):
            out = os.path.join(td, "place.html")
            rc = cli_main(["build", "--place", "Stub", "--out-html", out, "--open"])
            self.assertEqual(rc, 0)
            self.assertTrue(os.path.isfile(out))
            open_mock.assert_called_once()

    def test_build_exports_all_formats(self) -> None:
        stub_city = generate_3d_city(SIMPLE_OSM_DATA)
        with (
            mock.patch("osm2threejs.cli.from_bbox", return_value=stub_city),
            tempfile.TemporaryDirectory() as td,
        ):
            glb = os.path.join(td, "a.glb")
            obj = os.path.join(td, "a.obj")
            geojson = os.path.join(td, "a.geojson")
            rc = cli_main(
                [
                    "build",
                    "--bbox",
                    "27.0,38.0,27.01,38.01",
                    "--out-glb",
                    glb,
                    "--out-obj",
                    obj,
                    "--out-geojson",
                    geojson,
                ]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(os.path.isfile(glb))
            self.assertTrue(os.path.isfile(obj))
            self.assertTrue(os.path.isfile(geojson))


class TestExporterEdgeCases(unittest.TestCase):
    def test_glb_export_empty_city(self) -> None:
        city = generate_3d_city({"elements": []})
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "empty.glb")
            city.to_glb(path)
            with open(path, "rb") as f:
                self.assertEqual(f.read(4), b"glTF")

    def test_geojson_export_without_path_returns_mapping(self) -> None:
        city = generate_3d_city(SIMPLE_OSM_DATA)
        fc = city.to_geojson()
        self.assertEqual(fc["type"], "FeatureCollection")
        self.assertGreaterEqual(len(fc["features"]), 1)


if __name__ == "__main__":
    unittest.main()
