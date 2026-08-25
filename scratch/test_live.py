# -*- coding: utf-8 -*-
import sys
import os

# Set UTF-8 encoding for stdout
sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.abspath("src"))
import osm2threejs as o3

print(">>> [1/4] Geocoding and fetching OpenStreetMap data for 'Alsancak, Izmir'...")
city = o3.from_place("Alsancak, İzmir", theme="Editorial Paper", radius_meters=500)

print(f">>> [2/4] Procedural 3D City Generated:")
print(f"    - Buildings count : {city.building_count}")
print(f"    - Roads count     : {city.road_count} ({city.total_road_km:.2f} km)")
print(f"    - Waterbodies     : {len(city.waterbodies)}")
print(f"    - Parks/Greenery  : {len(city.parks)}")
print(f"    - Trees instances : {city.tree_count}")

html_path = os.path.abspath("alsancak_3d.html")
glb_path = os.path.abspath("alsancak_3d.glb")
geojson_path = os.path.abspath("alsancak_3d.geojson")

print(">>> [3/4] Exporting 3D assets...")
city.to_html(html_path)
city.to_glb(glb_path)
city.to_geojson(geojson_path)

print(f">>> [4/4] Done! Files generated:")
print(f"    - HTML    : {html_path} ({os.path.getsize(html_path):,} bytes)")
print(f"    - GLB     : {glb_path} ({os.path.getsize(glb_path):,} bytes)")
print(f"    - GeoJSON : {geojson_path} ({os.path.getsize(geojson_path):,} bytes)")
