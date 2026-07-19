# Quickstart

## Install

```bash
# From source (until the first PyPI release lands):
pip install git+https://github.com/Madhvansh/cooling-tower-chem

# Once released on PyPI:
pip install cooling-tower-chem
```

No third-party dependencies. Pure standard-library Python, tested on CPython 3.9–3.13.

## One sample, every index

```python
from cooling_tower_chem import WaterSample

sample = WaterSample(
    ph=8.2,
    temperature_c=32,
    calcium_hardness=450,     # mg/L as CaCO3
    total_alkalinity=250,     # mg/L as CaCO3
    conductivity_us_cm=2400,  # TDS derived from this if not given
    chloride=180,             # mg/L (for the Larson-Skold index)
    sulfate=120,              # mg/L
)

print(sample.lsi())   # 1.38  -> scale-forming
print(sample.rsi())   # 5.44  -> heavy scale
report = sample.report()  # JSON-serializable dict of every index + interpretation
```

## Prefer plain functions?

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

## Cooling-tower water balance

The `CoolingTower` object ties the balance together and projects how makeup water
concentrates in the basin:

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

## Units & conventions

- Calcium hardness and total alkalinity: **mg/L as CaCO₃**
- TDS and ions (chloride, sulfate): **mg/L**
- Temperature: **°C** (use `celsius_to_fahrenheit` / `fahrenheit_to_celsius` to convert)
- Flows: any consistent volumetric unit (m³/h, gpm, …) — results carry the same unit

Inputs that would break a logarithm (non-positive hardness, alkalinity, or TDS)
raise a clear `ValueError` rather than returning a silent fallback.

See the runnable scripts in
[`examples/`](https://github.com/Madhvansh/cooling-tower-chem/tree/main/examples).
