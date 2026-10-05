# -*- coding: utf-8 -*-
"""Dynamic 3D Solar Shadow & Rooftop Irradiance Simulator for osm2threejs."""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Sequence


@dataclass(frozen=True)
class SolarPosition:
    """Astronomical sun position."""

    azimuth_degrees: float  # 0 = North, 90 = East, 180 = South, 270 = West
    elevation_degrees: float  # Angle above horizon (-90 to +90)
    zenith_degrees: float  # 90 - elevation
    is_daylight: bool


@dataclass
class BuildingSolarAssessment:
    """Solar and shadow assessment for a single building."""

    building_id: str
    height: float
    roof_area: float
    shadow_length: float
    shadow_polygon: list[tuple[float, float]]
    annual_irradiation_kwh_m2: float
    annual_energy_potential_mwh: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "building_id": self.building_id,
            "height": round(self.height, 2),
            "roof_area": round(self.roof_area, 2),
            "shadow_length": round(self.shadow_length, 2),
            "annual_irradiation_kwh_m2": round(self.annual_irradiation_kwh_m2, 1),
            "annual_energy_potential_mwh": round(self.annual_energy_potential_mwh, 2),
        }


@dataclass
class CitySolarReport:
    """Master solar potential and shadow exposure report for a 3D city scene."""

    solar_position: SolarPosition
    total_buildings: int
    total_roof_area: float
    total_annual_generation_mwh: float
    buildings: list[BuildingSolarAssessment]

    def to_dict(self) -> dict[str, Any]:
        return {
            "solar_azimuth": round(self.solar_position.azimuth_degrees, 2),
            "solar_elevation": round(self.solar_position.elevation_degrees, 2),
            "is_daylight": self.solar_position.is_daylight,
            "total_buildings": self.total_buildings,
            "total_roof_area_m2": round(self.total_roof_area, 2),
            "total_annual_generation_mwh": round(self.total_annual_generation_mwh, 2),
            "buildings": [b.to_dict() for b in self.buildings],
        }


def calculate_solar_position(
    lat: float,
    lon: float,
    dt: datetime | None = None,
) -> SolarPosition:
    """Calculate solar azimuth and elevation angles using standard solar geometry.

    Args:
        lat: Latitude in decimal degrees.
        lon: Longitude in decimal degrees.
        dt: UTC datetime. If None, uses current UTC time.
    """
    if dt is None:
        dt = datetime.now(timezone.utc)
    elif dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    # Day of year (1 - 365)
    day_of_year = dt.timetuple().tm_yday
    hour_utc = dt.hour + dt.minute / 60.0 + dt.second / 3600.0

    # Solar declination angle delta
    declination = 23.45 * math.sin(math.radians(360.0 * (284 + day_of_year) / 365.0))
    decl_rad = math.radians(declination)
    lat_rad = math.radians(lat)

    # Equation of Time (EoT in minutes)
    b = math.radians(360.0 * (day_of_year - 81) / 365.0)
    eot = 9.87 * math.sin(2 * b) - 7.53 * math.cos(b) - 1.5 * math.sin(b)

    # Solar time
    solar_time = (hour_utc * 60.0 + 4.0 * lon + eot) / 60.0
    hour_angle = math.radians(15.0 * (solar_time - 12.0))

    # Solar Elevation angle alpha
    sin_elev = math.sin(lat_rad) * math.sin(decl_rad) + math.cos(lat_rad) * math.cos(decl_rad) * math.cos(hour_angle)
    sin_elev = max(-1.0, min(1.0, sin_elev))
    elevation = math.degrees(math.asin(sin_elev))

    # Solar Azimuth angle gamma
    cos_az = (math.sin(decl_rad) * math.cos(lat_rad) - math.cos(decl_rad) * math.sin(lat_rad) * math.cos(hour_angle)) / max(1e-6, math.cos(math.radians(elevation)))
    cos_az = max(-1.0, min(1.0, cos_az))
    azimuth = math.degrees(math.acos(cos_az))
    if math.sin(hour_angle) > 0:
        azimuth = 360.0 - azimuth

    zenith = 90.0 - elevation
    is_daylight = elevation > 0.0

    return SolarPosition(
        azimuth_degrees=float(azimuth),
        elevation_degrees=float(elevation),
        zenith_degrees=float(zenith),
        is_daylight=is_daylight,
    )


def project_building_shadow(
    footprint: Sequence[tuple[float, float]],
    height: float,
    solar_pos: SolarPosition,
) -> tuple[float, list[tuple[float, float]]]:
    """Project 3D building shadow onto ground plane.

    Returns:
        Tuple of (shadow_length, shadow_ground_polygon_coords).
    """
    if not solar_pos.is_daylight or solar_pos.elevation_degrees <= 1.0 or height <= 0:
        return 0.0, list(footprint)

    elev_rad = math.radians(solar_pos.elevation_degrees)
    az_rad = math.radians(solar_pos.azimuth_degrees)

    # Shadow length = H / tan(elevation)
    shadow_len = height / math.tan(elev_rad)
    # Shadow vector direction is opposite to sun azimuth: az + 180
    opp_az = az_rad + math.pi
    dx = shadow_len * math.sin(opp_az)
    dy = shadow_len * math.cos(opp_az)

    # Project each footprint vertex by offset
    top_shadow_pts = [(x + dx, y + dy) for x, y in footprint]
    # Hull / polygon approximation: combined original + shifted points
    shadow_poly = list(footprint) + top_shadow_pts
    return float(shadow_len), shadow_poly


def compute_rooftop_solar_potential(
    buildings: list[dict[str, Any]],
    lat: float = 41.0,
    lon: float = 29.0,
    base_solar_radiation_kwh_m2: float = 1450.0,
    pv_panel_efficiency: float = 0.20,
    performance_ratio: float = 0.75,
    dt: datetime | None = None,
) -> CitySolarReport:
    """Analyze 3D solar irradiance and shadow casting for buildings in a city model.

    Args:
        buildings: List of dicts with 'id', 'footprint', 'height', 'area'.
        lat: Geographic latitude.
        lon: Geographic longitude.
        base_solar_radiation_kwh_m2: Global horizontal irradiation (GHI) in kWh/m²/year.
        pv_panel_efficiency: Solar PV panel conversion efficiency (e.g. 20% = 0.20).
        performance_ratio: BOS system performance ratio (standard 75% = 0.75).
        dt: Optional datetime for real-time shadow projection.

    Returns:
        CitySolarReport with metrics per building and total city solar yield.
    """
    solar_pos = calculate_solar_position(lat, lon, dt)
    assessments: list[BuildingSolarAssessment] = []
    total_area = 0.0
    total_mwh = 0.0

    for b in buildings:
        b_id = str(b.get("id", "bldg"))
        height = float(b.get("height", 10.0))
        area = float(b.get("area", 150.0))
        fp = b.get("footprint", [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)])

        shadow_len, shadow_poly = project_building_shadow(fp, height, solar_pos)

        # Usable rooftop area factor (approx 70% factoring HVAC, edge setbacks)
        usable_area = area * 0.70
        annual_irr = base_solar_radiation_kwh_m2
        annual_energy_kwh = usable_area * annual_irr * pv_panel_efficiency * performance_ratio
        annual_mwh = annual_energy_kwh / 1000.0

        assessments.append(
            BuildingSolarAssessment(
                building_id=b_id,
                height=height,
                roof_area=area,
                shadow_length=shadow_len,
                shadow_polygon=shadow_poly,
                annual_irradiation_kwh_m2=annual_irr,
                annual_energy_potential_mwh=annual_mwh,
            )
        )
        total_area += area
        total_mwh += annual_mwh

    return CitySolarReport(
        solar_position=solar_pos,
        total_buildings=len(buildings),
        total_roof_area=total_area,
        total_annual_generation_mwh=total_mwh,
        buildings=assessments,
    )
