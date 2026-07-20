"""Water-balance screen for swimming pools and spas.

The same saturation math that runs a cooling tower also governs pool and spa
water: the Langelier Saturation Index (LSI) is the standard pool water-balance
number, and the CCPP puts a mass on how far the water is from calcite
saturation. This script runs a handful of pool/spa-typical analyses through the
real library API (LSI, RSI, PSI, CCPP) and interprets the LSI with the tighter
band pool operators actually use.

Pool-practice LSI bands (tighter than the library's cooling-tower default of
+/-0.5, because bathers and plaster are less tolerant than steel):

    LSI < -0.3   aggressive: dissolves plaster/grout, etches, corrodes metal
    -0.3 .. +0.3 balanced   (0.0 is the target)
    LSI > +0.3   scaling: cloudy water, scale on tile/heater elements

Run:  python examples/pool_spa_check.py
"""

from cooling_tower_chem import WaterSample

# Synthetic but realistic pool/spa analyses. Calcium hardness and total
# alkalinity are mg/L as CaCO3; TDS is mg/L (salt pools carry a lot). Cyanuric
# acid is not modelled here -- for a heavily stabilized outdoor pool, subtract
# the CYA correction from total alkalinity before reading the LSI.
POOLS = [
    dict(name="Balanced plaster pool", ph=7.5, temperature_c=28,
         calcium_hardness=250, total_alkalinity=90, tds=1000),
    dict(name="Soft/etching plaster", ph=7.4, temperature_c=27,
         calcium_hardness=120, total_alkalinity=70, tds=800),
    dict(name="High-pH scaling pool", ph=7.9, temperature_c=29,
         calcium_hardness=350, total_alkalinity=120, tds=1500),
    dict(name="Hot spa (39 C)", ph=7.6, temperature_c=39,
         calcium_hardness=250, total_alkalinity=90, tds=1500),
    dict(name="Saltwater pool", ph=7.6, temperature_c=28,
         calcium_hardness=300, total_alkalinity=100, tds=4000),
    dict(name="Cold aggressive fill", ph=7.2, temperature_c=20,
         calcium_hardness=150, total_alkalinity=60, tds=500),
    dict(name="Vinyl-liner pool", ph=7.5, temperature_c=27,
         calcium_hardness=180, total_alkalinity=80, tds=900),
]


def pool_verdict(lsi: float) -> str:
    """Pool-practice LSI band (tighter than the cooling-tower interpret_lsi)."""
    if lsi < -0.3:
        return "aggressive"
    if lsi > 0.3:
        return "scaling"
    return "balanced"


def main() -> None:
    header = f"{'Pool / spa':22} {'pH':>4} {'LSI':>6} {'RSI':>6} " \
             f"{'PSI':>6} {'CCPP':>7}  Pool balance"
    print(header)
    print("-" * len(header))
    for p in POOLS:
        fields = {k: v for k, v in p.items() if k != "name"}
        s = WaterSample(**fields)
        print(
            f"{p['name']:22} {p['ph']:>4} {s.lsi():>6.2f} {s.rsi():>6.2f} "
            f"{s.psi():>6.2f} {s.ccpp():>7.1f}  {pool_verdict(s.lsi())}"
        )
    print()
    print("LSI is the standard pool water-balance index; target 0.0 (+/-0.3).")
    print("CCPP (mg/L as CaCO3): + tends to scale/cloud, - tends to etch/dissolve.")
    print("RSI/PSI are shown for completeness; LSI + CCPP are the pool-relevant pair.")


if __name__ == "__main__":
    main()


# --- Adapting this to your water type -------------------------------------
# Swap the POOLS list for your own tests. Keep the library's units: calcium
# hardness and total alkalinity in mg/L as CaCO3, temperature in C, TDS in mg/L
# (give `conductivity_us_cm=` instead and it is derived). Two pool-specific
# notes: (1) if you run a stabilized outdoor pool, correct total alkalinity for
# cyanuric acid before reading the LSI, since CYA contributes to measured
# alkalinity but not to carbonate scaling; (2) spa temperatures push the LSI
# positive fast -- a spa balanced cold will scale hot.
#
# If you maintain a fixed target chemistry (a plaster start-up curve, a salt-pool
# spec, a spa preset), it is worth codifying. The library is MIT on GitHub --
# fork it and add your water-type preset so the next operator starts from a known
# balance point instead of a blank spreadsheet.
