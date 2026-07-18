"""Show the scaling/water-use trade-off of running a tower at higher cycles.

As cycles of concentration rise, makeup water falls (good) but the basin water
concentrates and becomes more scale-forming (bad). This sweeps cycles 2-8 for a
fixed makeup analysis and prints makeup demand and the resulting LSI.

Run:  python examples/optimize_cycles.py
"""

from cooling_tower_chem import CoolingTower, WaterSample, interpret_lsi

MAKEUP = WaterSample(
    ph=7.8, temperature_c=32, calcium_hardness=90,
    total_alkalinity=60, conductivity_us_cm=400,
)
CIRCULATION_M3H = 1000.0
COOLING_RANGE_C = 6.0


def main() -> None:
    print(f"{'cycles':>6} {'makeup':>9} {'blowdown':>9} {'basin LSI':>10}  tendency")
    for cycles in range(2, 9):
        tower = CoolingTower(
            circulation_rate=CIRCULATION_M3H, delta_t_c=COOLING_RANGE_C, cycles=cycles
        )
        basin = tower.concentrated(MAKEUP)
        lsi = basin.lsi()
        tendency, _ = interpret_lsi(lsi)
        print(
            f"{cycles:>6} {tower.makeup:>9.2f} {tower.blowdown:>9.2f} "
            f"{lsi:>10.2f}  {tendency}"
        )
    print(
        "\nHigher cycles save makeup water but push the basin toward scaling; "
        "the sweet spot keeps LSI in the balanced band while minimizing makeup."
    )


if __name__ == "__main__":
    main()
