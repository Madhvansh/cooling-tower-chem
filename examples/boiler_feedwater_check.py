"""Residual-scaling screen across a boiler pre-treatment train.

Boiler feedwater is deliberately softened, dealkalized, or demineralized so that
almost no calcium carbonate remains: in a boiler any residual hardness bakes onto
heat-transfer surfaces as hard scale. So a *good* boiler feedwater reads
strongly **undersaturated** (aggressive) on the Langelier index -- there is no
protective carbonate film in a boiler, and corrosion is instead controlled
chemically (deaeration, oxygen scavenger, pH elevation, phosphate/polymer). Used
this way the LSI/CCPP are a **residual-hardness screen**: a feedwater that reads
scale-forming means hardness broke through and will foul tubes.

This walks one raw water through successive treatment steps and prints the
indices at each stage, using the real library API (LSI, RSI, PSI, CCPP).

Validity caveat: the Langelier/Ryznar/Puckorius indices and the CCPP
(Plummer & Busenberg calcite fits) were developed for ~0-90 C potable/cooling
water. The deaerator/economizer rows below (>=100 C) are extrapolations of the
temperature terms and should be read qualitatively, not as design numbers; they
are not a substitute for a boiler-water treatment program.

Run:  python examples/boiler_feedwater_check.py
"""

from cooling_tower_chem import WaterSample

# One hard raw water taken step by step through a boiler pre-treatment train.
# Calcium hardness and total alkalinity are mg/L as CaCO3; TDS is mg/L. The
# ambient rows are at the lab titration temperature (25 C); the deaerator and
# economizer rows are at operating temperature (see the validity caveat above).
STAGES = [
    dict(name="Raw hard makeup", ph=7.6, temperature_c=25,
         calcium_hardness=300, total_alkalinity=250, tds=700),
    dict(name="Na-zeolite softened", ph=7.8, temperature_c=25,
         calcium_hardness=6, total_alkalinity=250, tds=700),
    dict(name="Dealkalized + softened", ph=8.0, temperature_c=25,
         calcium_hardness=6, total_alkalinity=60, tds=450),
    dict(name="RO permeate", ph=6.9, temperature_c=25,
         calcium_hardness=3, total_alkalinity=8, tds=25),
    dict(name="Demineralized", ph=7.0, temperature_c=25,
         calcium_hardness=1, total_alkalinity=3, tds=6),
    dict(name="Deaerator feedwater", ph=8.8, temperature_c=105,
         calcium_hardness=4, total_alkalinity=40, tds=120),
    dict(name="Economizer inlet", ph=9.0, temperature_c=115,
         calcium_hardness=4, total_alkalinity=40, tds=120),
    dict(name="Softener Ca breakthrough", ph=7.8, temperature_c=105,
         calcium_hardness=45, total_alkalinity=120, tds=350),
]


def screen(sample: WaterSample) -> str:
    """Read the LSI as a residual-hardness screen for boiler feedwater.

    A positive LSI at meaningful hardness is a genuine scale risk; a positive
    LSI at trace hardness is almost always the pH/temperature terms talking, not
    scaling potential -- the exact confound that makes the LSI a poor standalone
    boiler-water tool. The screen distinguishes the two using the hardness input.
    """
    lsi = sample.lsi()
    if lsi <= -0.5:
        return "aggressive (as intended)"
    if lsi <= 0.3:
        return "marginal"
    if sample.calcium_hardness >= 20:
        return "SCALE RISK: hardness breakthrough"
    return "LSI up on pH/temp, not hardness"


def main() -> None:
    header = f"{'Treatment stage':24} {'pH':>4} {'LSI':>6} {'RSI':>6} " \
             f"{'PSI':>6} {'CCPP':>7}  Feedwater read"
    print(header)
    print("-" * len(header))
    for st in STAGES:
        fields = {k: v for k, v in st.items() if k != "name"}
        s = WaterSample(**fields)
        print(
            f"{st['name']:24} {st['ph']:>4} {s.lsi():>6.2f} {s.rsi():>6.2f} "
            f"{s.psi():>6.2f} {s.ccpp():>7.1f}  {screen(s)}"
        )
    print()
    print("Goal for boiler feedwater is a NEGATIVE LSI: hardness removed so it")
    print("cannot deposit on tubes. But note the deaerator/economizer rows: high")
    print("pH and temperature push the LSI positive at trace hardness, so cross-")
    print("check a positive reading against the hardness result before acting.")


if __name__ == "__main__":
    main()


# --- Adapting this to your water type -------------------------------------
# Replace STAGES with your own analyses. Keep the library's units: calcium
# hardness and total alkalinity in mg/L as CaCO3, temperature in C, TDS in mg/L
# (or give `conductivity_us_cm=`). Read the LSI here inverted from the cooling
# tower case: for feedwater you *want* it negative (no scaling), and a positive
# reading is the alarm. These saturation indices screen residual hardness only;
# they do not size a phosphate/polymer, amine, or oxygen-scavenger program, and
# above ~90-100 C the temperature terms are extrapolated -- treat the hot rows as
# directional.
#
# If your site runs a repeatable feedwater spec (a softener guarantee, a demin
# polish target, a condensate-return limit), it is worth encoding. The library is
# MIT on GitHub -- fork it and add your feedwater preset so the residual-hardness
# screen starts from your plant's numbers, not a generic table.
