"""Tests for the unit-conversion helpers (all conversions are exact)."""

import pytest

from cooling_tower_chem.convert import (
    EQUIVALENT_WEIGHTS,
    as_caco3,
    bicarbonate_as_caco3,
    caco3_to_ion,
    calcium_as_caco3,
    celsius_to_fahrenheit,
    fahrenheit_to_celsius,
    grains_per_gallon_to_mg_l,
    magnesium_as_caco3,
    mg_l_to_grains_per_gallon,
)


def test_calcium_as_caco3_standard_factor():
    # The textbook factor for Ca(2+) -> CaCO3 is ~2.5.
    assert calcium_as_caco3(100.0) == pytest.approx(249.7, abs=0.1)


def test_magnesium_as_caco3_standard_factor():
    assert magnesium_as_caco3(100.0) == pytest.approx(411.8, abs=0.2)


def test_bicarbonate_as_caco3_standard_factor():
    assert bicarbonate_as_caco3(100.0) == pytest.approx(82.0, abs=0.2)


def test_as_caco3_round_trips():
    for ion in ("Ca", "Mg", "HCO3", "Cl", "SO4"):
        eq = EQUIVALENT_WEIGHTS[ion]
        assert caco3_to_ion(as_caco3(50.0, eq), eq) == pytest.approx(50.0)


def test_grains_round_trip():
    assert grains_per_gallon_to_mg_l(1.0) == pytest.approx(17.118)
    assert mg_l_to_grains_per_gallon(171.18) == pytest.approx(10.0)


def test_temperature_conversions():
    assert celsius_to_fahrenheit(25.0) == pytest.approx(77.0)
    assert fahrenheit_to_celsius(77.0) == pytest.approx(25.0)
    assert celsius_to_fahrenheit(0.0) == 32.0
    assert fahrenheit_to_celsius(fahrenheit_to_celsius(212.0) * 9 / 5 + 32) == pytest.approx(100.0)


def test_invalid_inputs_raise():
    with pytest.raises(ValueError):
        as_caco3(-1.0, EQUIVALENT_WEIGHTS["Ca"])
    with pytest.raises(ValueError):
        as_caco3(10.0, 0.0)
    with pytest.raises(ValueError):
        celsius_to_fahrenheit(float("nan"))
