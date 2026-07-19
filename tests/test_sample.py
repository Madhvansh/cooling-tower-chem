"""Tests for the WaterSample convenience wrapper."""

import json

import pytest

from cooling_tower_chem import WaterSample, langelier_saturation_index
from cooling_tower_chem.convert import (
    fahrenheit_to_celsius,
    grains_per_gallon_to_mg_l,
)


def make_sample(**overrides):
    base = dict(
        ph=8.2,
        temperature_c=32.0,
        calcium_hardness=450.0,
        total_alkalinity=250.0,
        conductivity_us_cm=2400.0,
        chloride=180.0,
        sulfate=120.0,
    )
    base.update(overrides)
    return WaterSample(**base)


def test_effective_tds_from_conductivity():
    s = make_sample()
    assert s.effective_tds() == pytest.approx(2400.0 * 0.65)


def test_explicit_tds_takes_precedence():
    s = make_sample(tds=1500.0)
    assert s.effective_tds() == 1500.0


def test_missing_tds_and_conductivity_raises():
    s = WaterSample(ph=8.0, temperature_c=30.0, calcium_hardness=400.0, total_alkalinity=200.0)
    with pytest.raises(ValueError):
        s.effective_tds()
    with pytest.raises(ValueError):
        s.lsi()


def test_sample_matches_functional_api():
    s = make_sample()
    expected = langelier_saturation_index(
        ph=8.2, temperature_c=32.0, tds=2400.0 * 0.65,
        calcium_hardness=450.0, total_alkalinity=250.0,
    )
    assert s.lsi() == pytest.approx(expected)


def test_report_is_json_serializable_and_complete():
    s = make_sample()
    report = s.report()
    # Round-trips through JSON.
    assert json.loads(json.dumps(report)) == report
    for key in ("lsi", "rsi", "psi", "aggressiveness_index", "larson_skold_index"):
        assert key in report
        assert set(report[key]) == {"value", "tendency", "description"}


def test_report_omits_larson_skold_without_ions():
    s = make_sample(chloride=None, sulfate=None)
    assert s.larson_skold_index() is None
    assert "larson_skold_index" not in s.report()


def test_report_values_are_reasonable():
    s = make_sample()
    report = s.report()
    # Concentrated, alkaline cooling water -> LSI positive (scale-forming).
    assert report["lsi"]["value"] > 0
    assert report["lsi"]["tendency"] == "scale_forming"


# --- WaterSample.from_us_units (Fahrenheit + grains/gallon) --------------------

# Each case: (ph, temperature_f, calcium_hardness_gpg, total_alkalinity_gpg,
#             extra kwargs passed through unchanged).
US_UNIT_CASES = [
    (8.2, 90.0, 26.3, 14.6, dict(conductivity_us_cm=2400.0)),
    (7.5, 77.0, 14.0, 10.5, dict(tds=400.0)),
    (7.0, 60.0, 5.0, 3.0, dict(tds=250.0)),
    (8.8, 104.0, 30.0, 12.0, dict(conductivity_us_cm=3000.0)),
    (6.9, 50.0, 8.5, 6.0, dict(tds=800.0, chloride=180.0, sulfate=120.0)),
]


@pytest.mark.parametrize("ph,temp_f,ca_gpg,alk_gpg,extra", US_UNIT_CASES)
def test_from_us_units_round_trips_against_si_constructor(ph, temp_f, ca_gpg, alk_gpg, extra):
    us = WaterSample.from_us_units(
        ph=ph,
        temperature_f=temp_f,
        calcium_hardness_gpg=ca_gpg,
        total_alkalinity_gpg=alk_gpg,
        **extra,
    )
    # The SI constructor fed the same inputs after an explicit conversion.
    si = WaterSample(
        ph=ph,
        temperature_c=fahrenheit_to_celsius(temp_f),
        calcium_hardness=grains_per_gallon_to_mg_l(ca_gpg),
        total_alkalinity=grains_per_gallon_to_mg_l(alk_gpg),
        **extra,
    )

    # Every stored field matches the explicitly-converted SI sample.
    assert us.ph == si.ph
    assert us.temperature_c == pytest.approx(si.temperature_c)
    assert us.calcium_hardness == pytest.approx(si.calcium_hardness)
    assert us.total_alkalinity == pytest.approx(si.total_alkalinity)
    assert us.tds == si.tds
    assert us.conductivity_us_cm == si.conductivity_us_cm
    assert us.chloride == si.chloride
    assert us.sulfate == si.sulfate

    # ...so every index comes out identical.
    assert us.lsi() == pytest.approx(si.lsi())
    assert us.rsi() == pytest.approx(si.rsi())
    assert us.psi() == pytest.approx(si.psi())
    assert us.report() == si.report()


def test_from_us_units_applies_the_expected_conversions():
    us = WaterSample.from_us_units(
        ph=7.8, temperature_f=77.0,
        calcium_hardness_gpg=10.0, total_alkalinity_gpg=5.0,
        tds=500.0,
    )
    assert us.temperature_c == pytest.approx(25.0)          # 77 F -> 25 C
    assert us.calcium_hardness == pytest.approx(171.18)     # 10 gpg -> 171.18 mg/L
    assert us.total_alkalinity == pytest.approx(85.59)      # 5 gpg -> 85.59 mg/L
    # tds and ph pass through unchanged.
    assert us.tds == 500.0
    assert us.ph == 7.8


def test_from_us_units_matches_manual_functional_call():
    us = WaterSample.from_us_units(
        ph=8.0, temperature_f=86.0,
        calcium_hardness_gpg=20.0, total_alkalinity_gpg=8.0,
        conductivity_us_cm=1800.0,
    )
    expected = langelier_saturation_index(
        ph=8.0,
        temperature_c=30.0,                       # 86 F
        tds=1800.0 * 0.65,                        # default TDS factor
        calcium_hardness=20.0 * 17.118,           # 20 gpg
        total_alkalinity=8.0 * 17.118,            # 8 gpg
    )
    assert us.lsi() == pytest.approx(expected)
