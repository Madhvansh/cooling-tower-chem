"""Assess a single water analysis and print every index with its interpretation.

Run:  python examples/assess_water.py
"""

from cooling_tower_chem import WaterSample


def main() -> None:
    # A concentrated, alkaline cooling-tower basin sample.
    sample = WaterSample(
        ph=8.2,
        temperature_c=32,
        calcium_hardness=450,     # mg/L as CaCO3
        total_alkalinity=250,     # mg/L as CaCO3
        conductivity_us_cm=2400,  # TDS derived from this
        chloride=180,             # mg/L
        sulfate=120,              # mg/L
    )

    print(f"pH of saturation (pHs): {sample.ph_of_saturation():.2f}\n")
    for name, entry in sample.report().items():
        if name == "ph_of_saturation":
            continue
        print(f"{name:22s} {entry['value']:>7}  [{entry['tendency']}]")
        print(f"{'':22s} {entry['description']}")


if __name__ == "__main__":
    main()
