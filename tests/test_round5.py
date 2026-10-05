# -*- coding: utf-8 -*-
"""Unit tests for osm2threejs Round 5 features (Traffic Flow & Ground Shadow Baking)."""

from __future__ import annotations

import unittest

from osm2threejs import (
    ShadowBakeResult,
    TrafficSimulationMesh,
    bake_static_building_shadows,
    generate_traffic_flow_geometry,
)


class TestOsm2ThreeJsRound5(unittest.TestCase):
    def test_traffic_flow_simulation(self) -> None:
        road = [
            (0.0, 0.0, 0.0),
            (200.0, 0.0, 0.0),
            (400.0, 100.0, 5.0),
        ]

        sim = generate_traffic_flow_geometry(road, traffic_density_per_km=30.0, flow_speed_kmh=60.0)
        self.assertIsInstance(sim, TrafficSimulationMesh)
        self.assertGreater(sim.total_vehicles, 0)
        self.assertEqual(len(sim.vehicles), sim.total_vehicles)

        instances = sim.to_threejs_instances()
        self.assertEqual(len(instances), sim.total_vehicles)
        self.assertIn("pos", instances[0])
        self.assertIn("heading", instances[0])

    def test_ground_shadow_baking(self) -> None:
        footprints = [
            [(0.0, 0.0), (20.0, 0.0), (20.0, 20.0), (0.0, 20.0)],
            [(50.0, 50.0), (80.0, 50.0), (80.0, 80.0), (50.0, 80.0)],
        ]
        heights = [30.0, 45.0]

        shadows = bake_static_building_shadows(
            footprints, heights, sun_azimuth_deg=180.0, sun_elevation_deg=45.0
        )

        self.assertIsInstance(shadows, ShadowBakeResult)
        self.assertEqual(len(shadows.shadow_polygons), 2)
        self.assertGreater(shadows.total_shadow_area_m2, 0.0)

        geojson = shadows.to_geojson()
        self.assertEqual(geojson["type"], "FeatureCollection")
        self.assertEqual(len(geojson["features"]), 2)
