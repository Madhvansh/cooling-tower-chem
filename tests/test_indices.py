"""Tests for the saturation / corrosion indices.

Reference case A (used throughout): pH 7.5, 25 C, TDS 400 mg/L,
calcium hardness 240 mg/L as CaCO3, total alkalinity 180 mg/L as CaCO3.
The pHs/LSI/RSI/PSI values below are computed from the standard Langelier
analytical formula and are stable to 4 decimals.
"""

import math

import pytest

from cooling_tower_chem import (
    aggressiveness_index,
    langelier_saturation_index,
    larson_skold_index,
    ph_of_saturation,
    puckorius_scaling_index,
    ryznar_stability_index,
)

# Reference case A inputs
A = dict(temperature_c=25.0, tds=400.0, calcium_hardness=240.0, total_alkalinity=180.0)


def test_ph_of_saturation_reference():
    assert ph_of_saturation(**A) == pytest.approx(7.31014, abs=1e-4)


def test_lsi_reference():
    assert langelier_saturation_index(ph=7.5, **A) == pytest.approx(0.18986, abs=1e-4)


def test_rsi_reference():
    assert ryznar_stability_index(ph=7.5, **A) == pytest.approx(7.12027, abs=1e-4)


def test_psi_reference():
    # PSI does not take a measured pH.
    assert puckorius_scaling_index(**A) == pytest.approx(6.77630, abs=1e-4)


def test_lsi_and_rsi_share_phs():
    phs = ph_of_saturation(**A)
    ph = 7.5
    assert langelier_saturation_index(ph=ph, **A) == pytest.approx(ph - phs)
    assert ryznar_stability_index(ph=ph, **A) == pytest.approx(2 * phs - ph)


def test_lsi_sign_tracks_ph():
    # Raising pH above saturation makes water scale-forming (LSI > 0);
    # lowering it makes water corrosive (LSI < 0).
    phs = ph_of_saturation(**A)
    assert langelier_saturation_index(ph=phs + 1.0, **A) == pytest.approx(1.0, abs=1e-9)
    assert langelier_saturation_index(ph=phs - 1.0, **A) < 0


def test_lsi_increases_with_hardness_and_alkalinity():
    base = langelier_saturation_index(ph=7.5, **A)
    more_ca = langelier_saturation_index(
        ph=7.5, temperature_c=25.0, tds=400.0, calcium_hardness=480.0, total_alkalinity=180.0
    )
    more_alk = langelier_saturation_index(
        ph=7.5, temperature_c=25.0, tds=400.0, calcium_hardness=240.0, total_alkalinity=360.0
    )
    assert more_ca > base
    assert more_alk > base


def test_lsi_increases_with_temperature():
    cold = langelier_saturation_index(ph=7.5, temperature_c=10.0, tds=400.0,
                                      calcium_hardness=240.0, total_alkalinity=180.0)
    hot = langelier_saturation_index(ph=7.5, temperature_c=45.0, tds=400.0,
                                     calcium_hardness=240.0, total_alkalinity=180.0)
    assert hot > cold


def test_aggressiveness_index_reference():
    # AI = pH + log10(Ca * alkalinity)
    assert aggressiveness_index(ph=7.5, calcium_hardness=240.0, total_alkalinity=180.0) == (
        pytest.approx(7.5 + math.log10(240.0 * 180.0), abs=1e-9)
    )


def test_larson_skold_unit_case():
    # Chosen so every term is one equivalent: ratio == 1.0.
    ls = larson_skold_index(chloride=35.45, sulfate=48.03, total_alkalinity=100.08)
    assert ls == pytest.approx(1.0, abs=1e-3)


def test_larson_skold_scales_with_chloride():
    low = larson_skold_index(chloride=35.0, sulfate=50.0, total_alkalinity=150.0)
    high = larson_skold_index(chloride=140.0, sulfate=50.0, total_alkalinity=150.0)
    assert high > low


@pytest.mark.parametrize("bad", [0.0, -1.0, float("nan"), float("inf")])
@pytest.mark.parametrize("field", ["tds", "calcium_hardness", "total_alkalinity"])
def test_positive_inputs_are_validated(field, bad):
    kwargs = dict(temperature_c=25.0, tds=400.0, calcium_hardness=240.0, total_alkalinity=180.0)
    kwargs[field] = bad
    with pytest.raises(ValueError):
        ph_of_saturation(**kwargs)


def test_temperature_below_absolute_zero_rejected():
    with pytest.raises(ValueError):
        ph_of_saturation(
            temperature_c=-300.0, tds=400.0, calcium_hardness=240.0, total_alkalinity=180.0
        )


def test_larson_skold_rejects_negative_and_zero_alkalinity():
    with pytest.raises(ValueError):
        larson_skold_index(chloride=-1.0, sulfate=50.0, total_alkalinity=150.0)
    with pytest.raises(ValueError):
        larson_skold_index(chloride=35.0, sulfate=50.0, total_alkalinity=0.0)
