# -*- coding: utf-8 -*-
"""3D Volumetric City Building Heat Loss & Thermal Envelope Profiler for osm2threejs."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Sequence


@dataclass
class BuildingThermalLoss:
    building_id: str
    volume_m3: float
    total_envelope_area_m2: float
    compactness_ratio_s_v: float  # Envelope area / Volume (1/m)
    annual_heat_loss_kwh: float
    annual_cooling_load_kwh: float
    energy_performance_rating: str  # 'A', 'B', 'C', 'D', 'E', 'F', 'G'
    wall_u_value: float
    roof_u_value: float
    window_to_wall_ratio: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "building_id": self.building_id,
            "volume_m3": round(self.volume_m3, 1),
            "envelope_area_m2": round(self.total_envelope_area_m2, 1),
            "compactness_s_v": round(self.compactness_ratio_s_v, 3),
            "annual_heat_loss_kwh": round(self.annual_heat_loss_kwh, 1),
            "annual_cooling_load_kwh": round(self.annual_cooling_load_kwh, 1),
            "rating": self.energy_performance_rating,
        }


@dataclass
class ThermalEnvelopeReport:
    total_buildings: int
    total_city_heat_loss_mwh: float
    total_city_cooling_load_mwh: float
    mean_compactness_ratio: float
    buildings: list[BuildingThermalLoss]

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_buildings": self.total_buildings,
            "total_city_heat_loss_mwh": round(self.total_city_heat_loss_mwh, 2),
            "total_city_cooling_load_mwh": round(self.total_city_cooling_load_mwh, 2),
            "mean_compactness_ratio": round(self.mean_compactness_ratio, 3),
            "buildings": [b.to_dict() for b in self.buildings],
        }


def _calc_footprint_perimeter_and_area(footprint: Sequence[tuple[float, float]]) -> tuple[float, float]:
    n = len(footprint)
    if n < 3:
        return 0.0, 0.0
    perimeter = 0.0
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        dx = footprint[j][0] - footprint[i][0]
        dy = footprint[j][1] - footprint[i][1]
        perimeter += math.hypot(dx, dy)
        area += footprint[i][0] * footprint[j][1] - footprint[j][0] * footprint[i][1]
    return perimeter, abs(area) / 2.0


def compute_building_thermal_loss(
    buildings: list[dict[str, Any]],
    heating_degree_days: float = 2400.0,
    cooling_degree_days: float = 800.0,
    default_wall_u_val: float = 0.60,  # W/m2.K
    default_roof_u_val: float = 0.35,  # W/m2.K
    default_window_u_val: float = 1.80, # W/m2.K
    window_to_wall_ratio: float = 0.30,
) -> ThermalEnvelopeReport:
    """Calculate 3D thermal transmission heat loss and cooling loads across urban buildings."""
    assessments: list[BuildingThermalLoss] = []
    tot_heat_kwh = 0.0
    tot_cool_kwh = 0.0
    compactness_list: list[float] = []

    for b in buildings:
        b_id = str(b.get("id", "bldg"))
        height = float(b.get("height", 12.0))
        fp = b.get("footprint", [(0.0, 0.0), (15.0, 0.0), (15.0, 15.0), (0.0, 15.0)])

        perim, roof_area = _calc_footprint_perimeter_and_area(fp)
        wall_gross_area = perim * height
        window_area = wall_gross_area * window_to_wall_ratio
        opaque_wall_area = wall_gross_area - window_area
        total_envelope = wall_gross_area + roof_area
        volume = roof_area * height

        compactness = total_envelope / max(1.0, volume)
        compactness_list.append(compactness)

        # Transmission Heat Transfer Coefficient H_T (W/K)
        h_t = (opaque_wall_area * default_wall_u_val + window_area * default_window_u_val + roof_area * default_roof_u_val)

        # Annual Heating Loss Q_heat (kWh) = (H_T * HDD * 24) / 1000
        q_heat = (h_t * heating_degree_days * 24.0) / 1000.0
        # Cooling load approximation factoring solar gain on windows
        q_cool = (h_t * cooling_degree_days * 24.0 * 0.70 + window_area * 150.0) / 1000.0

        # EPC rating (kWh/m2.yr)
        epc_val = q_heat / max(1.0, roof_area * max(1, int(height / 3.0)))
        if epc_val < 35:
            rating = "A"
        elif epc_val < 70:
            rating = "B"
        elif epc_val < 110:
            rating = "C"
        elif epc_val < 160:
            rating = "D"
        elif epc_val < 220:
            rating = "E"
        else:
            rating = "F"

        assessments.append(
            BuildingThermalLoss(
                building_id=b_id,
                volume_m3=volume,
                total_envelope_area_m2=total_envelope,
                compactness_ratio_s_v=compactness,
                annual_heat_loss_kwh=q_heat,
                annual_cooling_load_kwh=q_cool,
                energy_performance_rating=rating,
                wall_u_value=default_wall_u_val,
                roof_u_value=default_roof_u_val,
                window_to_wall_ratio=window_to_wall_ratio,
            )
        )
        tot_heat_kwh += q_heat
        tot_cool_kwh += q_cool

    mean_compactness = sum(compactness_list) / max(1, len(compactness_list))

    return ThermalEnvelopeReport(
        total_buildings=len(buildings),
        total_city_heat_loss_mwh=tot_heat_kwh / 1000.0,
        total_city_cooling_load_mwh=tot_cool_kwh / 1000.0,
        mean_compactness_ratio=mean_compactness,
        buildings=assessments,
    )
