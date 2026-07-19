"""Pin index values to published, worked examples from the literature.

The other test modules validate the LSI/RSI/PSI *formulas* against the standard
Langelier analytical method plus monotonicity and validation properties. This
module is complementary: each test reproduces a fully worked example published
by an outside source, so a regression in the constants would be caught against a
number nobody in this project chose.

Every example below uses the same analytical saturation-pH formula this library
implements (``indices.ph_of_saturation``):

    pHs = (9.3 + A + B) - (C + D)
    A = (log10(TDS) - 1) / 10                 # ionic-strength / TDS term
    B = 34.55 - 13.12 * log10(T_kelvin)       # temperature term
    C = log10(calcium_hardness_as_CaCO3) - 0.4
    D = log10(total_alkalinity_as_CaCO3)

Tolerances are set to cover the rounding each source applied to its own
intermediate constants and final result (noted per case); they are not tuned to
make the library "pass".
"""

import pytest

from cooling_tower_chem import (
    langelier_saturation_index,
    ph_of_saturation,
    ryznar_stability_index,
)


def test_langelier_worked_example_corrosion_doctors():
    """LSI worked example, Carbotecnia reproducing the Corrosion Doctors correlation.

    Source (fetched 2026-07-19):
      https://www.carbotecnia.info/en/learning-center/water-chemistry/langelier-saturation-index/
      "Corrosion Doctors publishes the following correlation:
       pHs = 9.3 + A + B - C - D"  -- i.e. the exact formula used here.

    Worked example, verbatim from the page:
      pH = 8.8, TDS (SDT) = 320 mg/L, calcium hardness (DC) = 150 mg/L as CaCO3,
      total alkalinity (AT) = 34 mg/L as CaCO3, T = 25 C (298 K).
      A = (log 320 - 1)/10 = 0.15
      B = 34.55 - 13.12 * log 298 = 2.09
      C = log 150 - 0.4 = 1.78
      D = log 34 = 1.53
      pHs = 9.3 + 0.15 + 2.09 - 1.78 - 1.53 = 8.2
      LSI = 8.8 - 8.2 = 0.6   ("very encrusting" / scale-forming)

    Tolerance: the source rounds pHs and LSI to one decimal place, so +/-0.05.
    (This library reports pHs 8.228 and LSI 0.572; both round to the published
    8.2 and 0.6.)
    """
    phs = ph_of_saturation(
        temperature_c=25.0, tds=320.0, calcium_hardness=150.0, total_alkalinity=34.0
    )
    lsi = langelier_saturation_index(
        ph=8.8, temperature_c=25.0, tds=320.0,
        calcium_hardness=150.0, total_alkalinity=34.0,
    )
    assert phs == pytest.approx(8.2, abs=0.05)
    assert lsi == pytest.approx(0.6, abs=0.05)
    assert lsi > 0  # published verdict: scale-forming


def test_ryznar_worked_example_water_treatment_basics():
    """RSI worked example, Water Treatment Basics.

    Source (fetched 2026-07-19):
      https://watertreatmentbasics.com/ryznar-stability-index-calculation/
      Uses the same saturation-pH formula, pHs = (9.3 + A + B) - (C + D), then
      RSI = 2*pHs - pH.

    Worked example, verbatim from the page ("Ryznar Index Calculation Example"):
      pH = 8.0, TDS = 500 mg/L, T = 30 C, calcium hardness = 250 ppm as CaCO3,
      M-alkalinity = 100 ppm as CaCO3.
      A = 0.17, B = 2.02, C = 2.0, D = 2.0
      pHs = 7.49
      RSI = 2 * 7.49 - 8.0 = 6.98   ("slightly scale forming")

    Tolerance: the source rounds each constant to two decimals; its B = 2.02 is
    ~0.03 above the exact value (this library gets 1.99), which propagates and
    doubles through RSI = 2*pHs. +/-0.05 on pHs and +/-0.1 on RSI cover it.
    (This library reports pHs 7.463 and RSI 6.925.)
    """
    phs = ph_of_saturation(
        temperature_c=30.0, tds=500.0, calcium_hardness=250.0, total_alkalinity=100.0
    )
    rsi = ryznar_stability_index(
        ph=8.0, temperature_c=30.0, tds=500.0,
        calcium_hardness=250.0, total_alkalinity=100.0,
    )
    assert phs == pytest.approx(7.49, abs=0.05)
    assert rsi == pytest.approx(6.98, abs=0.1)
    assert rsi > 6.0  # published verdict: (slightly) scale-forming
