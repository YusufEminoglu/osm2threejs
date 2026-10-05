# -*- coding: utf-8 -*-
"""Unit tests for osm2threejs Round 8 features (Suspension Bridges & POI Callouts)."""

from __future__ import annotations

import unittest

from osm2threejs import (
    BridgePylonType,
    BridgeStructure3D,
    POICalloutSet,
    generate_3d_poi_callouts,
    generate_3d_suspension_bridge_mesh,
)


class TestOsm2ThreeJsRound8(unittest.TestCase):
    def test_procedural_suspension_bridge(self) -> None:
        path = [(0.0, 0.0, 20.0), (1000.0, 0.0, 20.0)]
        bridge = generate_3d_suspension_bridge_mesh(path, bridge_id="GoldenGate", tower_height_m=70.0, num_hangers=20)

        self.assertIsInstance(bridge, BridgeStructure3D)
        self.assertEqual(bridge.bridge_id, "GoldenGate")
        self.assertEqual(bridge.pylon_type, BridgePylonType.H_FRAME)
        self.assertEqual(bridge.span_length_m, 1000.0)
        self.assertEqual(len(bridge.pylon_vertices), 4)
        self.assertEqual(len(bridge.cable_catenary_points), 21)

        d = bridge.to_dict()
        self.assertIn("span_length_m", d)
        self.assertIn("cable_points_count", d)

    def test_interactive_poi_callouts(self) -> None:
        landmarks = [
            {"id": "landmark_1", "name": "Hagia Sophia", "category": "CIVIC", "position": (100.0, 200.0, 30.0)},
            {"id": "landmark_2", "name": "Galata Tower", "category": "LANDMARK", "position": (500.0, 600.0, 65.0)},
        ]

        callouts = generate_3d_poi_callouts(landmarks, city_name="Istanbul 3D")

        self.assertIsInstance(callouts, POICalloutSet)
        self.assertEqual(callouts.city_name, "Istanbul 3D")
        self.assertEqual(len(callouts.pins), 2)

        data = callouts.to_threejs_overlay_json()
        self.assertIn("pins", data)
        self.assertEqual(data["total_pins"], 2)
