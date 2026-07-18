"""Tests for the water-balance helpers and their mass-balance identities."""

import pytest

from cooling_tower_chem import (
    blowdown_loss,
    conductivity_from_tds,
    cycles_from_flows,
    cycles_of_concentration,
    drift_loss,
    evaporation_loss,
    makeup_water,
    tds_from_conductivity,
    water_saved_by_increasing_cycles,
)


def test_tds_conductivity_round_trip():
    assert tds_from_conductivity(2000.0, factor=0.65) == pytest.approx(1300.0)
    assert conductivity_from_tds(1300.0, factor=0.65) == pytest.approx(2000.0)
    # Round-trips exactly for any positive factor.
    assert conductivity_from_tds(tds_from_conductivity(1234.0)) == pytest.approx(1234.0)


def test_cycles_of_concentration_ratio():
    assert cycles_of_concentration(circulating=2400.0, makeup=400.0) == pytest.approx(6.0)


def test_evaporation_energy_balance():
    # ~1% of circulation evaporates per 5.5 C of range.
    e = evaporation_loss(circulation_rate=1000.0, delta_t_c=5.5)
    assert e == pytest.approx(1000.0 * 4.186 * 5.5 / 2450.0, rel=1e-9)
    assert 8.0 < e < 11.0  # ~0.8-1.1% of circulation


def test_evaporation_zero_range_is_zero():
    assert evaporation_loss(circulation_rate=1000.0, delta_t_c=0.0) == 0.0


def test_mass_balance_is_consistent():
    # Pick evaporation and target cycles, derive blowdown and makeup, then
    # recover the same cycles from the flows: CoC = M / (B + D).
    evap = 10.0
    cycles = 5.0
    drift = 0.0
    b = blowdown_loss(evap, cycles, drift)
    assert b == pytest.approx(2.5)
    m = makeup_water(evap, b, drift)
    assert m == pytest.approx(12.5)
    assert cycles_from_flows(m, b, drift) == pytest.approx(cycles)


def test_mass_balance_with_drift():
    evap = 20.0
    cycles = 6.0
    drift = 0.5
    b = blowdown_loss(evap, cycles, drift)
    m = makeup_water(evap, b, drift)
    assert cycles_from_flows(m, b, drift) == pytest.approx(cycles)


def test_blowdown_clamped_to_zero_when_drift_covers_solids():
    # Very high cycles and non-trivial drift can drive computed blowdown to 0.
    assert blowdown_loss(evaporation=1.0, cycles=100.0, drift=1.0) == 0.0


def test_higher_cycles_reduce_blowdown():
    assert blowdown_loss(10.0, cycles=3.0) > blowdown_loss(10.0, cycles=6.0)


def test_water_saved_by_increasing_cycles():
    # E=10: makeup at 3 cycles = 15, at 6 cycles = 12 -> 3 saved.
    saved = water_saved_by_increasing_cycles(evaporation=10.0, cycles_low=3.0, cycles_high=6.0)
    assert saved == pytest.approx(3.0)
    assert saved > 0


def test_drift_loss_fraction():
    assert drift_loss(10000.0, drift_fraction=0.0002) == pytest.approx(2.0)


def test_invalid_inputs_raise():
    with pytest.raises(ValueError):
        cycles_of_concentration(circulating=0.0, makeup=400.0)
    with pytest.raises(ValueError):
        blowdown_loss(evaporation=10.0, cycles=1.0)  # cycles must be > 1
    with pytest.raises(ValueError):
        cycles_from_flows(makeup=10.0, blowdown=0.0, drift=0.0)
    with pytest.raises(ValueError):
        water_saved_by_increasing_cycles(evaporation=10.0, cycles_low=6.0, cycles_high=3.0)
