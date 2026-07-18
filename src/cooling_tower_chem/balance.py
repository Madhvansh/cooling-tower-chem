"""Cooling-tower water balance: cycles of concentration and evaporation/blowdown.

These helpers relate the four water streams of an evaporative cooling tower:

* **Evaporation (E)** — pure water lost to the air; it concentrates dissolved
  solids in the remaining water.
* **Drift / windage (D)** — liquid droplets carried out in the air stream.
* **Blowdown / bleed (B)** — water deliberately discharged to cap the dissolved
  solids concentration.
* **Makeup (M)** — fresh water added to replace all losses: ``M = E + B + D``.

Cycles of concentration (CoC) is the ratio of a conservative species'
concentration in the recirculating water to its concentration in the makeup
water, and equals ``M / (B + D)``.

All flow rates share whatever volumetric unit you pass in (e.g. m3/h or gpm);
the functions only take ratios and sums, so the result carries the same unit.
"""

from __future__ import annotations

import math

__all__ = [
    "tds_from_conductivity",
    "conductivity_from_tds",
    "cycles_of_concentration",
    "evaporation_loss",
    "drift_loss",
    "blowdown_loss",
    "makeup_water",
    "cycles_from_flows",
    "water_saved_by_increasing_cycles",
]

# Cooling-tower recirculating water is typically ~0.55-0.70 mg/L per uS/cm.
DEFAULT_TDS_FACTOR = 0.65


def _require_positive(name: str, value: float) -> float:
    if value is None or not math.isfinite(value):
        raise ValueError(f"{name} must be a finite number, got {value!r}")
    if value <= 0:
        raise ValueError(f"{name} must be > 0, got {value!r}")
    return float(value)


def tds_from_conductivity(
    conductivity_us_cm: float, factor: float = DEFAULT_TDS_FACTOR
) -> float:
    """Estimate TDS (mg/L) from electrical conductivity (uS/cm).

    ``TDS ~= factor * conductivity``. The factor depends on the ionic makeup of
    the water and typically ranges 0.55-0.70 for cooling-tower water; 0.65 is a
    common default. Calibrate against a lab TDS when accuracy matters.
    """
    conductivity_us_cm = _require_positive("conductivity_us_cm", conductivity_us_cm)
    factor = _require_positive("factor", factor)
    return conductivity_us_cm * factor


def conductivity_from_tds(
    tds: float, factor: float = DEFAULT_TDS_FACTOR
) -> float:
    """Inverse of :func:`tds_from_conductivity`: estimate uS/cm from mg/L TDS."""
    tds = _require_positive("tds", tds)
    factor = _require_positive("factor", factor)
    return tds / factor


def cycles_of_concentration(circulating: float, makeup: float) -> float:
    """Cycles of concentration from a conservative-species ratio.

    Pass the concentration of a species that leaves only via blowdown/drift
    (conductivity, chloride, or silica are common choices) in the recirculating
    water and in the makeup water. ``CoC = circulating / makeup``.
    """
    circulating = _require_positive("circulating", circulating)
    makeup = _require_positive("makeup", makeup)
    return circulating / makeup


def evaporation_loss(
    circulation_rate: float,
    delta_t_c: float,
    latent_heat_kj_per_kg: float | None = None,
    specific_heat_kj_per_kg_c: float = 4.186,
) -> float:
    """Evaporation rate from a first-principles energy balance.

    ``E = circulation_rate * cp * delta_t / latent_heat``. Roughly 1% of the
    circulating flow evaporates per ~5.5 C (10 F) of cooling range, which this
    energy balance reproduces.

    Note this assumes **all** rejected heat leaves as latent heat of
    vaporization, so it returns the theoretical *maximum* evaporation. Real
    towers also reject some sensible/convective heat, so field evaporation is
    typically ~75-90% of this value; apply a heat-rejection factor if you need
    the practical estimate, or pass a temperature-appropriate ``latent_heat``.

    Parameters
    ----------
    circulation_rate:
        Recirculating water flow (any volumetric unit; the result is returned in
        the same unit).
    delta_t_c:
        Cooling range: the temperature drop across the tower, in C.
    latent_heat_kj_per_kg:
        Latent heat of vaporization. If omitted, a temperature-independent
        2450 kJ/kg (typical near 30-35 C) is used.
    specific_heat_kj_per_kg_c:
        Specific heat of water, default 4.186 kJ/(kg.C).
    """
    circulation_rate = _require_positive("circulation_rate", circulation_rate)
    if delta_t_c is None or not math.isfinite(delta_t_c) or delta_t_c < 0:
        raise ValueError(f"delta_t_c must be >= 0, got {delta_t_c!r}")
    latent = 2450.0 if latent_heat_kj_per_kg is None else latent_heat_kj_per_kg
    latent = _require_positive("latent_heat_kj_per_kg", latent)
    return circulation_rate * specific_heat_kj_per_kg_c * delta_t_c / latent


def drift_loss(circulation_rate: float, drift_fraction: float = 0.0002) -> float:
    """Drift (windage) loss as a fraction of circulation.

    Modern drift eliminators achieve 0.001%-0.02% of circulating flow; the
    default 0.0002 (0.02%) is a conservative upper estimate for a tower with
    good eliminators.
    """
    circulation_rate = _require_positive("circulation_rate", circulation_rate)
    if drift_fraction < 0 or not math.isfinite(drift_fraction):
        raise ValueError(f"drift_fraction must be >= 0, got {drift_fraction!r}")
    return circulation_rate * drift_fraction


def blowdown_loss(
    evaporation: float, cycles: float, drift: float = 0.0
) -> float:
    """Required blowdown to hold a target cycles of concentration.

    From the dissolved-solids mass balance, ``B = E / (CoC - 1) - D``. The
    result is clamped at zero (if drift alone already exceeds the solids budget,
    no blowdown is needed).
    """
    evaporation = _require_positive("evaporation", evaporation)
    if cycles <= 1:
        raise ValueError(f"cycles must be > 1, got {cycles!r}")
    if drift < 0 or not math.isfinite(drift):
        raise ValueError(f"drift must be >= 0, got {drift!r}")
    return max(0.0, evaporation / (cycles - 1.0) - drift)


def makeup_water(evaporation: float, blowdown: float, drift: float = 0.0) -> float:
    """Makeup water required: ``M = E + B + D``."""
    evaporation = _require_positive("evaporation", evaporation)
    if blowdown < 0 or not math.isfinite(blowdown):
        raise ValueError(f"blowdown must be >= 0, got {blowdown!r}")
    if drift < 0 or not math.isfinite(drift):
        raise ValueError(f"drift must be >= 0, got {drift!r}")
    return evaporation + blowdown + drift


def cycles_from_flows(makeup: float, blowdown: float, drift: float = 0.0) -> float:
    """Cycles of concentration from the water streams: ``CoC = M / (B + D)``."""
    makeup = _require_positive("makeup", makeup)
    denominator = blowdown + drift
    if denominator <= 0:
        raise ValueError("blowdown + drift must be > 0 to define cycles")
    return makeup / denominator


def water_saved_by_increasing_cycles(
    evaporation: float, cycles_low: float, cycles_high: float, drift: float = 0.0
) -> float:
    """Makeup water saved per unit time by raising cycles of concentration.

    Increasing CoC reduces blowdown (and therefore makeup) for the same
    evaporative duty. Returns ``makeup(cycles_low) - makeup(cycles_high)`` in the
    same flow unit as *evaporation*. A positive result is water saved; raising
    cycles from, say, 3 to 6 typically cuts makeup noticeably.
    """
    if cycles_high <= cycles_low:
        raise ValueError("cycles_high must be greater than cycles_low")
    b_low = blowdown_loss(evaporation, cycles_low, drift)
    b_high = blowdown_loss(evaporation, cycles_high, drift)
    return makeup_water(evaporation, b_low, drift) - makeup_water(
        evaporation, b_high, drift
    )
