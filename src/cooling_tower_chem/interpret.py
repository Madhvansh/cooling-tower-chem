"""Human-readable interpretation of the water-chemistry indices.

Each ``interpret_*`` function maps a numeric index to a :class:`Tendency`
(a coarse scaling/corrosion classification) and a short sentence. Thresholds
follow the conventional bands cited in the index references; they are screening
guides, not a substitute for site-specific engineering judgment.

Band edges vary between published sources (for example, some Ryznar tables put
the balanced/corrosive boundary at 6.8 rather than 7.0). This module uses the
common "RSI 6-7 balanced" convention; treat values near a boundary as
borderline rather than decisive.
"""

from __future__ import annotations

from enum import Enum

__all__ = [
    "Tendency",
    "interpret_lsi",
    "interpret_rsi",
    "interpret_psi",
    "interpret_larson_skold",
    "interpret_aggressiveness",
]


class Tendency(str, Enum):
    """Coarse classification shared by the interpretation helpers."""

    SEVERELY_CORROSIVE = "severely_corrosive"
    CORROSIVE = "corrosive"
    BALANCED = "balanced"
    SCALE_FORMING = "scale_forming"
    SEVERELY_SCALE_FORMING = "severely_scale_forming"

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.value


def interpret_lsi(lsi: float) -> tuple[Tendency, str]:
    """Interpret a Langelier Saturation Index value."""
    if lsi <= -2.0:
        return Tendency.SEVERELY_CORROSIVE, (
            f"LSI {lsi:+.2f}: severely undersaturated and aggressive; expect "
            "rapid dissolution of protective carbonate films."
        )
    if lsi < -0.5:
        return Tendency.CORROSIVE, (
            f"LSI {lsi:+.2f}: corrosive tendency; water will tend to dissolve "
            "calcium carbonate."
        )
    if lsi <= 0.5:
        return Tendency.BALANCED, (
            f"LSI {lsi:+.2f}: near saturation (balanced to slightly "
            "scale-forming) - the usual target band."
        )
    if lsi <= 1.5:
        return Tendency.SCALE_FORMING, (
            f"LSI {lsi:+.2f}: scale-forming; calcium carbonate will tend to "
            "precipitate."
        )
    return Tendency.SEVERELY_SCALE_FORMING, (
        f"LSI {lsi:+.2f}: heavily supersaturated; expect rapid scaling without "
        "inhibitor or blowdown control."
    )


def interpret_rsi(rsi: float) -> tuple[Tendency, str]:
    """Interpret a Ryznar Stability Index value."""
    if rsi < 5.5:
        return Tendency.SEVERELY_SCALE_FORMING, (
            f"RSI {rsi:.2f}: heavy scale formation expected."
        )
    if rsi < 6.2:
        return Tendency.SCALE_FORMING, (
            f"RSI {rsi:.2f}: scale-forming tendency."
        )
    if rsi <= 7.0:
        return Tendency.BALANCED, (
            f"RSI {rsi:.2f}: approximately balanced - the target band."
        )
    if rsi < 8.5:
        return Tendency.CORROSIVE, (
            f"RSI {rsi:.2f}: corrosive tendency."
        )
    return Tendency.SEVERELY_CORROSIVE, (
        f"RSI {rsi:.2f}: severely corrosive water."
    )


def interpret_psi(psi: float) -> tuple[Tendency, str]:
    """Interpret a Puckorius Scaling Index value (same bands as the RSI)."""
    tendency, text = interpret_rsi(psi)
    return tendency, text.replace("RSI", "PSI", 1)


def interpret_larson_skold(index: float) -> tuple[Tendency, str]:
    """Interpret a Larson-Skold index (corrosivity toward mild steel)."""
    if index < 0.8:
        return Tendency.BALANCED, (
            f"Larson-Skold {index:.2f}: chlorides and sulfates are unlikely to "
            "disrupt a protective film."
        )
    if index <= 1.2:
        return Tendency.CORROSIVE, (
            f"Larson-Skold {index:.2f}: chlorides and sulfates may raise "
            "corrosion rates on mild steel."
        )
    return Tendency.SEVERELY_CORROSIVE, (
        f"Larson-Skold {index:.2f}: high corrosion rates on mild steel expected."
    )


def interpret_aggressiveness(index: float) -> tuple[Tendency, str]:
    """Interpret an AWWA Aggressiveness Index value."""
    if index < 10.0:
        return Tendency.SEVERELY_CORROSIVE, (
            f"AI {index:.2f}: highly aggressive water."
        )
    if index < 12.0:
        return Tendency.CORROSIVE, (
            f"AI {index:.2f}: moderately aggressive water."
        )
    return Tendency.BALANCED, (
        f"AI {index:.2f}: non-aggressive water."
    )
