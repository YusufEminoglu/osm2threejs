# -*- coding: utf-8 -*-
"""Unit tests for procedural roofs and 3D solar shadow simulator in osm2threejs."""

from __future__ import annotations

import unittest
from datetime import datetime, timezone

from osm2threejs import (
    CitySolarReport,
    RoofMesh3D,
    RoofType,
    SolarPosition,
    calculate_solar_position,
    compute_rooftop_solar_potential,
    generate_roof_mesh,
    project_building_shadow,
)


class TestRoofAndSolar(unittest.TestCase):
    def setUp(self) -> None:
        self.square_footprint = [(0.0, 0.0), (20.0, 0.0), (20.0, 20.0), (0.0, 20.0)]
        self.rect_footprint = [(0.0, 0.0), (40.0, 0.0), (40.0, 15.0), (0.0, 15.0)]

    def test_gabled_and_hipped_roof_mesh_generation(self) -> None:
        # Gabled
        gabled = generate_roof_mesh(self.rect_footprint, base_height=12.0, roof_type=RoofType.GABLED, roof_height=4.0)
        self.assertEqual(gabled.roof_type, RoofType.GABLED)
        self.assertGreater(len(gabled.vertices), 4)
        self.assertGreater(len(gabled.faces), 0)
        self.assertGreater(gabled.area, 0.0)

        # Hipped
        hipped = generate_roof_mesh(self.rect_footprint, base_height=12.0, roof_type=RoofType.HIPPED, roof_height=3.5)
        self.assertEqual(hipped.roof_type, RoofType.HIPPED)
        self.assertGreater(len(hipped.faces), 0)

        # Pyramidal
        pyramidal = generate_roof_mesh(self.square_footprint, base_height=10.0, roof_type=RoofType.PYRAMIDAL, roof_height=5.0)
        self.assertEqual(pyramidal.roof_type, RoofType.PYRAMIDAL)
        self.assertEqual(len(pyramidal.faces), 4)

        # Mansard & Skillion
        mansard = generate_roof_mesh(self.square_footprint, base_height=10.0, roof_type=RoofType.MANSARD)
        self.assertGreater(len(mansard.faces), 4)

        skillion = generate_roof_mesh(self.square_footprint, base_height=10.0, roof_type=RoofType.SKILLION)
        self.assertGreater(len(skillion.faces), 0)

    def test_solar_position_and_shadow_projection(self) -> None:
        # Noon in Istanbul during summer solstice (June 21)
        dt = datetime(2026, 6, 21, 10, 0, 0, tzinfo=timezone.utc)  # ~13:00 local
        pos = calculate_solar_position(lat=41.0, lon=29.0, dt=dt)

        self.assertIsInstance(pos, SolarPosition)
        self.assertTrue(pos.is_daylight)
        self.assertGreater(pos.elevation_degrees, 45.0)
        self.assertGreater(pos.azimuth_degrees, 90.0)

        # Shadow projection of 15m building
        shadow_len, shadow_poly = project_building_shadow(self.square_footprint, height=15.0, solar_pos=pos)
        self.assertGreater(shadow_len, 0.0)
        self.assertGreaterEqual(len(shadow_poly), 4)

    def test_compute_rooftop_solar_potential(self) -> None:
        buildings = [
            {"id": "b1", "height": 18.0, "area": 300.0, "footprint": self.rect_footprint},
            {"id": "b2", "height": 12.0, "area": 400.0, "footprint": self.square_footprint},
        ]
        report = compute_rooftop_solar_potential(buildings, lat=41.0, lon=29.0)

        self.assertIsInstance(report, CitySolarReport)
        self.assertEqual(report.total_buildings, 2)
        self.assertEqual(report.total_roof_area, 700.0)
        self.assertGreater(report.total_annual_generation_mwh, 0.0)

        d = report.to_dict()
        self.assertIn("total_annual_generation_mwh", d)
        self.assertEqual(len(d["buildings"]), 2)
