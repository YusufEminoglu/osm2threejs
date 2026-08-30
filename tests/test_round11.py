# -*- coding: utf-8 -*-
"""Unit tests for osm2threejs Round 11 features (Helipad Aviation Lighting & Nautical Marina)."""

from __future__ import annotations

import unittest

from osm2threejs import (
    DockBerthSpec,
    HelipadAviation3D,
    HelipadLightingProfile,
    MarinaHarborGeometry3D,
    generate_3d_helipad_mesh,
    generate_3d_marina_harbor_mesh,
)


class TestOsm2ThreeJsRound11(unittest.TestCase):
    def test_helipad_aviation_lighting(self) -> None:
        prof = HelipadLightingProfile(perimeter_lights_count=18, beacon_light_color_hex="#00ff44")
        res = generate_3d_helipad_mesh(center_coordinates=(0.0, 0.0, 30.0), touchdown_diameter_m=20.0, lighting=prof)

        self.assertIsInstance(res, HelipadAviation3D)
        self.assertEqual(res.touchdown_diameter_m, 20.0)
        self.assertEqual(res.perimeter_beacons_count, 18)
        self.assertGreater(len(res.helipad_mesh["vertices"]), 0)

        d = res.to_dict()
        self.assertIn("helipad_id", d)
        self.assertIn("beacons_count", d)

    def test_marina_harbor_dock_builder(self) -> None:
        pier_line = [(0.0, 0.0, 0.0), (100.0, 0.0, 0.0)]
        spec = DockBerthSpec(pier_length_m=100.0, num_finger_piers=6, berth_capacity_boats=12)
        buoys = [(120.0, 10.0), (120.0, -10.0)]

        res = generate_3d_marina_harbor_mesh(pier_line, dock_spec=spec, navigation_buoys_coords=buoys)

        self.assertIsInstance(res, MarinaHarborGeometry3D)
        self.assertEqual(res.total_berths_count, 12)
        self.assertEqual(res.navigation_buoys_count, 2)
        self.assertGreater(len(res.floating_docks_mesh["vertices"]), 0)

        d = res.to_dict()
        self.assertIn("harbor_id", d)
        self.assertIn("berths_count", d)
