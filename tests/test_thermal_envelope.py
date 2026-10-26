# -*- coding: utf-8 -*-
"""Hand-computed checks and branch coverage for the thermal envelope profiler."""

from __future__ import annotations

import pytest

from osm2threejs import compute_building_thermal_loss

SQUARE = [(0.0, 0.0), (20.0, 0.0), (20.0, 20.0), (0.0, 20.0)]


def test_hand_computed_box() -> None:
    """20 x 20 x 15 m box: walls 1200 m2 (30 % glazed), roof 400 m2."""
    rep = compute_building_thermal_loss([{"id": "b", "height": 15.0, "footprint": SQUARE}])
    b = rep.buildings[0]
    h_t = 840.0 * 0.60 + 360.0 * 1.80 + 400.0 * 0.35  # 1292 W/K
    assert b.volume_m3 == pytest.approx(6000.0)
    assert b.total_envelope_area_m2 == pytest.approx(1600.0)
    assert b.compactness_ratio_s_v == pytest.approx(1600.0 / 6000.0)
    assert b.annual_heat_loss_kwh == pytest.approx(h_t * 2400.0 * 24.0 / 1000.0)
    assert b.annual_cooling_load_kwh == pytest.approx(
        (h_t * 800.0 * 24.0 * 0.70 + 360.0 * 150.0) / 1000.0
    )
    d = rep.to_dict()
    assert d["total_buildings"] == 1
    assert d["total_city_heat_loss_mwh"] == pytest.approx(round(74.4192, 2))
    assert d["buildings"][0]["rating"] == "B"


def test_closed_ring_matches_open_ring() -> None:
    """Repeating the first vertex (GeoJSON/OSM style) changes nothing."""
    open_rep = compute_building_thermal_loss([{"height": 9.0, "footprint": SQUARE}])
    closed_rep = compute_building_thermal_loss([{"height": 9.0, "footprint": SQUARE + [SQUARE[0]]}])
    assert open_rep.to_dict() == closed_rep.to_dict()


@pytest.mark.parametrize(
    "hdd, rating",
    [(2000.0, "A"), (2400.0, "B"), (5000.0, "C"), (8000.0, "D"), (11000.0, "E"), (15000.0, "F")],
)
def test_rating_bands(hdd: float, rating: str) -> None:
    """EPC value is heat loss per floor area (37.2 kWh/m2 at 2400 HDD for the box)."""
    rep = compute_building_thermal_loss(
        [{"height": 15.0, "footprint": SQUARE}], heating_degree_days=hdd
    )
    assert rep.buildings[0].energy_performance_rating == rating


def test_degenerate_footprint_and_empty_input() -> None:
    """Fewer than 3 vertices give a zero-size envelope; no buildings give zeros."""
    rep = compute_building_thermal_loss([{"height": 10.0, "footprint": [(0.0, 0.0), (5.0, 0.0)]}])
    b = rep.buildings[0]
    assert b.volume_m3 == 0.0 and b.total_envelope_area_m2 == 0.0
    assert b.annual_heat_loss_kwh == 0.0
    empty = compute_building_thermal_loss([])
    assert empty.total_buildings == 0
    assert empty.mean_compactness_ratio == 0.0
