"""Unit conversions for water-chemistry work.

Water-treatment data arrives in inconsistent units: an ion may be reported as
mg/L of the ion itself or "as CaCO3", hardness may be in grains per gallon, and
US sources use Fahrenheit. These helpers convert between the conventions the
indices in :mod:`cooling_tower_chem.indices` expect (mg/L as CaCO3, degrees C).

"As CaCO3" expresses a concentration in terms of an equivalent amount of calcium
carbonate: ``mg/L as CaCO3 = mg/L of ion x (50.04 / equivalent_weight_of_ion)``,
where 50.04 mg/meq is the equivalent weight of CaCO3.
"""

from __future__ import annotations

import math

__all__ = [
    "EQUIVALENT_WEIGHTS",
    "GRAINS_PER_GALLON_TO_MG_L",
    "as_caco3",
    "caco3_to_ion",
    "calcium_as_caco3",
    "magnesium_as_caco3",
    "bicarbonate_as_caco3",
    "mg_l_to_grains_per_gallon",
    "grains_per_gallon_to_mg_l",
    "celsius_to_fahrenheit",
    "fahrenheit_to_celsius",
]

#: Equivalent weight (mg per milliequivalent) of common water-chemistry species.
EQUIVALENT_WEIGHTS = {
    "CaCO3": 50.04,
    "Ca": 20.04,     # Ca(2+), 40.078 / 2
    "Mg": 12.15,     # Mg(2+), 24.305 / 2
    "Na": 22.99,     # Na(+)
    "HCO3": 61.02,   # bicarbonate
    "CO3": 30.00,    # carbonate, 60.01 / 2
    "Cl": 35.45,     # chloride
    "SO4": 48.03,    # sulfate, 96.06 / 2
}

#: One grain per US gallon equals 17.118 mg/L (as CaCO3, the usual hardness unit).
GRAINS_PER_GALLON_TO_MG_L = 17.118

_CACO3_EQ = EQUIVALENT_WEIGHTS["CaCO3"]


def _check(name: str, value: float) -> float:
    if value is None or not math.isfinite(value) or value < 0:
        raise ValueError(f"{name} must be a non-negative finite number, got {value!r}")
    return float(value)


def as_caco3(concentration_mg_l: float, equivalent_weight: float) -> float:
    """Convert a concentration in mg/L of an ion to mg/L as CaCO3.

    Pass the ion's equivalent weight (mg/meq); several are in
    :data:`EQUIVALENT_WEIGHTS`.
    """
    concentration_mg_l = _check("concentration_mg_l", concentration_mg_l)
    if equivalent_weight <= 0 or not math.isfinite(equivalent_weight):
        raise ValueError(f"equivalent_weight must be > 0, got {equivalent_weight!r}")
    return concentration_mg_l * (_CACO3_EQ / equivalent_weight)


def caco3_to_ion(caco3_mg_l: float, equivalent_weight: float) -> float:
    """Inverse of :func:`as_caco3`: mg/L as CaCO3 back to mg/L of the ion."""
    caco3_mg_l = _check("caco3_mg_l", caco3_mg_l)
    if equivalent_weight <= 0 or not math.isfinite(equivalent_weight):
        raise ValueError(f"equivalent_weight must be > 0, got {equivalent_weight!r}")
    return caco3_mg_l * (equivalent_weight / _CACO3_EQ)


def calcium_as_caco3(calcium_mg_l: float) -> float:
    """Convert mg/L of Ca(2+) to mg/L as CaCO3 (x ~2.497)."""
    return as_caco3(calcium_mg_l, EQUIVALENT_WEIGHTS["Ca"])


def magnesium_as_caco3(magnesium_mg_l: float) -> float:
    """Convert mg/L of Mg(2+) to mg/L as CaCO3 (x ~4.118)."""
    return as_caco3(magnesium_mg_l, EQUIVALENT_WEIGHTS["Mg"])


def bicarbonate_as_caco3(bicarbonate_mg_l: float) -> float:
    """Convert mg/L of HCO3(-) alkalinity to mg/L as CaCO3 (x ~0.820)."""
    return as_caco3(bicarbonate_mg_l, EQUIVALENT_WEIGHTS["HCO3"])


def mg_l_to_grains_per_gallon(mg_l: float) -> float:
    """Convert mg/L (as CaCO3) to grains per US gallon."""
    return _check("mg_l", mg_l) / GRAINS_PER_GALLON_TO_MG_L


def grains_per_gallon_to_mg_l(grains_per_gallon: float) -> float:
    """Convert grains per US gallon to mg/L (as CaCO3)."""
    return _check("grains_per_gallon", grains_per_gallon) * GRAINS_PER_GALLON_TO_MG_L


def celsius_to_fahrenheit(celsius: float) -> float:
    """Convert degrees Celsius to Fahrenheit."""
    if celsius is None or not math.isfinite(celsius):
        raise ValueError(f"celsius must be finite, got {celsius!r}")
    return celsius * 9.0 / 5.0 + 32.0


def fahrenheit_to_celsius(fahrenheit: float) -> float:
    """Convert degrees Fahrenheit to Celsius."""
    if fahrenheit is None or not math.isfinite(fahrenheit):
        raise ValueError(f"fahrenheit must be finite, got {fahrenheit!r}")
    return (fahrenheit - 32.0) * 5.0 / 9.0
