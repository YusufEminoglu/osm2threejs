# -*- coding: utf-8 -*-
import sys
import os

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.abspath("src"))
import osm2threejs as o3

print(">>> Generating Cyberpunk Neon 3D Model for 'Galata Kulesi, Istanbul'...")
city = o3.from_place("Galata Kulesi, İstanbul", theme="Cyberpunk Neon", radius_meters=450)

print(f"    - Buildings count : {city.building_count}")
print(f"    - Roads count     : {city.road_count} ({city.total_road_km:.2f} km)")
print(f"    - Waterbodies     : {len(city.waterbodies)}")
print(f"    - Parks/Greenery  : {len(city.parks)}")

html_path = os.path.abspath("galata_cyberpunk_3d.html")
glb_path = os.path.abspath("galata_cyberpunk_3d.glb")

city.to_html(html_path)
city.to_glb(glb_path)

print(f">>> Exported:")
print(f"    - HTML : {html_path} ({os.path.getsize(html_path):,} bytes)")
print(f"    - GLB  : {glb_path} ({os.path.getsize(glb_path):,} bytes)")
