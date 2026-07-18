"""Tests for the WaterSample convenience wrapper."""

import json

import pytest

from cooling_tower_chem import WaterSample, langelier_saturation_index


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
