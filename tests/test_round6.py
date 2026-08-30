# -*- coding: utf-8 -*-
"""Unit tests for osm2threejs Round 6 features (Street Furniture & Weather Particle FX)."""

from __future__ import annotations

import unittest

from osm2threejs import (
    FurniturePlacementReport,
    StreetFurnitureInstance,
    WeatherParticleFX,
    WeatherType,
    generate_weather_particle_system,
    instantiate_street_furniture,
)


class TestOsm2ThreeJsRound6(unittest.TestCase):
    def test_street_furniture_instancer(self) -> None:
        road = [(0.0, 0.0, 0.0), (100.0, 0.0, 0.0), (200.0, 0.0, 0.0)]
        rep = instantiate_street_furniture(
            road,
            road_width_m=8.0,
            streetlight_spacing_m=20.0,
            bench_spacing_m=30.0,
            include_hydrants=True,
        )

        self.assertIsInstance(rep, FurniturePlacementReport)
        self.assertGreater(rep.total_furniture_count, 0)
        self.assertGreater(rep.streetlight_count, 0)
        self.assertGreater(rep.bench_count, 0)
        self.assertEqual(rep.hydrant_count, 1)

        instances = rep.to_threejs_instances()
        self.assertEqual(len(instances), rep.total_furniture_count)
        self.assertIn("pos", instances[0])
        self.assertIn("type", instances[0])

    def test_weather_particle_fx(self) -> None:
        # Rain
        rain_fx = generate_weather_particle_system(WeatherType.RAIN, intensity=1.5, wind_speed_ms=8.0)
        self.assertIsInstance(rain_fx, WeatherParticleFX)
        self.assertEqual(rain_fx.weather_type, WeatherType.RAIN)
        self.assertGreater(rain_fx.particle_count, 10000)
        self.assertGreater(rain_fx.fall_velocity_ms, 15.0)

        # Snow
        snow_fx = generate_weather_particle_system(WeatherType.SNOW, intensity=1.0)
        self.assertEqual(snow_fx.weather_type, WeatherType.SNOW)
        self.assertLess(snow_fx.fall_velocity_ms, 5.0)

        d = rain_fx.to_threejs_config()
        self.assertEqual(d["type"], "RAIN")
        self.assertIn("wind", d)
