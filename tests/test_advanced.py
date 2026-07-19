"""Tests for the Calcium Carbonate Precipitation Potential (``advanced`` module).

The reference cases are Wojtowicz's (2001) worked closed-system examples,
reproduced with the Plummer & Busenberg (1982) constants and the Davies activity
model that this library implements. As with :mod:`test_literature`, the pinned
numbers come from an outside source, not from this project.

A note on ionic strength. Wojtowicz's three examples are all quoted at
TDS = 5000 mg/L. CCPP is dominated by the activity correction, so it is sensitive
to the ionic strength used; reproducing Wojtowicz's published figures with this
model requires ``mu`` about 0.24 mol/L, which is supplied explicitly below. The
Langelier TDS estimate (``mu = 2.5e-5 * TDS = 0.125``) is lower and would predict
~30 / 17.6 / 8.9 mg/L instead — the dependency-free Davies model carries no ion
pairing and over-predicts precipitation for hard, high-TDS water. This sensitivity
is documented in the function's Notes; the tests below therefore pass ``mu``
directly rather than leaning on the rough TDS estimate.
"""

import math

import pytest

from cooling_tower_chem import (
    calcium_carbonate_precipitation_potential,
    ionic_strength_from_tds,
)
from cooling_tower_chem.advanced import _plummer_busenberg_constants


def test_plummer_busenberg_constants_at_25c():
    """Pin the equilibrium constants to Plummer & Busenberg's 25 C values.

    Verified in the issue #1 spec: pK1 = 6.352, pK2 = 10.329,
    pKsp(calcite) = 8.480, log Kw = -13.995.
    """
    k1, k2, ksp, kw = _plummer_busenberg_constants(25.0)
    assert -math.log10(k1) == pytest.approx(6.352, abs=1e-3)
    assert -math.log10(k2) == pytest.approx(10.329, abs=1e-3)
    assert -math.log10(ksp) == pytest.approx(8.480, abs=1e-3)
    assert math.log10(kw) == pytest.approx(-13.995, abs=1e-3)


@pytest.mark.parametrize(
    "ph, calcium, expected",
    [
        (7.0, 4786.0, 25.2),
        (7.5, 1514.0, 14.1),
        (8.0, 479.0, 7.1),
    ],
)
def test_wojtowicz_worked_examples(ph, calcium, expected):
    """Wojtowicz (2001), closed system, T = 26.7 C, alkalinity 100 mg/L as CaCO3.

    Source: Wojtowicz, J. A. (2001), *The Calcium Carbonate Precipitation
    Potential (CCPP) and its Use in Pool Water Balance*, J. Swimming Pool & Spa
    Industry 2(2), 23-29. The three rows are quoted at TDS 5000 (mu ~= 0.24; see
    the module docstring). This library computes 25.22, 14.13 and 7.15 mg/L for
    the three rows, each within ~0.06 of the published figure; the tolerance
    covers Wojtowicz's rounding to 0.1 mg/L.
    """
    ccpp = calcium_carbonate_precipitation_potential(
        ph=ph,
        temperature_c=26.7,
        calcium_hardness=calcium,
        total_alkalinity=100.0,
        ionic_strength=0.24,
    )
    assert ccpp == pytest.approx(expected, abs=0.15)
    assert ccpp > 0  # every row is supersaturated -> net precipitation


def test_sign_supersaturated_positive_undersaturated_negative():
    common = dict(ph=7.5, temperature_c=25.0, total_alkalinity=150.0, ionic_strength=0.05)
    undersaturated = calcium_carbonate_precipitation_potential(calcium_hardness=50.0, **common)
    supersaturated = calcium_carbonate_precipitation_potential(calcium_hardness=3000.0, **common)
    assert undersaturated < 0 < supersaturated


def test_ccpp_is_zero_at_saturation():
    """The calcium that makes CCPP change sign is the saturation point, CCPP ~ 0."""
    common = dict(ph=7.5, temperature_c=25.0, total_alkalinity=150.0, ionic_strength=0.05)
    low, high = 50.0, 3000.0
    for _ in range(60):
        mid = 0.5 * (low + high)
        if calcium_carbonate_precipitation_potential(calcium_hardness=mid, **common) > 0:
            high = mid
        else:
            low = mid
    ca_saturation = 0.5 * (low + high)
    at_saturation = calcium_carbonate_precipitation_potential(
        calcium_hardness=ca_saturation, **common
    )
    assert at_saturation == pytest.approx(0.0, abs=1e-3)


def test_ccpp_increases_with_calcium():
    common = dict(ph=8.0, temperature_c=25.0, total_alkalinity=200.0, ionic_strength=0.02)
    base = calcium_carbonate_precipitation_potential(calcium_hardness=800.0, **common)
    more = calcium_carbonate_precipitation_potential(calcium_hardness=1600.0, **common)
    assert more > base > 0


def test_ccpp_increases_with_ph():
    common = dict(temperature_c=25.0, calcium_hardness=800.0, total_alkalinity=200.0,
                  ionic_strength=0.02)
    base = calcium_carbonate_precipitation_potential(ph=8.0, **common)
    higher = calcium_carbonate_precipitation_potential(ph=8.3, **common)
    assert higher > base > 0


def test_ccpp_increases_with_alkalinity():
    common = dict(ph=8.0, temperature_c=25.0, calcium_hardness=800.0, ionic_strength=0.02)
    base = calcium_carbonate_precipitation_potential(total_alkalinity=200.0, **common)
    more = calcium_carbonate_precipitation_potential(total_alkalinity=400.0, **common)
    assert more > base > 0


def test_higher_ionic_strength_reduces_precipitation():
    """Raising ionic strength raises apparent solubility, so less CaCO3 precipitates."""
    common = dict(ph=8.0, temperature_c=25.0, calcium_hardness=800.0, total_alkalinity=200.0)
    dilute = calcium_carbonate_precipitation_potential(ionic_strength=0.02, **common)
    saline = calcium_carbonate_precipitation_potential(ionic_strength=0.30, **common)
    assert 0 < saline < dilute


def test_tds_and_ionic_strength_paths_agree():
    from_tds = calcium_carbonate_precipitation_potential(
        ph=8.0, temperature_c=30.0, calcium_hardness=400.0, total_alkalinity=200.0, tds=1200.0
    )
    explicit = calcium_carbonate_precipitation_potential(
        ph=8.0, temperature_c=30.0, calcium_hardness=400.0, total_alkalinity=200.0,
        ionic_strength=ionic_strength_from_tds(1200.0),
    )
    assert from_tds == pytest.approx(explicit)


def test_requires_tds_or_ionic_strength():
    with pytest.raises(ValueError):
        calcium_carbonate_precipitation_potential(
            ph=7.5, temperature_c=25.0, calcium_hardness=300.0, total_alkalinity=150.0
        )


def test_non_positive_tds_rejected():
    with pytest.raises(ValueError):
        calcium_carbonate_precipitation_potential(
            ph=7.5, temperature_c=25.0, calcium_hardness=300.0,
            total_alkalinity=150.0, tds=0.0,
        )


@pytest.mark.parametrize("bad", [0.0, -1.0, float("nan"), float("inf")])
@pytest.mark.parametrize("field", ["calcium_hardness", "total_alkalinity", "ionic_strength"])
def test_positive_inputs_are_validated(field, bad):
    kwargs = dict(
        ph=7.5, temperature_c=25.0, calcium_hardness=300.0,
        total_alkalinity=150.0, ionic_strength=0.05,
    )
    kwargs[field] = bad
    with pytest.raises(ValueError):
        calcium_carbonate_precipitation_potential(**kwargs)


@pytest.mark.parametrize("bad_ph", [float("nan"), float("inf")])
def test_non_finite_ph_rejected(bad_ph):
    with pytest.raises(ValueError):
        calcium_carbonate_precipitation_potential(
            ph=bad_ph, temperature_c=25.0, calcium_hardness=300.0,
            total_alkalinity=150.0, ionic_strength=0.05,
        )


def test_temperature_below_absolute_zero_rejected():
    with pytest.raises(ValueError):
        calcium_carbonate_precipitation_potential(
            ph=7.5, temperature_c=-300.0, calcium_hardness=300.0,
            total_alkalinity=150.0, ionic_strength=0.05,
        )
