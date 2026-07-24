# cooling-tower-chem

[![CI](https://github.com/Madhvansh/cooling-tower-chem/actions/workflows/ci.yml/badge.svg)](https://github.com/Madhvansh/cooling-tower-chem/actions/workflows/ci.yml)
[![Docs](https://img.shields.io/badge/docs-mkdocs--material-blue.svg)](https://madhvansh.github.io/cooling-tower-chem/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![OpenSSF Best Practices](https://www.bestpractices.dev/projects/13776/badge)](https://www.bestpractices.dev/projects/13776)

[![PyPI](https://img.shields.io/pypi/v/cooling-tower-chem.svg)](https://pypi.org/project/cooling-tower-chem/)
[![Python versions](https://img.shields.io/pypi/pyversions/cooling-tower-chem.svg)](https://pypi.org/project/cooling-tower-chem/)

**The water-stability and corrosion math for cooling towers, as a small, dependency-free Python library.**

Water-treatment engineers screen cooling-tower and process water with a handful
of classical indices — Langelier, Ryznar, Puckorius, Larson-Skold — plus the
evaporation / blowdown / makeup balance that sets cycles of concentration.
Those formulas are scattered across textbooks and spreadsheets. `cooling-tower-chem`
puts them in one tested, documented, importable place.

> **Try it in your browser:** the [interactive water-stability calculator](https://madhvansh.github.io/cooling-tower-chem/calculator/)
> computes LSI, RSI, PSI, and CCPP live — no install required, and cross-checked against this library.

```bash
# From PyPI:
pip install cooling-tower-chem

# Or install the latest development version from source:
pip install git+https://github.com/Madhvansh/cooling-tower-chem
```

No third-party dependencies. Pure standard-library Python, fully type-hinted, tested on CPython 3.9–3.13.

## Quick start

```python
from cooling_tower_chem import WaterSample

# One analysis in, every index out.
sample = WaterSample(
    ph=8.2,
    temperature_c=32,
    calcium_hardness=450,     # mg/L as CaCO3
    total_alkalinity=250,     # mg/L as CaCO3
    conductivity_us_cm=2400,  # TDS is derived from this if not given
    chloride=180,             # mg/L (for the Larson-Skold index)
    sulfate=120,              # mg/L
)

print(sample.lsi())   # 1.38  -> scale-forming
print(sample.rsi())   # 5.44  -> heavy scale
report = sample.report()
print(report["lsi"]["description"])
# "LSI +1.38: scale-forming; calcium carbonate will tend to precipitate."
```

Prefer plain functions? Every index is available directly:

```python
from cooling_tower_chem import (
    langelier_saturation_index,
    ryznar_stability_index,
    puckorius_scaling_index,
    larson_skold_index,
)

lsi = langelier_saturation_index(
    ph=7.5, temperature_c=25, tds=400,
    calcium_hardness=240, total_alkalinity=180,
)   # -> +0.19
```

### From the command line

Installing the package also gives you a `ctchem` command:

```console
$ ctchem report --ph 8.2 --temp 32 --calcium 450 --alkalinity 250 \
      --conductivity 2400 --chloride 180 --sulfate 120
pH of saturation (pHs): 6.821
LSI: 1.379  [scale_forming]
    LSI +1.38: scale-forming; calcium carbonate will tend to precipitate.
RSI: 5.443  [severely_scale_forming]
    RSI 5.44: heavy scale formation expected.
...

$ ctchem lsi --ph 7.5 --temp 25 --tds 400 --calcium 240 --alkalinity 180
LSI = +0.189
```

Add `--json` to any command for machine-readable output.

## What's included

### Stability & corrosion indices

| Function | Index | Reads as |
|---|---|---|
| `langelier_saturation_index` | LSI = pH − pHs | `> 0` scaling, `< 0` corrosive |
| `ryznar_stability_index` | RSI = 2·pHs − pH | `< 6` scaling, `> 7` corrosive |
| `puckorius_scaling_index` | PSI = 2·pHs − pH_eq | better fit for buffered recirculating water |
| `larson_skold_index` | (Cl⁻+SO₄²⁻)/alkalinity | corrosivity toward mild steel |
| `aggressiveness_index` | AI = pH + log₁₀(Ca·Alk) | AWWA aggressiveness screen |
| `stiff_davis_index` | S&DSI = pH − pHs (ionic-strength corrected) | LSI for high-salinity / brine water |
| `ph_of_saturation` | pHs | the shared building block |

### Precipitation potential (CCPP)

Beyond the *direction* the indices give, `calcium_carbonate_precipitation_potential`
reports the **quantity**: the signed mass of CaCO₃ (mg/L as CaCO₃) that must
precipitate (`+`) or dissolve (`−`) to reach calcite saturation, solved for a
closed system with the Plummer & Busenberg (1982) equilibrium constants and a
Davies activity model. It reproduces Wojtowicz's (2001) worked examples, and is
also available on `WaterSample.ccpp()` and the `ctchem ccpp` CLI.

### Cooling-tower water balance

`cycles_of_concentration`, `evaporation_loss` (energy balance), `drift_loss`,
`blowdown_loss`, `makeup_water`, `cycles_from_flows`,
`water_saved_by_increasing_cycles`, and TDS ↔ conductivity conversion.

The `CoolingTower` object ties the balance together and can project how makeup
water concentrates in the basin:

```python
from cooling_tower_chem import CoolingTower, WaterSample

tower = CoolingTower(circulation_rate=1000, delta_t_c=6, cycles=5)  # m3/h
print(tower.water_balance())
# {'evaporation': 10.2514, 'drift': 0.2, 'blowdown': 2.3629, 'makeup': 12.8143, 'cycles': 5}

makeup = WaterSample(ph=7.8, temperature_c=32, calcium_hardness=90,
                     total_alkalinity=60, conductivity_us_cm=400)
basin = tower.concentrated(makeup)   # conservative species x cycles
print(round(makeup.lsi(), 2), "->", round(basin.lsi(), 2))  # -0.26 -> 1.07
```

### Interpretation

`interpret_lsi`, `interpret_rsi`, `interpret_psi`, `interpret_larson_skold`,
`interpret_aggressiveness` each return a coarse `Tendency` and a one-line
explanation, so you can turn a number into an actionable message.

### Unit conversions

Water data arrives in mixed units. `as_caco3` / `caco3_to_ion` (plus named
`calcium_as_caco3`, `magnesium_as_caco3`, `bicarbonate_as_caco3`) convert between
mg/L-of-ion and mg/L-as-CaCO3; `grains_per_gallon_to_mg_l` and
`celsius_to_fahrenheit` (and inverses) cover the common US/metric gaps.

If your analysis is already in customary US units — temperature in °F and
hardness/alkalinity in grains per gallon (as CaCO₃) — skip the manual
conversions and use `WaterSample.from_us_units`:

```python
from cooling_tower_chem import WaterSample

# 90 °F, 26.3 gpg calcium hardness, 14.6 gpg alkalinity (both as CaCO3).
sample = WaterSample.from_us_units(
    ph=8.2,
    temperature_f=90,
    calcium_hardness_gpg=26.3,
    total_alkalinity_gpg=14.6,
    conductivity_us_cm=2400,   # TDS/conductivity keep their usual units
)
print(round(sample.lsi(), 2))  # same result as the SI constructor
```

It converts °F and grains/gallon internally (via `fahrenheit_to_celsius` and
`grains_per_gallon_to_mg_l`) and returns an ordinary `WaterSample`, so every
index method behaves exactly as if you had built it in SI units.

### Runnable examples

See the [Examples](#examples) section below, or browse
[`examples/`](examples/) directly.

## Examples

Runnable, dependency-free cookbook scripts in [`examples/`](examples/) — each
prints a plain-text table (real output in the
[examples README](examples/README.md)):

| Script | What it screens |
|---|---|
| [`plant_water_screening.py`](examples/plant_water_screening.py) | batch LSI/RSI/PSI/CCPP + Larson-Skold risk table for a set of cooling-tower waters |
| [`pool_spa_check.py`](examples/pool_spa_check.py) | the same indices at pool/spa chemistry, read with pool-practice LSI bands |
| [`boiler_feedwater_check.py`](examples/boiler_feedwater_check.py) | residual-hardness screen across a boiler pre-treatment train |
| [`assess_water.py`](examples/assess_water.py) | full index report for a single analysis |
| [`optimize_cycles.py`](examples/optimize_cycles.py) | cycles-of-concentration sweep: makeup water vs. basin LSI |

For the theory behind the cycles sweep, see the
[Cycles of concentration](https://madhvansh.github.io/cooling-tower-chem/cycles/)
doc — the COC mass balance and the water-savings vs. scaling-risk trade-off,
worked through with the library.

## Units & conventions

- Calcium hardness and total alkalinity: **mg/L as CaCO₃**
- TDS and ions (chloride, sulfate): **mg/L**
- Temperature: **°C**
- Flows: any consistent volumetric unit (m³/h, gpm, …) — results carry the same unit

Inputs that would break a logarithm (non-positive hardness, alkalinity, or TDS)
raise a clear `ValueError` rather than returning a silent fallback.

## Why this exists

These indices are the daily bread of industrial water treatment, but the Python
ecosystem had no small, focused, well-tested home for them. `cooling-tower-chem`
was extracted from the physics engine of
[TGF](https://github.com/Madhvansh/TGF), a cooling-tower dosing-control project,
and hardened into a standalone library so any process-engineering or
water-treatment codebase can depend on it.

## References

- Langelier, W. F. (1936). *The Analytical Control of Anti-Corrosion Water Treatment.* J. AWWA 28(10).
- Ryznar, J. W. (1944). *A New Index for Determining Amount of Calcium Carbonate Scale Formed by a Water.* J. AWWA 36(4).
- Puckorius, P. R. & Brooke, J. M. (1991). *A New Practical Index for Calcium Carbonate Scale Prediction in Cooling Tower Systems.* Corrosion 47(4).
- Larson, T. E. & Skold, R. V. (1958). *Laboratory Studies Relating Mineral Quality of Water to Corrosion of Steel and Cast Iron.* Corrosion 14(6).

The interpretation thresholds are the conventional screening bands from these
sources; they are guides, not a substitute for site-specific engineering judgment.

## Contributing

Issues and pull requests are welcome — see [CONTRIBUTING.md](CONTRIBUTING.md).
Good first contributions: additional well-referenced indices, further
unit-conversion helpers, and more worked examples from the literature to expand
the test suite.

## License

MIT — see [LICENSE](LICENSE).
