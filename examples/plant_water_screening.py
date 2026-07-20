"""Batch-screen a set of cooling-tower water analyses into a risk table.

A plant may run several towers (or one tower at several cycles of
concentration) off different makeup sources. This script takes a small inline
dataset of recirculating-water analyses and prints one row per water with its
Langelier (LSI), Ryznar (RSI), Puckorius (PSI), and CCPP values, the
Larson-Skold corrosion ratio, and a one-word scale/corrosion verdict.

Everything comes from the real library API: each analysis becomes a
``WaterSample``; the numbers are read straight off ``.lsi()``, ``.rsi()``,
``.psi()``, ``.ccpp()`` and ``.larson_skold_index()``, and the verdict reuses
the library's own ``interpret_*`` bands.

Run:  python examples/plant_water_screening.py
"""

from cooling_tower_chem import Tendency, WaterSample, interpret_lsi

# Synthetic but realistic recirculating cooling-tower waters. Calcium hardness
# and total alkalinity are mg/L as CaCO3; chloride and sulfate are mg/L as the
# ion; conductivity is uS/cm (TDS is derived from it by the library).
WATERS = [
    dict(name="RO makeup, 2 cycles", ph=7.2, temperature_c=28,
         calcium_hardness=30, total_alkalinity=25, conductivity_us_cm=230,
         chloride=8, sulfate=6),
    dict(name="Soft city, 3 cycles", ph=7.6, temperature_c=30,
         calcium_hardness=95, total_alkalinity=70, conductivity_us_cm=520,
         chloride=25, sulfate=30),
    dict(name="Balanced target", ph=7.9, temperature_c=30,
         calcium_hardness=250, total_alkalinity=180, conductivity_us_cm=1540,
         chloride=45, sulfate=55),
    dict(name="Municipal, 4 cycles", ph=8.0, temperature_c=32,
         calcium_hardness=320, total_alkalinity=210, conductivity_us_cm=1850,
         chloride=120, sulfate=150),
    dict(name="Low-alkalinity acidic", ph=6.8, temperature_c=29,
         calcium_hardness=120, total_alkalinity=35, conductivity_us_cm=900,
         chloride=140, sulfate=110),
    dict(name="Coastal high-chloride", ph=7.8, temperature_c=33,
         calcium_hardness=300, total_alkalinity=120, conductivity_us_cm=3400,
         chloride=600, sulfate=200),
    dict(name="Hard well, 6 cycles", ph=8.4, temperature_c=35,
         calcium_hardness=650, total_alkalinity=320, conductivity_us_cm=3700,
         chloride=90, sulfate=110),
    dict(name="Alkaline high-pH", ph=9.0, temperature_c=34,
         calcium_hardness=400, total_alkalinity=260, conductivity_us_cm=2800,
         chloride=90, sulfate=110),
    dict(name="Concentrated blowdown", ph=8.6, temperature_c=36,
         calcium_hardness=800, total_alkalinity=380, conductivity_us_cm=4900,
         chloride=350, sulfate=400),
]

_SCALING = {Tendency.SCALE_FORMING, Tendency.SEVERELY_SCALE_FORMING}
_CORROSIVE = {Tendency.CORROSIVE, Tendency.SEVERELY_CORROSIVE}


def verdict(lsi: float, larson_skold: float) -> str:
    """Collapse the LSI band and Larson-Skold ratio into a short verdict."""
    tendency, _ = interpret_lsi(lsi)
    if tendency in _SCALING:
        base = "SCALING"
    elif tendency in _CORROSIVE:
        base = "corrosive"
    else:
        base = "balanced"
    # Larson-Skold >= 0.8 flags chloride/sulfate-driven attack on mild steel,
    # independent of the carbonate-scaling picture the LSI describes.
    if larson_skold >= 0.8:
        base += " + Cl/SO4 attack"
    return base


def main() -> None:
    header = f"{'Water':22} {'pH':>4} {'LSI':>6} {'RSI':>6} {'PSI':>6} " \
             f"{'CCPP':>7} {'L-S':>5}  Verdict"
    print(header)
    print("-" * len(header))
    for w in WATERS:
        fields = {k: v for k, v in w.items() if k != "name"}
        s = WaterSample(**fields)
        ls = s.larson_skold_index()
        print(
            f"{w['name']:22} {w['ph']:>4} {s.lsi():>6.2f} {s.rsi():>6.2f} "
            f"{s.psi():>6.2f} {s.ccpp():>7.1f} {ls:>5.2f}  {verdict(s.lsi(), ls)}"
        )
    print()
    print("LSI/RSI/PSI: carbonate scaling vs. corrosion (see interpret_* bands).")
    print("CCPP: mg/L as CaCO3 that would deposit (+) or dissolve (-) at saturation.")
    print("L-S (Larson-Skold): (Cl- + SO4^2-)/alkalinity; >=0.8 raises steel corrosion.")


if __name__ == "__main__":
    main()


# --- Adapting this to your water type -------------------------------------
# Replace the WATERS list with your own analyses. Keep the units the library
# expects: calcium hardness and total alkalinity in mg/L as CaCO3, chloride and
# sulfate in mg/L as the ion, temperature in C. Give either `conductivity_us_cm`
# (TDS is derived with the default 0.65 factor) or `tds` directly; pass
# `tds_factor=` to override the conductivity->TDS factor for your water.
#
# If you routinely screen one recurring water chemistry (a specific plant,
# process, or product line), that "preset" is worth sharing. The library is MIT
# licensed on GitHub -- fork it, add your preset as a small helper or dataset,
# and the community screening table grows a column.
