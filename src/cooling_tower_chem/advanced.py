"""Quantitative closed-system carbonate chemistry: the CaCO3 precipitation potential.

The saturation indices in :mod:`cooling_tower_chem.indices` (LSI, RSI, S&DSI, ...)
report a *direction* — whether water tends to scale or corrode — but not *how
much* calcium carbonate is involved. The **Calcium Carbonate Precipitation
Potential (CCPP)** closes that gap: it is the mass of CaCO3, in mg/L as CaCO3,
that must precipitate (positive) or dissolve (negative) to bring the water to
exact calcite saturation (saturation index ``SI = 0``).

Method
------
There is no closed form in the general case, so the equilibrium is solved
iteratively. The water is treated as a **closed system**: as CaCO3 is deposited
or dissolved the total (carbonate) alkalinity and the CO2-acidity are held
conservative. Removing one mole of CaCO3 removes one mole of calcium, one mole
of total carbonate, and **two equivalents of alkalinity**; the CO2-acidity
``2*CT - Alk`` is therefore unchanged. The equilibrium calcium, carbonate and
pH that satisfy ``[Ca][CO3] = Ksp`` are found by a bracketed root search, and

    CCPP (mg/L as CaCO3) = x * 100086.9      (x = mol/L of CaCO3 exchanged)

Thermodynamic equilibrium constants are the Plummer & Busenberg (1982) fits
(``T`` in kelvin); at 25 C they give ``pK1 = 6.352``, ``pK2 = 10.329``,
``pK_sp(calcite) = 8.480`` and ``log Kw = -13.995``. They are converted to
conditional (concentration) constants with single-ion activity coefficients from
the Davies equation, ``log gamma = -A z^2 (sqrt(I)/(1 + sqrt(I)) - 0.3 I)`` with
``A = 0.509`` (its 25 C value), valid to an ionic strength of about 0.5 mol/L.

References
----------
* Plummer, L. N. & Busenberg, E. (1982). "The solubilities of calcite, aragonite
  and vaterite in CO2-H2O solutions between 0 and 90 C." *Geochim. Cosmochim.
  Acta* 46(6), 1011-1040.
* Wojtowicz, J. A. (2001). "The Calcium Carbonate Precipitation Potential (CCPP)
  and its Use in Pool Water Balance." *J. Swimming Pool & Spa Industry* 2(2),
  23-29.
* Rossum, J. R. & Merrill, D. T. (1983). "An Evaluation of the Calcium Carbonate
  Saturation Indexes." *J. AWWA* 75(1), 95-100.
* Standard Methods for the Examination of Water and Wastewater, Method 2330
  (Calcium Carbonate Saturation).
* Tang, C. et al. (2021). "Prediction of Calcium Carbonate Precipitation
  Potential." *Water* 13(1), 42.
"""

from __future__ import annotations

import math

from .balance import ionic_strength_from_tds

__all__ = ["calcium_carbonate_precipitation_potential"]

# Debye-Huckel / Davies "A" constant at 25 C (per the reference above).
_A_DAVIES_25C = 0.509

# Molar mass / equivalent weight of CaCO3, matching cooling_tower_chem.indices.
_CACO3_MOLAR_MASS_MG = 100086.9  # mg per mol
_CACO3_EQUIV_MG = 50043.45       # mg per equivalent


def _require_finite(name: str, value: float) -> float:
    if value is None or not math.isfinite(value):
        raise ValueError(f"{name} must be a finite number, got {value!r}")
    return float(value)


def _require_positive(name: str, value: float) -> float:
    value = _require_finite(name, value)
    if value <= 0:
        raise ValueError(f"{name} must be > 0, got {value!r}")
    return value


def _require_temperature(temperature_c: float) -> float:
    temperature_c = _require_finite("temperature_c", temperature_c)
    if temperature_c <= -273.15:
        raise ValueError(
            f"temperature_c must be above absolute zero (-273.15 C), got {temperature_c!r}"
        )
    return temperature_c


def _plummer_busenberg_constants(temperature_c: float) -> tuple[float, float, float, float]:
    """Thermodynamic ``(K1, K2, Ksp_calcite, Kw)`` from Plummer & Busenberg (1982).

    ``temperature_c`` is degrees Celsius; the fits themselves take ``T`` in kelvin.
    The returned values are activity-based (thermodynamic) constants.
    """
    t = temperature_c + 273.15
    t2 = t * t
    log_t = math.log10(t)
    log_k1 = -356.3094 - 0.06091964 * t + 21834.37 / t + 126.8339 * log_t - 1684915.0 / t2
    log_k2 = -107.8871 - 0.032528 * t + 5151.79 / t + 38.92561 * log_t - 563713.9 / t2
    log_ksp = -171.9065 - 0.077993 * t + 2839.319 / t + 71.595 * log_t
    log_kw = -4470.99 / t + 6.0875 - 0.01706 * t
    return 10.0**log_k1, 10.0**log_k2, 10.0**log_ksp, 10.0**log_kw


def _davies_activity_coefficients(ionic_strength: float) -> tuple[float, float]:
    """Davies-equation activity coefficients ``(gamma_1, gamma_2)`` for z = 1 and z = 2."""
    sqrt_i = math.sqrt(ionic_strength)
    bracket = sqrt_i / (1.0 + sqrt_i) - 0.3 * ionic_strength
    gamma_1 = 10.0 ** (-_A_DAVIES_25C * 1.0 * bracket)
    gamma_2 = 10.0 ** (-_A_DAVIES_25C * 4.0 * bracket)
    return gamma_1, gamma_2


def calcium_carbonate_precipitation_potential(
    ph: float,
    temperature_c: float,
    calcium_hardness: float,
    total_alkalinity: float,
    tds: float | None = None,
    ionic_strength: float | None = None,
) -> float:
    """Calcium Carbonate Precipitation Potential (CCPP), in mg/L as CaCO3.

    The signed mass of calcium carbonate that must **precipitate** (positive) or
    **dissolve** (negative) to bring the water to exact calcite saturation
    (``SI = 0``), computed for a closed system in which the total alkalinity and
    CO2-acidity are conserved as CaCO3 is exchanged (see the module docstring for
    the method and the Plummer & Busenberg / Wojtowicz references).

    Provide the ionic strength directly (``ionic_strength``, mol/L) or a ``tds``
    (mg/L) from which it is estimated as ``I = 2.5e-5 * TDS`` via
    :func:`cooling_tower_chem.balance.ionic_strength_from_tds`.

    Parameters
    ----------
    ph:
        Measured pH of the water (treated as ``-log10`` of the H+ *activity*).
    temperature_c:
        Water temperature in degrees Celsius.
    calcium_hardness:
        Calcium hardness in mg/L **as CaCO3** (must be > 0).
    total_alkalinity:
        Total (carbonate) alkalinity in mg/L **as CaCO3** (must be > 0).
    tds:
        Total dissolved solids in mg/L, used to estimate ionic strength when
        ``ionic_strength`` is not given.
    ionic_strength:
        Ionic strength in mol/L. Takes precedence over ``tds`` when both are
        given; the Davies model it feeds is valid to about 0.5 mol/L.

    Returns
    -------
    float
        CCPP in mg/L as CaCO3: ``> 0`` scale-forming (calcite will precipitate),
        ``< 0`` aggressive (calcite will dissolve), ``~ 0`` at saturation.

    Notes
    -----
    This is a screening estimate, not a substitute for a full speciation model.
    Its magnitude is dominated by the activity correction, so it is sensitive to
    the ionic strength: the ``I = 2.5e-5 * TDS`` estimate is rough, and the
    dependency-free Davies model carries no ion pairing (e.g. CaHCO3+, CaCO3-aq),
    so it tends to over-predict precipitation for hard, high-TDS water relative to
    an ion-pairing model such as PHREEQC. Supply a measured or model-derived
    ``ionic_strength`` when accuracy matters. The Davies ``A`` is held at its
    25 C value (0.509); the closed-system assumption (no CO2 exchange with the
    atmosphere) suits a snapshot of a recirculating loop rather than an aerated
    basin.

    Raises
    ------
    ValueError
        If an input is non-finite or non-physical, or if neither ``tds`` nor
        ``ionic_strength`` is provided.
    """
    ph = _require_finite("ph", ph)
    temperature_c = _require_temperature(temperature_c)
    calcium_hardness = _require_positive("calcium_hardness", calcium_hardness)
    total_alkalinity = _require_positive("total_alkalinity", total_alkalinity)
    if ionic_strength is None:
        if tds is None:
            raise ValueError("provide either tds or ionic_strength")
        ionic_strength = ionic_strength_from_tds(tds)
    else:
        ionic_strength = _require_positive("ionic_strength", ionic_strength)

    k1, k2, ksp, kw = _plummer_busenberg_constants(temperature_c)
    gamma_1, gamma_2 = _davies_activity_coefficients(ionic_strength)
    # Conditional (concentration-based) constants; H+ is carried as an activity,
    # so pH = -log10(a_H+) and the carbonate/hydroxide species are concentrations.
    ck1 = k1 / gamma_1
    ck2 = k2 * gamma_1 / gamma_2
    cksp = ksp / (gamma_2 * gamma_2)
    ckw = kw / gamma_1

    def _alpha1_alpha2(h: float) -> tuple[float, float]:
        denom = h * h + h * ck1 + ck1 * ck2
        return h * ck1 / denom, ck1 * ck2 / denom

    def _alkalinity(h: float, ct: float) -> float:
        alpha_1, alpha_2 = _alpha1_alpha2(h)
        return ct * (alpha_1 + 2.0 * alpha_2) + ckw / h - h / gamma_1

    def _equilibrium_h(ct: float, alk_target: float) -> float:
        # Alkalinity strictly decreases with [H+]; bracket pH 0..14 and bisect
        # geometrically (i.e. linearly in pH).
        low, high = 1e-14, 1.0
        for _ in range(200):
            mid = math.sqrt(low * high)
            if _alkalinity(mid, ct) > alk_target:
                low = mid
            else:
                high = mid
            if high - low < 1e-18:
                break
        return math.sqrt(low * high)

    h_initial = 10.0 ** (-ph)
    alpha1_i, alpha2_i = _alpha1_alpha2(h_initial)
    alk_total = total_alkalinity / _CACO3_EQUIV_MG        # eq/L
    ca_total = calcium_hardness / _CACO3_MOLAR_MASS_MG      # mol/L
    ct_initial = (alk_total - ckw / h_initial + h_initial / gamma_1) / (
        alpha1_i + 2.0 * alpha2_i
    )

    def _saturation_gap(x: float) -> float:
        # x = mol/L of CaCO3 precipitated (>0) or dissolved (<0). Removing x
        # removes x from Ca and from total carbonate and 2x from alkalinity.
        ct_eq = ct_initial - x
        h_eq = _equilibrium_h(ct_eq, alk_total - 2.0 * x)
        _, alpha2_eq = _alpha1_alpha2(h_eq)
        return (ca_total - x) * ct_eq * alpha2_eq - cksp

    # The saturation gap decreases monotonically in x. Bracket the root.
    if _saturation_gap(0.0) >= 0.0:
        # Supersaturated: precipitate, 0 < x < min(Ca, CT).
        low, high = 0.0, min(ca_total, ct_initial) * (1.0 - 1e-12)
    else:
        # Undersaturated: dissolve, x < 0. Grow the bracket until the gap turns.
        low, high = -1e-9, 0.0
        for _ in range(200):
            if _saturation_gap(low) > 0.0:
                break
            low *= 2.0
        else:  # pragma: no cover - unreachable for physical inputs
            raise ValueError("could not bracket the calcite equilibrium state")

    for _ in range(200):
        mid = 0.5 * (low + high)
        if _saturation_gap(mid) > 0.0:
            low = mid
        else:
            high = mid
        if high - low < 1e-18:
            break
    x = 0.5 * (low + high)
    return x * _CACO3_MOLAR_MASS_MG
