# -*- coding: utf-8 -*-
"""Unit tests for osm2threejs Round 4 features (3D Water Mesh & Camera Director)."""

from __future__ import annotations

import unittest

from osm2threejs import (
    CameraKeyframe3D,
    CinematicFlythroughPath,
    GerstnerWaveParams,
    WaterSurfaceMesh3D,
    generate_animated_water_mesh,
    generate_cinematic_flythrough_path,
)


class TestOsm2ThreeJsRound4(unittest.TestCase):
    def test_water_mesh_builder(self) -> None:
        poly = [(0.0, 0.0), (100.0, 0.0), (100.0, 80.0), (0.0, 80.0)]
        water = generate_animated_water_mesh(
            poly,
            waterbody_id="lake_1",
            mesh_resolution=20.0,
            wave_params=GerstnerWaveParams(amplitude_m=0.6, wavelength_m=30.0),
        )

        self.assertIsInstance(water, WaterSurfaceMesh3D)
        self.assertGreater(len(water.vertices), 10)
        self.assertGreater(len(water.faces), 10)

        d = water.to_dict()
        self.assertIn("vertex_count", d)

    def test_camera_director_keyframes(self) -> None:
        flight = generate_cinematic_flythrough_path(
            city_center=(50.0, 50.0, 0.0),
            orbit_radius=200.0,
            duration_seconds=20.0,
            num_keyframes=12,
        )

        self.assertIsInstance(flight, CinematicFlythroughPath)
        self.assertEqual(flight.total_duration_seconds, 20.0)
        self.assertEqual(len(flight.keyframes), 13)

        json_kf = flight.to_json_keyframes()
        self.assertEqual(len(json_kf), 13)
        self.assertIn("pos", json_kf[0])
        self.assertIn("target", json_kf[0])
