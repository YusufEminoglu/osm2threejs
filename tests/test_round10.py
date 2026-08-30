# -*- coding: utf-8 -*-
"""Unit tests for osm2threejs Round 10 features (Wind Turbines/Solar & Pedestrian Plazas)."""

from __future__ import annotations

import unittest

from osm2threejs import (
    CrosswalkMarkingType,
    PedestrianPlazaGeometry3D,
    RenewableEnergyScene3D,
    WindTurbineSpec,
    generate_3d_pedestrian_plaza_mesh,
    generate_3d_renewable_energy_assets,
)


class TestOsm2ThreeJsRound10(unittest.TestCase):
    def test_wind_turbines_and_solar_farms(self) -> None:
        turbines = [(0.0, 0.0, 0.0), (300.0, 100.0, 0.0)]
        solar_poly = [(500.0, 500.0), (550.0, 500.0), (550.0, 530.0), (500.0, 530.0)]

        scene = generate_3d_renewable_energy_assets(
            turbine_locations=turbines,
            solar_farm_boundary_polygon=solar_poly,
            turbine_spec=WindTurbineSpec(hub_height_m=100.0, rated_power_mw=3.6),
        )

        self.assertIsInstance(scene, RenewableEnergyScene3D)
        self.assertEqual(scene.total_turbines_count, 2)
        self.assertGreater(scene.total_solar_panels_count, 0)
        self.assertGreater(scene.estimated_annual_energy_gwh, 10.0)

        d = scene.to_dict()
        self.assertIn("turbines_count", d)
        self.assertIn("annual_energy_gwh", d)

    def test_pedestrian_plaza_and_crosswalks(self) -> None:
        plaza_poly = [(0.0, 0.0), (50.0, 0.0), (50.0, 50.0), (0.0, 50.0)]
        crosswalk_lines = [[(10.0, -5.0), (10.0, 5.0)], [(30.0, -5.0), (30.0, 5.0)]]

        res = generate_3d_pedestrian_plaza_mesh(
            plaza_boundary_polygon=plaza_poly,
            crosswalk_centerlines=crosswalk_lines,
            crosswalk_width_m=4.0,
            marking_type=CrosswalkMarkingType.ZEBRA_STRIPES,
        )

        self.assertIsInstance(res, PedestrianPlazaGeometry3D)
        self.assertGreater(res.crosswalk_stripes_count, 0)
        self.assertGreater(res.tactile_warning_studs_count, 0)

        d = res.to_dict()
        self.assertIn("plaza_id", d)
        self.assertIn("stripes_count", d)
