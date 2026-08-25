# -*- coding: utf-8 -*-
"""Command Line Interface (CLI) for osm2threejs."""

from __future__ import annotations

import argparse
import sys
import webbrowser

from . import __version__, from_bbox, from_place, list_themes
from .fetcher import BoundingBox, geocode_place_name
from .themes import get_theme


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="osm2threejs",
        description="Headless 3D City Generator from OpenStreetMap into Three.js WebGL & 3D Assets.",
    )
    parser.add_argument("-v", "--version", action="version", version=f"osm2threejs {__version__}")

    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # 1. build
    build_p = subparsers.add_parser(
        "build", help="Generate 3D City Model from place name or bounding box"
    )
    group = build_p.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--place", type=str, help="Geocode place name (e.g. 'Kadıköy, İstanbul' or 'Eiffel Tower')"
    )
    group.add_argument("--bbox", type=str, help="Bounding box as min_lon,min_lat,max_lon,max_lat")

    build_p.add_argument(
        "--radius",
        type=float,
        default=500.0,
        help="Study radius in meters when using --place (default: 500m)",
    )
    build_p.add_argument(
        "--theme",
        type=str,
        default="Editorial Paper",
        help="Visual theme name (default: 'Editorial Paper')",
    )
    build_p.add_argument(
        "--levels",
        type=int,
        default=3,
        help="Default building levels when missing from OSM (default: 3)",
    )
    build_p.add_argument(
        "--out-html", type=str, help="Output file path for standalone Three.js HTML bundle"
    )
    build_p.add_argument(
        "--out-glb", type=str, help="Output file path for binary glTF 2.0 (.glb) 3D scene"
    )
    build_p.add_argument("--out-obj", type=str, help="Output file path for Wavefront OBJ 3D model")
    build_p.add_argument(
        "--out-geojson", type=str, help="Output file path for 3D GeoJSON FeatureCollection"
    )
    build_p.add_argument(
        "--open", action="store_true", help="Automatically open generated HTML in web browser"
    )

    # 2. themes
    subparsers.add_parser("themes", help="List all available visual themes")

    # 3. geocode
    geo_p = subparsers.add_parser("geocode", help="Geocode place name to bounding box")
    geo_p.add_argument("place", type=str, help="Place name to geocode")
    geo_p.add_argument(
        "--radius", type=float, default=500.0, help="Radius in meters (default: 500m)"
    )

    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 0

    if args.command == "themes":
        print("\n🎨 Available Visual Themes in osm2threejs:")
        for t_name in list_themes():
            t = get_theme(t_name)
            print(f"  • {t_name:<25} | Roof: {t.roof_texture:<15} | Asset: {t.asset_theme}")
        print()
        return 0

    if args.command == "geocode":
        try:
            bbox = geocode_place_name(args.place, radius_meters=args.radius)
            print(f"\n📍 Place: '{args.place}' (Radius: {args.radius}m)")
            print(
                f"   Bounding Box: {bbox.min_lon:.6f}, {bbox.min_lat:.6f}, {bbox.max_lon:.6f}, {bbox.max_lat:.6f}"
            )
            print(f"   Center: {bbox.center[0]:.6f}, {bbox.center[1]:.6f}\n")
            return 0
        except Exception as e:
            print(f"❌ Geocoding error: {e}", file=sys.stderr)
            return 1

    if args.command == "build":
        try:
            print("⚡ Fetching OpenStreetMap data and generating 3D model...")
            if args.place:
                city = from_place(
                    args.place,
                    theme=args.theme,
                    radius_meters=args.radius,
                    default_building_levels=args.levels,
                )
            else:
                parts = [float(x.strip()) for x in args.bbox.split(",")]
                if len(parts) != 4:
                    print(
                        "❌ Error: --bbox must be 4 comma-separated floats: min_lon,min_lat,max_lon,max_lat",
                        file=sys.stderr,
                    )
                    return 1
                b = BoundingBox(
                    min_lon=parts[0], min_lat=parts[1], max_lon=parts[2], max_lat=parts[3]
                )
                city = from_bbox(b, theme=args.theme, default_building_levels=args.levels)

            summary = city.summary()
            print("✅ 3D City Model generated successfully:")
            print(f"   • Buildings : {summary['building_count']}")
            print(f"   • Roads     : {summary['road_count']} ({summary['total_road_km']} km)")
            print(f"   • Water     : {summary['waterbody_count']}")
            print(f"   • Parks     : {summary['park_count']}")
            print(f"   • Trees     : {summary['tree_count']}")

            html_target = args.out_html or (
                "city.html" if not (args.out_glb or args.out_obj or args.out_geojson) else None
            )

            if html_target:
                city.to_html(html_target)
                print(f"   📄 Standalone WebGL HTML exported: {html_target}")
                if args.open:
                    webbrowser.open(html_target)

            if args.out_glb:
                city.to_glb(args.out_glb)
                print(f"   📦 Binary glTF (.glb) exported: {args.out_glb}")

            if args.out_obj:
                city.to_obj(args.out_obj)
                print(f"   📐 Wavefront OBJ exported: {args.out_obj}")

            if args.out_geojson:
                city.to_geojson(args.out_geojson)
                print(f"   🗺️ 3D GeoJSON exported: {args.out_geojson}")

            return 0
        except Exception as e:
            print(f"❌ Build failed: {e}", file=sys.stderr)
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
