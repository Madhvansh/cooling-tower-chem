"""Tests for the CoolingTower convenience object."""

import pytest

from cooling_tower_chem import CoolingTower, WaterSample


def test_streams_and_balance():
    tower = CoolingTower(circulation_rate=1000.0, delta_t_c=5.5, cycles=5.0, drift_fraction=0.0)
    # Evaporation from the energy balance.
    assert tower.evaporation == pytest.approx(1000.0 * 4.186 * 5.5 / 2450.0, rel=1e-9)
    assert tower.drift == 0.0
    # Blowdown = E / (cycles - 1); makeup = E + B + D.
    assert tower.blowdown == pytest.approx(tower.evaporation / 4.0)
    assert tower.makeup == pytest.approx(tower.evaporation + tower.blowdown)


def test_water_balance_dict_round_trips_cycles():
    tower = CoolingTower(circulation_rate=500.0, delta_t_c=6.0, cycles=4.0)
    wb = tower.water_balance()
    assert set(wb) >= {"evaporation", "drift", "blowdown", "makeup", "cycles"}
    # Recover cycles from the reported streams.
    recovered = wb["makeup"] / (wb["blowdown"] + wb["drift"])
    assert recovered == pytest.approx(4.0, rel=1e-3)


def test_blowdown_requires_cycles():
    tower = CoolingTower(circulation_rate=1000.0, delta_t_c=5.5)
    with pytest.raises(ValueError):
        _ = tower.blowdown
    # Balance without cycles still reports the flow-independent streams.
    wb = tower.water_balance()
    assert "blowdown" not in wb and "evaporation" in wb


def test_concentrated_projection_raises_lsi():
    makeup = WaterSample(
        ph=7.8, temperature_c=32.0, calcium_hardness=90.0,
        total_alkalinity=60.0, conductivity_us_cm=400.0,
        chloride=30.0, sulfate=25.0,
    )
    tower = CoolingTower(circulation_rate=1000.0, delta_t_c=6.0, cycles=5.0)
    basin = tower.concentrated(makeup)
    # Conservative species scale by cycles; pH/temperature are carried through.
    assert basin.calcium_hardness == pytest.approx(90.0 * 5)
    assert basin.total_alkalinity == pytest.approx(60.0 * 5)
    assert basin.conductivity_us_cm == pytest.approx(400.0 * 5)
    assert basin.ph == makeup.ph
    # Concentrating the water makes it far more scale-forming.
    assert basin.lsi() > makeup.lsi()
