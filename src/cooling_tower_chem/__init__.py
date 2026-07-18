"""cooling-tower-chem: water-stability and corrosion indices for cooling towers.

A small, dependency-free toolkit for the classical water-chemistry calculations
used to run evaporative cooling towers and other industrial water systems:

* Saturation / stability indices - :func:`langelier_saturation_index` (LSI),
  :func:`ryznar_stability_index` (RSI), :func:`puckorius_scaling_index` (PSI),
  :func:`larson_skold_index`, :func:`aggressiveness_index`, and the underlying
  :func:`ph_of_saturation`.
* Water balance - :func:`cycles_of_concentration`, :func:`evaporation_loss`,
  :func:`blowdown_loss`, :func:`makeup_water`, and TDS/conductivity conversion.
* Interpretation - :func:`interpret_lsi` and friends map a number to a plain
  ``(Tendency, description)`` pair.
* :class:`WaterSample` - hand it one analysis and get every index at once.

Everything is pure Python (standard library only), fully type-hinted, and
validated against the published formulas. Units are documented per function;
the convention throughout is mg/L as CaCO3 for hardness and alkalinity, mg/L for
TDS and ions, and degrees Celsius for temperature.
"""

from __future__ import annotations

from .balance import (
    DEFAULT_TDS_FACTOR,
    blowdown_loss,
    conductivity_from_tds,
    cycles_from_flows,
    cycles_of_concentration,
    drift_loss,
    evaporation_loss,
    makeup_water,
    tds_from_conductivity,
    water_saved_by_increasing_cycles,
)
from .convert import (
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
from .indices import (
    aggressiveness_index,
    langelier_saturation_index,
    larson_skold_index,
    ph_of_saturation,
    puckorius_scaling_index,
    ryznar_stability_index,
)
from .interpret import (
    Tendency,
    interpret_aggressiveness,
    interpret_larson_skold,
    interpret_lsi,
    interpret_psi,
    interpret_rsi,
)
from .sample import WaterSample
from .tower import CoolingTower

__version__ = "0.1.0"

__all__ = [
    "__version__",
    # indices
    "ph_of_saturation",
    "langelier_saturation_index",
    "ryznar_stability_index",
    "puckorius_scaling_index",
    "larson_skold_index",
    "aggressiveness_index",
    # balance
    "DEFAULT_TDS_FACTOR",
    "tds_from_conductivity",
    "conductivity_from_tds",
    "cycles_of_concentration",
    "evaporation_loss",
    "drift_loss",
    "blowdown_loss",
    "makeup_water",
    "cycles_from_flows",
    "water_saved_by_increasing_cycles",
    # interpret
    "Tendency",
    "interpret_lsi",
    "interpret_rsi",
    "interpret_psi",
    "interpret_larson_skold",
    "interpret_aggressiveness",
    # convenience
    "WaterSample",
    "CoolingTower",
    # unit conversions
    "EQUIVALENT_WEIGHTS",
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
