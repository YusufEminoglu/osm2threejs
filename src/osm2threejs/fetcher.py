# -*- coding: utf-8 -*-
"""Overpass OSM data fetcher, Nominatim geocoder, and disk cache manager."""

from __future__ import annotations

import hashlib
import json
import math
import os
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any

OVERPASS_MIRRORS = (
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
)
NOMINATIM_ENDPOINT = "https://nominatim.openstreetmap.org/search"
DEFAULT_USER_AGENT = "osm2threejs-sdk/0.1.0 (https://github.com/YusufEminoglu/osm2threejs)"
CACHE_TTL_SECONDS = 7 * 24 * 3600  # 1 week


class OsmFetchError(RuntimeError):
    """Raised when OSM Overpass or Nominatim fetch fails."""


@dataclass(frozen=True)
class BoundingBox:
    """Geographic bounding box in WGS84 (EPSG:4326)."""

    min_lon: float
    min_lat: float
    max_lon: float
    max_lat: float

    def __post_init__(self) -> None:
        if self.min_lon > self.max_lon:
            object.__setattr__(self, "min_lon", self.max_lon)
            object.__setattr__(self, "max_lon", self.min_lon)
        if self.min_lat > self.max_lat:
            object.__setattr__(self, "min_lat", self.max_lat)
            object.__setattr__(self, "max_lat", self.min_lat)

    @property
    def center(self) -> tuple[float, float]:
        return (self.min_lon + self.max_lon) / 2.0, (self.min_lat + self.max_lat) / 2.0

    @property
    def overpass_bbox(self) -> str:
        """Format as (south, west, north, east) for Overpass QL."""
        return f"{self.min_lat:.6f},{self.min_lon:.6f},{self.max_lat:.6f},{self.max_lon:.6f}"

    def to_tuple(self) -> tuple[float, float, float, float]:
        return (self.min_lon, self.min_lat, self.max_lon, self.max_lat)


def _get_cache_dir() -> str:
    path = os.path.join(tempfile.gettempdir(), "osm2threejs_cache")
    os.makedirs(path, exist_ok=True)
    return path


def _get_cached_query(query: str) -> dict[str, Any] | None:
    digest = hashlib.sha256(query.encode("utf-8")).hexdigest()[:40]
    path = os.path.join(_get_cache_dir(), f"{digest}.json")
    if not os.path.isfile(path):
        return None
    try:
        if time.time() - os.path.getmtime(path) > CACHE_TTL_SECONDS:
            os.remove(path)
            return None
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _save_cached_query(query: str, data: dict[str, Any]) -> None:
    digest = hashlib.sha256(query.encode("utf-8")).hexdigest()[:40]
    path = os.path.join(_get_cache_dir(), f"{digest}.json")
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f)
    except Exception:
        pass


def geocode_place_name(place_name: str, radius_meters: float = 500.0) -> BoundingBox:
    """Geocode a place query into a BoundingBox using OpenStreetMap Nominatim."""
    params = {
        "q": place_name,
        "format": "json",
        "limit": 1,
    }
    url = f"{NOMINATIM_ENDPOINT}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": DEFAULT_USER_AGENT})

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            results = json.loads(resp.read().decode("utf-8"))
            if not results:
                raise OsmFetchError(f"No location found for place name: '{place_name}'")
            lat = float(results[0]["lat"])
            lon = float(results[0]["lon"])
    except Exception as e:
        if isinstance(e, OsmFetchError):
            raise
        raise OsmFetchError(f"Nominatim geocoding failed for '{place_name}': {e}") from e

    # Convert radius_meters into delta degrees
    lat_deg_m = 111132.0
    lon_deg_m = 111132.0 * math.cos(math.radians(lat))
    d_lat = radius_meters / lat_deg_m
    d_lon = radius_meters / max(1e-5, lon_deg_m)

    return BoundingBox(
        min_lon=lon - d_lon,
        min_lat=lat - d_lat,
        max_lon=lon + d_lon,
        max_lat=lat + d_lat,
    )


def query_overpass(
    query_str: str,
    timeout: int = 60,
    endpoints: tuple[str, ...] = OVERPASS_MIRRORS,
    use_cache: bool = True,
) -> dict[str, Any]:
    """Execute an Overpass QL query across available mirrors with automatic retry and caching."""
    if use_cache:
        cached = _get_cached_query(query_str)
        if cached is not None:
            return cached

    encoded_query = urllib.parse.urlencode({"data": query_str}).encode("utf-8")
    last_error: Exception | None = None

    for endpoint in endpoints:
        for _attempt in range(2):
            try:
                req = urllib.request.Request(
                    endpoint,
                    data=encoded_query,
                    headers={
                        "User-Agent": DEFAULT_USER_AGENT,
                        "Accept": "application/json",
                    },
                )
                with urllib.request.urlopen(req, timeout=timeout) as response:
                    raw_data = response.read().decode("utf-8")
                    data = json.loads(raw_data)
                    if use_cache:
                        _save_cached_query(query_str, data)
                    return data
            except Exception as exc:
                last_error = exc
                time.sleep(1.0)

    raise OsmFetchError(f"All Overpass mirrors failed. Last error: {last_error}")


class OsmDataFetcher:
    """High-performance OpenStreetMap Overpass client for 3D city scene elements."""

    def __init__(self, endpoints: tuple[str, ...] = OVERPASS_MIRRORS) -> None:
        self.endpoints = endpoints

    def build_study_query(self, bbox: BoundingBox) -> str:
        """Construct comprehensive Overpass QL query for buildings, roads, parks, water, and trees."""
        b = bbox.overpass_bbox
        return f"""
        [out:json][timeout:60];
        (
          // 1. Buildings & Roofs
          way["building"]({b});
          relation["building"]({b});

          // 2. Road Network
          way["highway"]({b});

          // 3. Green Spaces & Parks
          way["leisure"="park"]({b});
          way["landuse"~"grass|forest|meadow|village_green"]({b});
          relation["leisure"="park"]({b});
          relation["landuse"~"grass|forest|meadow|village_green"]({b});

          // 4. Waterbodies
          way["natural"="water"]({b});
          way["waterway"]({b});
          relation["natural"="water"]({b});
          relation["waterway"]({b});

          // 5. Trees & Natural Points
          node["natural"="tree"]({b});
          node["amenity"="fountain"]({b});
        );
        out body;
        >;
        out skel qt;
        """

    def fetch_bbox(self, bbox: BoundingBox) -> dict[str, Any]:
        """Fetch and assemble raw OSM JSON for the given bounding box."""
        query = self.build_study_query(bbox)
        return query_overpass(query, endpoints=self.endpoints)
