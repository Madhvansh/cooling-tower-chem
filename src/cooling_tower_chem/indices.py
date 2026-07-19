"""Water-stability and corrosion indices for cooling-tower and process water.

All indices use the classical water-chemistry conventions:

* Calcium hardness and total alkalinity are expressed in **mg/L as CaCO3**.
* Total dissolved solids (TDS) is in **mg/L**.
* Temperature is in **degrees Celsius**.
* Chloride and sulfate are in **mg/L** (as the ion).

The saturation pH (``ph_of_saturation``) uses the standard analytical form of
Langelier's equation::

    pHs = (9.3 + A + B) - (C + D)
    A = (log10(TDS) - 1) / 10
    B = -13.12 * log10(T_kelvin) + 34.55
    C = log10(calcium_hardness_as_CaCO3) - 0.4
    D = log10(total_alkalinity_as_CaCO3)

References
----------
* Langelier, W. F. (1936). "The Analytical Control of Anti-Corrosion Water
  Treatment." *J. AWWA* 28(10), 1500-1521.
* Ryznar, J. W. (1944). "A New Index for Determining Amount of Calcium
  Carbonate Scale Formed by a Water." *J. AWWA* 36(4), 472-483.
* Puckorius, P. R. & Brooke, J. M. (1991). "A New Practical Index for Calcium
  Carbonate Scale Prediction in Cooling Tower Systems." *Corrosion* 47(4).
* Larson, T. E. & Skold, R. V. (1958). "Laboratory Studies Relating Mineral
  Quality of Water to Corrosion of Steel and Cast Iron." *Corrosion* 14(6).
"""

from __future__ import annotations

import math

from .balance import ionic_strength_from_tds

__all__ = [
    "ph_of_saturation",
    "langelier_saturation_index",
    "ryznar_stability_index",
    "puckorius_scaling_index",
    "larson_skold_index",
    "aggressiveness_index",
    "stiff_davis_index",
    "stiff_davis_ph_of_saturation",
]

# Equivalent weights (mg per milliequivalent) used by the Larson-Skold index.
_EQ_WEIGHT_CHLORIDE = 35.45
_EQ_WEIGHT_SULFATE = 48.03  # SO4(2-): 96.06 / 2
_EQ_WEIGHT_CACO3 = 50.04    # CaCO3: 100.09 / 2 (alkalinity/hardness as CaCO3)

# Molar mass / equivalent weight of CaCO3 in mg (for molar concentrations).
_CACO3_MOLAR_MASS_MG = 100086.9  # mg per mol
_CACO3_EQUIV_MG = 50043.45       # mg per equivalent


def _require_positive(name: str, value: float) -> float:
    """Validate that *value* is a positive, finite number."""
    if value is None:
        raise ValueError(f"{name} is required and must be a positive number")
    if not math.isfinite(value):
        raise ValueError(f"{name} must be a finite number, got {value!r}")
    if value <= 0:
        raise ValueError(
            f"{name} must be > 0 (a logarithm is taken); got {value!r}"
        )
    return float(value)


def _require_temperature(temperature_c: float) -> float:
    if temperature_c is None or not math.isfinite(temperature_c):
        raise ValueError(f"temperature_c must be finite, got {temperature_c!r}")
    if temperature_c <= -273.15:
        raise ValueError(
            f"temperature_c must be above absolute zero (-273.15 C); got {temperature_c!r}"
        )
    return float(temperature_c)


def ph_of_saturation(
    temperature_c: float,
    tds: float,
    calcium_hardness: float,
    total_alkalinity: float,
) -> float:
    """Return the pH of calcium-carbonate saturation (``pHs``).

    Parameters
    ----------
    temperature_c:
        Water temperature in degrees Celsius.
    tds:
        Total dissolved solids in mg/L. If you only have conductivity, convert
        it first with :func:`cooling_tower_chem.balance.tds_from_conductivity`.
    calcium_hardness:
        Calcium hardness in mg/L **as CaCO3**.
    total_alkalinity:
        Total alkalinity in mg/L **as CaCO3**.

    Returns
    -------
    float
        The saturation pH. ``LSI = pH - pHs`` and ``RSI = 2*pHs - pH``.
    """
    temperature_c = _require_temperature(temperature_c)
    tds = _require_positive("tds", tds)
    calcium_hardness = _require_positive("calcium_hardness", calcium_hardness)
    total_alkalinity = _require_positive("total_alkalinity", total_alkalinity)

    a = (math.log10(tds) - 1.0) / 10.0
    b = -13.12 * math.log10(temperature_c + 273.15) + 34.55
    c = math.log10(calcium_hardness) - 0.4
    d = math.log10(total_alkalinity)
    return (9.3 + a + b) - (c + d)


def langelier_saturation_index(
    ph: float,
    temperature_c: float,
    tds: float,
    calcium_hardness: float,
    total_alkalinity: float,
) -> float:
    """Langelier Saturation Index (LSI): ``pH - pHs``.

    * ``LSI > 0`` — water is supersaturated; calcium carbonate tends to
      precipitate (scaling).
    * ``LSI = 0`` — water is at equilibrium.
    * ``LSI < 0`` — water is undersaturated; it tends to dissolve calcium
      carbonate (corrosive / aggressive).

    For most cooling-tower programs a small positive LSI (roughly ``0`` to
    ``+1``) is targeted to lay a thin protective scale without fouling.
    """
    phs = ph_of_saturation(temperature_c, tds, calcium_hardness, total_alkalinity)
    return float(ph) - phs


def ryznar_stability_index(
    ph: float,
    temperature_c: float,
    tds: float,
    calcium_hardness: float,
    total_alkalinity: float,
) -> float:
    """Ryznar Stability Index (RSI): ``2*pHs - pH``.

    The RSI is always positive and is read on an empirical scale:

    * ``RSI < 6``   — scale-forming;
    * ``6 <= RSI <= 7`` — approximately balanced;
    * ``RSI > 7``   — corrosive (increasingly so above ~8).
    """
    phs = ph_of_saturation(temperature_c, tds, calcium_hardness, total_alkalinity)
    return 2.0 * phs - float(ph)


def puckorius_scaling_index(
    temperature_c: float,
    tds: float,
    calcium_hardness: float,
    total_alkalinity: float,
) -> float:
    """Puckorius (Practical) Scaling Index (PSI): ``2*pHs - pH_eq``.

    The PSI replaces the measured pH of the RSI with an *equilibrium* pH driven
    only by alkalinity, ``pH_eq = 1.465 * log10(total_alkalinity) + 4.54``. This
    makes it a better predictor than LSI/RSI for the highly buffered,
    recirculating water typical of cooling towers, where measured pH can swing
    without changing scaling potential.

    Interpreted on the same empirical scale as the RSI (``< 6`` scaling,
    ``6-7`` balanced, ``> 7`` corrosive). Note the PSI does not take a measured
    pH argument by design.
    """
    total_alkalinity = _require_positive("total_alkalinity", total_alkalinity)
    phs = ph_of_saturation(temperature_c, tds, calcium_hardness, total_alkalinity)
    ph_eq = 1.465 * math.log10(total_alkalinity) + 4.54
    return 2.0 * phs - ph_eq


def larson_skold_index(
    chloride: float,
    sulfate: float,
    total_alkalinity: float,
) -> float:
    """Larson-Skold index: corrosivity of water toward mild steel.

    Defined as the equivalents ratio
    ``(Cl- + SO4(2-)) / (HCO3- + CO3(2-))``. Alkalinity is supplied here as
    mg/L **as CaCO3** and converted to equivalents internally.

    * ``< 0.8`` — chlorides and sulfates are unlikely to interfere with a
      protective film;
    * ``0.8 - 1.2`` — chlorides and sulfates may increase corrosion rates;
    * ``> 1.2`` — high corrosion rates on mild steel are expected.

    Parameters
    ----------
    chloride, sulfate:
        Concentrations in mg/L (as the ion).
    total_alkalinity:
        Total alkalinity in mg/L as CaCO3 (must be > 0).
    """
    if chloride is None or not math.isfinite(chloride) or chloride < 0:
        raise ValueError(f"chloride must be a non-negative number, got {chloride!r}")
    if sulfate is None or not math.isfinite(sulfate) or sulfate < 0:
        raise ValueError(f"sulfate must be a non-negative number, got {sulfate!r}")
    total_alkalinity = _require_positive("total_alkalinity", total_alkalinity)

    epm_chloride = chloride / _EQ_WEIGHT_CHLORIDE
    epm_sulfate = sulfate / _EQ_WEIGHT_SULFATE
    epm_alkalinity = total_alkalinity / _EQ_WEIGHT_CACO3
    return (epm_chloride + epm_sulfate) / epm_alkalinity


def _stiff_davis_k(ionic_strength: float, temperature_c: float) -> float:
    """The Stiff-Davis ``K`` constant from the ASTM D4582 / USBR curve fit.

    ``K`` plays the role of the Langelier saturation constant, extended to high
    ionic strength. Source: USBR, *Water Chemistry Analysis for Water Conveyance,
    Storage, and Desalination Projects* (2013), Eqs. 13-14, developed from the
    ASTM D4582 chart. Temperature is in degrees Celsius.
    """
    strength = _require_positive("ionic_strength", ionic_strength)
    t = _require_temperature(temperature_c)
    if strength < 1.2:
        return (
            2.022 * math.exp((math.log(strength) + 7.544) ** 2 / 102.60)
            - 0.0002 * t * t
            + 0.00097 * t
            + 0.262
        )
    return -0.1 * strength - 0.0002 * t * t - 0.00097 * t + 3.887


def stiff_davis_ph_of_saturation(
    temperature_c: float,
    calcium_hardness: float,
    total_alkalinity: float,
    ionic_strength: float,
) -> float:
    """Stiff-Davis pH of saturation: ``pHs = pCa + pAlk + K``.

    ``pCa`` and ``pAlk`` are molar negative logs, derived from the CaCO3-basis
    inputs (``[Ca] = hardness / 100086.9`` mol/L, ``[Alk] = alkalinity / 50043.45``
    eq/L). ``K`` comes from :func:`_stiff_davis_k`.
    """
    calcium_hardness = _require_positive("calcium_hardness", calcium_hardness)
    total_alkalinity = _require_positive("total_alkalinity", total_alkalinity)
    p_ca = -math.log10(calcium_hardness / _CACO3_MOLAR_MASS_MG)
    p_alk = -math.log10(total_alkalinity / _CACO3_EQUIV_MG)
    return p_ca + p_alk + _stiff_davis_k(ionic_strength, temperature_c)


def stiff_davis_index(
    ph: float,
    temperature_c: float,
    calcium_hardness: float,
    total_alkalinity: float,
    tds: float | None = None,
    ionic_strength: float | None = None,
) -> float:
    """Stiff-Davis Stability Index (S&DSI): ``pH - pHs``, for high-salinity water.

    The Langelier/Ryznar indices lose accuracy at high ionic strength (brines,
    seawater, concentrated blowdown). The Stiff-Davis index corrects for this by
    replacing the LSI temperature/TDS terms with an ionic-strength-dependent
    constant ``K``. Read like the LSI: ``> 0`` scale-forming, ``< 0`` corrosive.

    Provide the ionic strength directly (mol/L), or ``tds`` (mg/L) to estimate it
    via ``I = 2.5e-5 * TDS``. Hardness and alkalinity are mg/L as CaCO3.

    .. note::
        S&DSI is intended for the high-salinity regime (roughly TDS > 10,000 mg/L,
        ionic strength >= ~0.05 mol/L). The ``K`` curve fit is unreliable at very
        low ionic strength; use :func:`langelier_saturation_index` for
        low-salinity water instead.

    References: Stiff & Davis (1952); ASTM D4582; USBR (2013).
    """
    if ionic_strength is None:
        if tds is None:
            raise ValueError("provide either tds or ionic_strength")
        ionic_strength = ionic_strength_from_tds(tds)
    phs = stiff_davis_ph_of_saturation(
        temperature_c, calcium_hardness, total_alkalinity, ionic_strength
    )
    return float(ph) - phs


def aggressiveness_index(
    ph: float,
    calcium_hardness: float,
    total_alkalinity: float,
) -> float:
    """AWWA Aggressiveness Index (AI): ``pH + log10(calcium_hardness * alkalinity)``.

    Originally standardized (AWWA C400) for asbestos-cement pipe, the AI is a
    simplified, temperature-independent corrosivity screen:

    * ``AI >= 12`` — non-aggressive;
    * ``10 <= AI < 12`` — moderately aggressive;
    * ``AI < 10``  — highly aggressive.

    Hardness and alkalinity are in mg/L as CaCO3.
    """
    calcium_hardness = _require_positive("calcium_hardness", calcium_hardness)
    total_alkalinity = _require_positive("total_alkalinity", total_alkalinity)
    return float(ph) + math.log10(calcium_hardness * total_alkalinity)
