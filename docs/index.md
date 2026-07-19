# cooling-tower-chem

**The water-stability and corrosion math for cooling towers, as a small, dependency-free Python library.**

Water-treatment engineers screen cooling-tower and process water with a handful
of classical indices — Langelier, Ryznar, Puckorius, Larson-Skold — plus the
evaporation / blowdown / makeup balance that sets cycles of concentration. Those
formulas are scattered across textbooks, vendor notes, and one-off web
calculators. `cooling-tower-chem` puts them in one tested, documented,
importable place.

!!! tip "Try it in your browser"
    The **[interactive water-stability calculator](calculator.md)** computes the
    Langelier (LSI), Ryznar (RSI), Puckorius (PSI), and CCPP indices live — no install
    required, and cross-checked against this library.

```python
from cooling_tower_chem import WaterSample

sample = WaterSample(
    ph=8.2, temperature_c=32,
    calcium_hardness=450, total_alkalinity=250,  # mg/L as CaCO3
    conductivity_us_cm=2400, chloride=180, sulfate=120,
)
print(sample.lsi())                       # 1.38  -> scale-forming
print(sample.report()["lsi"]["description"])
# "LSI +1.38: scale-forming; calcium carbonate will tend to precipitate."
```

## Why it exists

The Python ecosystem had no small, focused, well-tested home for these indices.
The alternatives are heavyweight geochemical engines (`phreeqpython`, which needs
PHREEQC and gives a generic calcite saturation index) or process suites
(`watertap`, for RO/desalination) — neither computes the named utility indices,
and neither does cooling-tower water balance. This library was extracted from the
physics engine of [TGF](https://github.com/Madhvansh/TGF), a cooling-tower
dosing-control project, and hardened into a standalone package.

## Highlights

- **Dependency-free.** Pure standard-library Python, fully type-hinted (`py.typed`).
- **Correct and cited.** Formulas reference the original papers; 111 tests cover
  formula correctness, input validation, and monotonicity.
- **Batteries included.** A `WaterSample` report, a `CoolingTower` water-balance
  object, unit conversions, and a `ctchem` CLI.
- **Tested on CPython 3.9–3.13**, MIT licensed.

<div class="grid cards" markdown>
- [:material-rocket-launch: **Quickstart**](quickstart.md)
- [:material-calculator: **Water stability calculator**](calculator.md)
- [:material-flask: **Indices & the science**](indices.md)
- [:material-console: **Command line**](cli.md)
- [:material-api: **API reference**](api.md)
</div>
