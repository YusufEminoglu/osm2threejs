# -*- coding: utf-8 -*-
"""Unit tests for osm2threejs Rounds 2 and 3 features."""

from __future__ import annotations

import unittest

from osm2threejs import (
    BridgeDeckMesh,
    BuildingThermalLoss,
    CityLightingRig,
    RoadGeometry3D,
    ThermalEnvelopeReport,
    TreeMesh3D,
    TreeType,
    compute_building_thermal_loss,
    generate_3d_road_mesh,
    generate_forest_canopy_mesh,
    generate_night_city_effects,
    generate_procedural_tree_mesh,
)


class TestOsm2ThreeJsRounds2And3(unittest.TestCase):
    def test_procedural_vegetation_generator(self) -> None:
        tree = generate_procedural_tree_mesh(10.0, 20.0, 0.0, tree_type=TreeType.BROADLEAF)
        self.assertIsInstance(tree, TreeMesh3D)
        self.assertGreater(len(tree.vertices), 10)
        self.assertGreater(len(tree.faces), 10)

        forest = generate_forest_canopy_mesh([(0, 0, 0), (10, 10, 0), (20, 20, 0)], tree_type=TreeType.CONIFER)
        self.assertEqual(len(forest), 3)

    def test_thermal_envelope_heat_loss(self) -> None:
        buildings = [
            {"id": "b1", "height": 15.0, "footprint": [(0, 0), (20, 0), (20, 20), (0, 20)]},
            {"id": "b2", "height": 30.0, "footprint": [(50, 50), (70, 50), (70, 70), (50, 70)]},
        ]
        rep = compute_building_thermal_loss(buildings, heating_degree_days=2500.0)
        self.assertIsInstance(rep, ThermalEnvelopeReport)
        self.assertEqual(rep.total_buildings, 2)
        self.assertGreater(rep.total_city_heat_loss_mwh, 0.0)
        self.assertIn("rating", rep.buildings[0].to_dict())

    def test_road_3d_and_bridges(self) -> None:
        coords = [(0.0, 0.0), (100.0, 0.0), (200.0, 50.0)]
        road = generate_3d_road_mesh(coords, width=10.0, is_bridge=True, bridge_elevation=8.0)
        self.assertIsInstance(road, RoadGeometry3D)
        self.assertTrue(road.is_bridge)
        self.assertIsNotNone(road.bridge_mesh)
        self.assertGreater(len(road.vertices), 4)

    def test_city_lighting_rig(self) -> None:
        roads = [[(0.0, 0.0), (100.0, 0.0), (200.0, 0.0)]]
        rig = generate_night_city_effects(roads, lamp_interval_meters=25.0)
        self.assertIsInstance(rig, CityLightingRig)
        self.assertTrue(rig.is_night_mode)
        self.assertGreater(len(rig.streetlamps), 0)
