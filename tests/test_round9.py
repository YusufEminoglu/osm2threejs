# -*- coding: utf-8 -*-
"""Unit tests for osm2threejs Round 9 features (Rail Tracks & Noise Barrier Soundwalls)."""

from __future__ import annotations

import unittest

from osm2threejs import (
    AcousticPanelMaterial,
    NoiseBarrierMesh3D,
    RailTrackProfile,
    RailwayGeometry3D,
    generate_3d_noise_barrier_mesh,
    generate_3d_railway_mesh,
)


class TestOsm2ThreeJsRound9(unittest.TestCase):
    def test_3d_railway_mesh_generator(self) -> None:
        centerline = [(0.0, 0.0, 5.0), (100.0, 0.0, 5.0), (200.0, 50.0, 6.0)]
        profile = RailTrackProfile(gauge_width_m=1.435)

        rail = generate_3d_railway_mesh(centerline, track_id="Metro_M1", profile=profile)

        self.assertIsInstance(rail, RailwayGeometry3D)
        self.assertEqual(rail.track_id, "Metro_M1")
        self.assertGreater(rail.track_length_m, 200.0)
        self.assertEqual(len(rail.rail_left_vertices), 3)
        self.assertEqual(len(rail.rail_right_vertices), 3)
        self.assertGreater(rail.sleepers_count, 100)

        d = rail.to_dict()
        self.assertIn("track_id", d)
        self.assertIn("track_length_m", d)
        self.assertIn("sleepers", d)

    def test_acoustic_noise_barrier_mesh(self) -> None:
        path = [(0.0, 0.0, 0.0), (250.0, 0.0, 0.0)]
        wall = generate_3d_noise_barrier_mesh(
            path,
            barrier_id="Highway_Soundwall",
            barrier_height_m=4.0,
            material=AcousticPanelMaterial.PERFORATED_ALUMINUM,
        )

        self.assertIsInstance(wall, NoiseBarrierMesh3D)
        self.assertEqual(wall.height_m, 4.0)
        self.assertEqual(wall.total_barrier_length_m, 250.0)
        self.assertEqual(wall.material, AcousticPanelMaterial.PERFORATED_ALUMINUM)
        self.assertEqual(wall.sound_transmission_class_stc_db, 36.0)

        d = wall.to_dict()
        self.assertIn("barrier_id", d)
        self.assertIn("material", d)
        self.assertIn("stc_db", d)
