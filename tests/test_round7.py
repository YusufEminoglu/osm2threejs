# -*- coding: utf-8 -*-
"""Unit tests for osm2threejs Round 7 features (Tunnel Builder & Billboard LOD Manager)."""

from __future__ import annotations

import unittest

from osm2threejs import (
    BuildingLODSet,
    LODDistanceConfig,
    TunnelGeometry3D,
    generate_3d_tunnel_mesh,
    generate_lod_building_levels,
)


class TestOsm2ThreeJsRound7(unittest.TestCase):
    def test_tunnel_subsurface_builder(self) -> None:
        path = [(0.0, 0.0, 0.0), (100.0, 0.0, 0.0), (200.0, 0.0, 0.0)]
        tunnel = generate_3d_tunnel_mesh(path, tunnel_radius_m=5.0, radial_segments=8)

        self.assertIsInstance(tunnel, TunnelGeometry3D)
        self.assertEqual(tunnel.tunnel_id, "tunnel_main")
        self.assertEqual(tunnel.inner_radius_m, 5.0)
        self.assertEqual(len(tunnel.vertices), 3 * 8)
        self.assertEqual(len(tunnel.faces), 2 * 8 * 2)  # 2 segments * 8 quads * 2 tris
        self.assertGreater(tunnel.tunnel_length_m, 150.0)

        d = tunnel.to_dict()
        self.assertIn("tunnel_id", d)
        self.assertIn("length_m", d)

    def test_billboard_lod_manager(self) -> None:
        footprint = [(0.0, 0.0), (30.0, 0.0), (30.0, 20.0), (0.0, 20.0)]
        cfg = LODDistanceConfig(lod0_max_distance_m=200.0, lod1_max_distance_m=600.0)
        lod_set = generate_lod_building_levels(footprint, building_id="Tower_Alpha", height_m=50.0, distance_config=cfg)

        self.assertIsInstance(lod_set, BuildingLODSet)
        self.assertEqual(lod_set.building_id, "Tower_Alpha")
        self.assertGreater(lod_set.lod0_vertices_count, lod_set.lod1_vertices_count)
        self.assertEqual(lod_set.lod1_vertices_count, 8)
        self.assertEqual(lod_set.lod2_billboard_center[2], 25.0)

        node = lod_set.to_threejs_lod_node()
        self.assertIn("lod0_vcount", node)
        self.assertIn("lod2_billboard", node)
