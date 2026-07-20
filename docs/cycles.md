---
description: What cycles of concentration (COC) means for a cooling tower, the evaporation / blowdown / makeup mass balance behind it, a worked example computed with the cooling-tower-chem Python library, typical COC ranges, and how raising cycles trades water savings against scaling risk (LSI).
---

# Cycles of Concentration (COC)

**Cycles of concentration** (COC, also written CoC or "cycles") is the single
number that ties a cooling tower's water use to its scaling and corrosion risk.
It is the ratio of the concentration of a conservative dissolved species in the
recirculating water to its concentration in the makeup water:

```text
COC = (concentration in recirculating water) / (concentration in makeup water)
```

Because an evaporative tower loses **pure water vapour** but leaves the dissolved
solids behind, the recirculating water steadily concentrates. Conductivity,
chloride, or silica — species that leave essentially only with blowdown and
drift — are the usual tracers. A tower running at "5 cycles" holds five times the
makeup's dissolved-solids concentration in the basin.

## The water balance

Four streams close the balance on an evaporative tower:

| Stream | Symbol | What it is |
|---|---|---|
| Evaporation | `E` | pure water lost to the air; concentrates the solids |
| Drift (windage) | `D` | liquid droplets carried out in the air stream |
| Blowdown (bleed) | `B` | water deliberately discharged to cap the solids |
| Makeup | `M` | fresh water added to replace every loss |

Conservation of water and of dissolved solids gives the relationships the
library implements in
[`cooling_tower_chem.balance`](api.md):

```text
M = E + B + D                (makeup replaces all losses)
COC = M / (B + D)            (cycles from the water streams)
B   = E / (COC - 1) - D      (blowdown to hold a target COC)
```

The last line is the practical one: pick a target COC, and it tells you the
blowdown needed to hold it. Raising COC shrinks the `E / (COC - 1)` term, so
blowdown — and therefore makeup — falls. Evaporation itself follows a
first-principles energy balance,

```text
E = circulation_rate * cp * dT / latent_heat
```

where `dT` is the cooling range. This is the theoretical (100 % latent-heat)
maximum; real towers reject some sensible heat, so field evaporation is roughly
75–90 % of it. These are the same formulas presented under
[Indices & the science → cooling-tower water balance](indices.md#cooling-tower-water-balance);
their derivation is a straightforward water/solids mass balance, not a fitted
correlation.

## Worked example

A 1000 m³/h tower with an 8 °C cooling range, good drift eliminators
(0.02 %), run at a target of 5 cycles, on a soft makeup water:

```python
from cooling_tower_chem import CoolingTower, WaterSample

tower = CoolingTower(circulation_rate=1000, delta_t_c=8, cycles=5)  # m3/h
print(tower.water_balance())
# {'evaporation': 13.6686, 'drift': 0.2, 'blowdown': 3.2171, 'makeup': 17.0857, 'cycles': 5}
```

The numbers check by hand: `E = 1000 · 4.186 · 8 / 2450 = 13.67 m³/h`,
`B = 13.67/(5−1) − 0.2 = 3.22 m³/h`, `M = 13.67 + 3.22 + 0.2 = 17.09 m³/h`, and
`M/(B+D) = 17.09/3.42 = 5.0` cycles, as required.

Now project how that makeup concentrates in the basin, and read the Langelier
index (LSI) of the water actually circulating:

```python
makeup = WaterSample(
    ph=7.4, temperature_c=32, calcium_hardness=45,
    total_alkalinity=35, conductivity_us_cm=280,
)
basin = tower.concentrated(makeup)   # conservative species x cycles
print(round(makeup.lsi(), 2), "->", round(basin.lsi(), 2))
# -1.18 -> 0.15
```

The makeup is aggressive on its own (`LSI −1.18`); concentrating it five-fold
brings the basin to a near-balanced `LSI +0.15`.

## Typical COC ranges

There is no universal target — it depends on makeup quality, the treatment
program, and discharge limits — but these bands are representative:

| COC | Typical situation |
|---|---|
| 2–3 | poor makeup, minimal treatment, or tight scaling limits |
| 3–5 | common untreated / lightly treated baseline |
| 5–8 | well-run tower with scale/corrosion inhibitor and pH control |
| 8–15+ | high-purity (softened / RO) makeup with an engineered program |

Below ~2 cycles a tower wastes water; above the point where the basin water
turns strongly scale-forming, higher cycles trade a shrinking water saving for a
rising fouling and cleaning cost.

## Raising cycles: water saved vs. scaling risk

Every extra cycle saves less water than the one before, while the basin LSI keeps
climbing. Sweeping the worked-example tower from 2 to 8 cycles makes the
trade-off explicit:

```python
from cooling_tower_chem import CoolingTower, WaterSample, interpret_lsi

makeup = WaterSample(ph=7.4, temperature_c=32, calcium_hardness=45,
                     total_alkalinity=35, conductivity_us_cm=280)
for c in range(2, 9):
    t = CoolingTower(circulation_rate=1000, delta_t_c=8, cycles=c)
    basin = t.concentrated(makeup)
    tendency, _ = interpret_lsi(basin.lsi())
    print(f"{c:>2} {t.makeup:>8.2f} {t.blowdown:>9.2f} {basin.lsi():>7.2f}  {tendency}")
```

```text
cycles   makeup  blowdown  basin LSI  tendency
     2    27.34     13.47      -0.61  corrosive
     3    20.50      6.63      -0.28  balanced
     4    18.22      4.36      -0.04  balanced
     5    17.09      3.22       0.15  balanced
     6    16.40      2.53       0.30  balanced
     7    15.95      2.08       0.42  balanced
     8    15.62      1.75       0.53  scale_forming
```

Read the table as the operating window: at 2 cycles the water is both wasteful
(27.3 m³/h makeup) and corrosive; the LSI enters the balanced band by 3 cycles
and stays there to 7; at 8 cycles it tips scale-forming. The makeup saving also
flattens — going 2 → 3 cycles saves 6.8 m³/h, but 7 → 8 saves only 0.3 m³/h.
`water_saved_by_increasing_cycles` quantifies any such move directly:

```python
from cooling_tower_chem import water_saved_by_increasing_cycles

tower = CoolingTower(circulation_rate=1000, delta_t_c=8, cycles=5)
saved = water_saved_by_increasing_cycles(tower.evaporation, 3, 6, drift=tower.drift)
print(round(saved, 2), "m3/h", "->", round(saved * 24, 1), "m3/day")
# 4.1 m3/h -> 98.4 m3/day
```

Raising this tower from 3 to 6 cycles saves about 98 m³/day of makeup — but note
the basin LSI rises from −0.28 to +0.30 over the same move, so the water saving
is bought with a real increase in scaling tendency that the treatment program
has to absorb. The practical target is the highest COC that keeps the basin LSI
inside the balanced band for your inhibitor.

To explore the same LSI/RSI/PSI/CCPP response interactively, try the
[water-stability calculator](calculator.md); enter your concentrated basin
chemistry and watch the indices move. The full water-balance API — `CoolingTower`,
`cycles_from_flows`, `blowdown_loss`, `evaporation_loss`, and
`water_saved_by_increasing_cycles` — is documented in the
[API reference](api.md), and both worked scripts above are shipped as
[`examples/optimize_cycles.py`](https://github.com/Madhvansh/cooling-tower-chem/blob/main/examples/optimize_cycles.py).

## References

- Langelier, W. F. (1936). *The Analytical Control of Anti-Corrosion Water Treatment.* J. AWWA 28(10). (LSI used for the basin-water read above.)
- The evaporation / blowdown / makeup relationships are a first-principles water and dissolved-solids mass balance; see [Indices & the science](indices.md#cooling-tower-water-balance) for the same equations in context.

!!! note
    Cycles of concentration is a mass-balance quantity; the scaling and
    corrosion reads that go with it (LSI, RSI, PSI, CCPP) are **screening
    estimates**, not a substitute for site-specific engineering judgment or a
    jar test. The evaporation figure is the theoretical maximum — apply a
    heat-rejection factor (~0.75–0.9) for field estimates.
