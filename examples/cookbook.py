# -*- coding: utf-8 -*-
"""osm2threejs Cookbook — Procedural 3D Trees, Gerstner Water Waves & Flight Keyframes."""

import osm2threejs

# 1. Procedural 3D Tree Mesh
tree = osm2threejs.generate_procedural_tree_mesh(10.0, 20.0, 0.0, tree_type=osm2threejs.TreeType.CONIFER)
print(f"Generated 3D Tree: {len(tree.vertices)} vertices, {len(tree.faces)} faces")

# 2. 3D Animated Water Surface with Gerstner Waves
water = osm2threejs.generate_animated_water_mesh([(0, 0), (100, 0), (100, 100), (0, 100)])
print(f"Generated 3D Water Mesh: {len(water.vertices)} vertices")

# 3. Cinematic Camera Keyframe Flight
flight = osm2threejs.generate_cinematic_flythrough_path(city_center=(50, 50, 0), duration_seconds=20.0)
print(f"Generated Camera Keyframes: {len(flight.keyframes)}")
