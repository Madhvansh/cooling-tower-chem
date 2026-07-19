"""A convenience ``WaterSample`` that computes every index from one input.

Example:

```python
from cooling_tower_chem import WaterSample

s = WaterSample(ph=8.2, temperature_c=32, calcium_hardness=450,
                total_alkalinity=250, conductivity_us_cm=2400,
                chloride=180, sulfate=120)
s.lsi()                        # 1.38
s.report()["lsi"]["tendency"]  # 'scale_forming'
```
"""

from __future__ import annotations

from dataclasses import dataclass

from . import balance, convert, indices, interpret

__all__ = ["WaterSample"]


@dataclass
class WaterSample:
    """A single water analysis, with lazy accessors for every index.

    Required fields: ``ph``, ``temperature_c``, ``calcium_hardness`` and
    ``total_alkalinity`` (hardness and alkalinity in mg/L as CaCO3).

    ``tds`` may be given directly (mg/L) or derived from ``conductivity_us_cm``.
    ``chloride`` and ``sulfate`` (mg/L) are only needed for the Larson-Skold
    index.
    """

    ph: float
    temperature_c: float
    calcium_hardness: float
    total_alkalinity: float
    tds: float | None = None
    conductivity_us_cm: float | None = None
    chloride: float | None = None
    sulfate: float | None = None
    tds_factor: float = balance.DEFAULT_TDS_FACTOR

    @classmethod
    def from_us_units(
        cls,
        ph: float,
        temperature_f: float,
        calcium_hardness_gpg: float,
        total_alkalinity_gpg: float,
        tds: float | None = None,
        conductivity_us_cm: float | None = None,
        chloride: float | None = None,
        sulfate: float | None = None,
        tds_factor: float = balance.DEFAULT_TDS_FACTOR,
    ) -> WaterSample:
        """Build a :class:`WaterSample` from customary US units.

        Many US practitioners report temperature in degrees Fahrenheit and
        calcium hardness / total alkalinity in grains per US gallon (as CaCO3).
        This constructor accepts those units and converts them to the SI
        conventions the indices expect, via
        :func:`cooling_tower_chem.convert.fahrenheit_to_celsius` and
        :func:`cooling_tower_chem.convert.grains_per_gallon_to_mg_l`
        (1 grain/gal = 17.118 mg/L as CaCO3). The signature is otherwise
        parallel to :class:`WaterSample`.

        Parameters
        ----------
        ph:
            Water pH (dimensionless), unchanged.
        temperature_f:
            Water temperature in degrees **Fahrenheit**.
        calcium_hardness_gpg:
            Calcium hardness in **grains per US gallon** as CaCO3.
        total_alkalinity_gpg:
            Total alkalinity in **grains per US gallon** as CaCO3.
        tds:
            Total dissolved solids in **mg/L** (its usual unit), or ``None`` to
            derive it from ``conductivity_us_cm``.
        conductivity_us_cm:
            Conductivity in **microsiemens/cm** (its usual unit); used to derive
            TDS when ``tds`` is not given.
        chloride, sulfate:
            Concentrations in **mg/L** as the ion (their usual units), for the
            Larson-Skold index.
        tds_factor:
            TDS-from-conductivity factor (mg/L per uS/cm), same as
            :class:`WaterSample`.

        Returns
        -------
        WaterSample
            An instance whose fields are all in SI units, so every index method
            behaves identically to one built with the primary constructor.

        Example
        -------
        ```python
        # 90 F, 26.3 gpg calcium hardness, 14.6 gpg alkalinity as CaCO3.
        s = WaterSample.from_us_units(
            ph=8.2, temperature_f=90,
            calcium_hardness_gpg=26.3, total_alkalinity_gpg=14.6,
            conductivity_us_cm=2400,
        )
        ```
        """
        return cls(
            ph=ph,
            temperature_c=convert.fahrenheit_to_celsius(temperature_f),
            calcium_hardness=convert.grains_per_gallon_to_mg_l(calcium_hardness_gpg),
            total_alkalinity=convert.grains_per_gallon_to_mg_l(total_alkalinity_gpg),
            tds=tds,
            conductivity_us_cm=conductivity_us_cm,
            chloride=chloride,
            sulfate=sulfate,
            tds_factor=tds_factor,
        )

    def effective_tds(self) -> float:
        """TDS in mg/L, using the measured value or deriving it from conductivity."""
        if self.tds is not None:
            return self.tds
        if self.conductivity_us_cm is not None:
            return balance.tds_from_conductivity(
                self.conductivity_us_cm, self.tds_factor
            )
        raise ValueError(
            "Provide either tds or conductivity_us_cm to compute saturation indices"
        )

    def ph_of_saturation(self) -> float:
        return indices.ph_of_saturation(
            self.temperature_c,
            self.effective_tds(),
            self.calcium_hardness,
            self.total_alkalinity,
        )

    def lsi(self) -> float:
        return indices.langelier_saturation_index(
            self.ph,
            self.temperature_c,
            self.effective_tds(),
            self.calcium_hardness,
            self.total_alkalinity,
        )

    def rsi(self) -> float:
        return indices.ryznar_stability_index(
            self.ph,
            self.temperature_c,
            self.effective_tds(),
            self.calcium_hardness,
            self.total_alkalinity,
        )

    def psi(self) -> float:
        return indices.puckorius_scaling_index(
            self.temperature_c,
            self.effective_tds(),
            self.calcium_hardness,
            self.total_alkalinity,
        )

    def aggressiveness_index(self) -> float:
        return indices.aggressiveness_index(
            self.ph, self.calcium_hardness, self.total_alkalinity
        )

    def stiff_davis_index(self) -> float:
        """Stiff-Davis Stability Index, with ionic strength estimated from TDS.

        For high-salinity water only (see
        :func:`cooling_tower_chem.indices.stiff_davis_index`). Not included in
        :meth:`report`, which targets ordinary cooling-tower water.
        """
        return indices.stiff_davis_index(
            self.ph,
            self.temperature_c,
            self.calcium_hardness,
            self.total_alkalinity,
            tds=self.effective_tds(),
        )

    def larson_skold_index(self) -> float | None:
        """Larson-Skold index, or ``None`` if chloride/sulfate were not provided."""
        if self.chloride is None or self.sulfate is None:
            return None
        return indices.larson_skold_index(
            self.chloride, self.sulfate, self.total_alkalinity
        )

    def report(self) -> dict:
        """Return every available index with its interpretation as a plain dict.

        Keys are index names; each value has ``value``, ``tendency`` and
        ``description``. Larson-Skold is included only when chloride and sulfate
        are present. The result is JSON-serializable.
        """
        lsi = self.lsi()
        rsi = self.rsi()
        psi = self.psi()
        ai = self.aggressiveness_index()

        lsi_t, lsi_desc = interpret.interpret_lsi(lsi)
        rsi_t, rsi_desc = interpret.interpret_rsi(rsi)
        psi_t, psi_desc = interpret.interpret_psi(psi)
        ai_t, ai_desc = interpret.interpret_aggressiveness(ai)

        report: dict = {
            "ph_of_saturation": round(self.ph_of_saturation(), 3),
            "lsi": {
                "value": round(lsi, 3),
                "tendency": str(lsi_t),
                "description": lsi_desc,
            },
            "rsi": {
                "value": round(rsi, 3),
                "tendency": str(rsi_t),
                "description": rsi_desc,
            },
            "psi": {
                "value": round(psi, 3),
                "tendency": str(psi_t),
                "description": psi_desc,
            },
            "aggressiveness_index": {
                "value": round(ai, 3),
                "tendency": str(ai_t),
                "description": ai_desc,
            },
        }

        ls = self.larson_skold_index()
        if ls is not None:
            ls_t, ls_desc = interpret.interpret_larson_skold(ls)
            report["larson_skold_index"] = {
                "value": round(ls, 3),
                "tendency": str(ls_t),
                "description": ls_desc,
            }
        return report
