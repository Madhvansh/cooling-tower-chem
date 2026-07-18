"""A :class:`CoolingTower` convenience object over the water-balance functions.

Give it a circulating flow, a cooling range, and a target cycles of
concentration; read back the evaporation, drift, blowdown and makeup streams,
and project how the recirculating water concentrates relative to the makeup.
"""

from __future__ import annotations

from dataclasses import dataclass

from . import balance
from .sample import WaterSample

__all__ = ["CoolingTower"]


@dataclass
class CoolingTower:
    """Steady-state water balance for an evaporative cooling tower.

    Parameters
    ----------
    circulation_rate:
        Recirculating water flow in any consistent volumetric unit (e.g. m3/h).
        Every returned stream is in the same unit.
    delta_t_c:
        Cooling range (temperature drop across the tower) in degrees C.
    cycles:
        Target cycles of concentration. Required to compute blowdown/makeup.
    drift_fraction:
        Drift (windage) as a fraction of circulation. Default 0.0002 (0.02%).
    latent_heat_kj_per_kg:
        Optional override for the latent heat used by the evaporation estimate.
    """

    circulation_rate: float
    delta_t_c: float
    cycles: float | None = None
    drift_fraction: float = 0.0002
    latent_heat_kj_per_kg: float | None = None

    @property
    def evaporation(self) -> float:
        """Evaporation loss (energy balance)."""
        return balance.evaporation_loss(
            self.circulation_rate,
            self.delta_t_c,
            latent_heat_kj_per_kg=self.latent_heat_kj_per_kg,
        )

    @property
    def drift(self) -> float:
        """Drift / windage loss."""
        return balance.drift_loss(self.circulation_rate, self.drift_fraction)

    def _require_cycles(self) -> float:
        if self.cycles is None:
            raise ValueError("cycles must be set to compute blowdown/makeup")
        return self.cycles

    @property
    def blowdown(self) -> float:
        """Blowdown required to hold ``cycles`` (needs ``cycles``)."""
        return balance.blowdown_loss(self.evaporation, self._require_cycles(), self.drift)

    @property
    def makeup(self) -> float:
        """Makeup water required (needs ``cycles``)."""
        return balance.makeup_water(self.evaporation, self.blowdown, self.drift)

    def water_balance(self) -> dict:
        """All four streams (and cycles) as a JSON-serializable dict."""
        result = {
            "evaporation": round(self.evaporation, 4),
            "drift": round(self.drift, 4),
        }
        if self.cycles is not None:
            result["blowdown"] = round(self.blowdown, 4)
            result["makeup"] = round(self.makeup, 4)
            result["cycles"] = self.cycles
        return result

    def concentrated(self, makeup_water_sample: WaterSample) -> WaterSample:
        """Project recirculating-water chemistry from the makeup analysis.

        Conservative species (hardness, alkalinity, TDS, chloride, sulfate,
        conductivity) concentrate by the cycles of concentration; pH and
        temperature are *not* scaled (they are governed by equilibria and the
        process, not by a mass balance) and are carried through unchanged. Use
        the result to estimate the LSI/RSI of the water actually in the basin.
        """
        n = self._require_cycles()

        def scaled(value: float | None) -> float | None:
            return None if value is None else value * n

        return WaterSample(
            ph=makeup_water_sample.ph,
            temperature_c=makeup_water_sample.temperature_c,
            calcium_hardness=makeup_water_sample.calcium_hardness * n,
            total_alkalinity=makeup_water_sample.total_alkalinity * n,
            tds=scaled(makeup_water_sample.tds),
            conductivity_us_cm=scaled(makeup_water_sample.conductivity_us_cm),
            chloride=scaled(makeup_water_sample.chloride),
            sulfate=scaled(makeup_water_sample.sulfate),
            tds_factor=makeup_water_sample.tds_factor,
        )
