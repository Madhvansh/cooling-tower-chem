# Examples

Runnable, self-contained scripts that use the real `cooling_tower_chem` API.
Each is dependency-free (standard library plus the package itself) and prints a
plain-text table you can paste into a report.

```bash
# From a checkout of this repo:
pip install -e .
python examples/plant_water_screening.py
```

The outputs below are the actual runs of these scripts against the library.

## Cookbook

### `plant_water_screening.py`

Batch-screen a set of cooling-tower recirculating waters into one risk table:
LSI, RSI, PSI, CCPP, the Larson-Skold corrosion ratio, and a scale/corrosion
verdict per water.

```text
Water                    pH    LSI    RSI    PSI    CCPP   L-S  Verdict
-----------------------------------------------------------------------
RO makeup, 2 cycles     7.2  -1.77  10.74  11.35    -7.9  0.70  corrosive
Soft city, 3 cycles     7.6  -0.42   8.44   8.80    -3.0  0.95  balanced + Cl/SO4 attack
Balanced target         7.9   0.66   6.57   6.63    24.7  0.67  SCALING
Municipal, 4 cycles     8.0   0.97   6.07   6.13    40.6  1.55  SCALING + Cl/SO4 attack
Low-alkalinity acidic   6.8  -1.46   9.73   9.72   -19.1  8.92  corrosive + Cl/SO4 attack
Coastal high-chloride   7.8   0.49   6.83   7.04    10.2  8.79  balanced + Cl/SO4 attack
Hard well, 6 cycles     8.4   1.88   4.63   4.82   114.5  0.76  SCALING
Alkaline high-pH        9.0   2.18   4.65   5.57    88.6  0.93  SCALING + Cl/SO4 attack
Concentrated blowdown   8.6   2.25   4.09   4.37   158.5  2.40  SCALING + Cl/SO4 attack
```

### `pool_spa_check.py`

The same saturation math applied to swimming pools and spas, interpreting the
LSI with the tighter band pool operators use (target `0.0`, `+/-0.3`), and
showing how spa temperature pushes an otherwise-balanced water toward scaling.

```text
Pool / spa               pH    LSI    RSI    PSI    CCPP  Pool balance
----------------------------------------------------------------------
Balanced plaster pool   7.5  -0.08   7.65   7.75     0.3  balanced
Soft/etching plaster    7.4  -0.61   8.63   8.78    -6.9  aggressive
High-pH scaling pool    7.9   0.60   6.71   7.02    13.9  scaling
Hot spa (39 C)          7.6   0.21   7.18   7.38     3.8  balanced
Saltwater pool          7.6   0.09   7.42   7.55     0.6  balanced
Cold aggressive fill    7.2  -0.90   8.99   9.05   -11.9  aggressive
Vinyl-liner pool        7.5  -0.28   8.07   8.24    -2.9  balanced
```

### `boiler_feedwater_check.py`

A residual-hardness screen across a boiler pre-treatment train. For feedwater a
negative LSI is the goal (hardness removed so it cannot scale on tubes); the
script also shows the confound that makes the LSI a poor standalone boiler tool
-- at the hot, high-pH deaerator/economizer stages the LSI reads positive even
at trace hardness.

```text
Treatment stage            pH    LSI    RSI    PSI    CCPP  Feedwater read
--------------------------------------------------------------------------
Raw hard makeup           7.6   0.51   6.59   6.14    41.4  SCALE RISK: hardness breakthrough
Na-zeolite softened       7.8  -0.99   9.79   9.53   -11.9  aggressive (as intended)
Dealkalized + softened    8.0  -1.39  10.79  11.64    -7.7  aggressive (as intended)
RO permeate               6.9  -3.54  13.99  15.03   -10.0  aggressive (as intended)
Demineralized             7.0  -4.29  15.57  17.33    -9.9  aggressive (as intended)
Deaerator feedwater       8.8   0.47   7.87   9.78    -0.3  LSI up on pH/temp, not hardness
Economizer inlet          9.0   0.81   7.37   9.49   -16.3  LSI up on pH/temp, not hardness
Softener Ca breakthrough  7.8   0.95   5.91   6.12    19.0  SCALE RISK: hardness breakthrough
```

> The LSI/RSI/PSI indices and the CCPP were developed for ~0-90 C
> potable/cooling water; the `>=100 C` rows are extrapolations of the
> temperature terms and are directional only, not a substitute for a boiler
> water-treatment program.

## Single-sample and water-balance helpers

### `assess_water.py`

Full index report for one analysis, printing every index with its
interpretation.

```text
pH of saturation (pHs): 6.82

lsi                      1.379  [scale_forming]
                       LSI +1.38: scale-forming; calcium carbonate will tend to precipitate.
rsi                      5.443  [severely_scale_forming]
                       RSI 5.44: heavy scale formation expected.
psi                       5.59  [scale_forming]
                       PSI 5.59: scale-forming tendency.
aggressiveness_index    13.251  [balanced]
                       AI 13.25: non-aggressive water.
larson_skold_index       1.516  [severely_corrosive]
                       Larson-Skold 1.52: high corrosion rates on mild steel expected.
```

### `optimize_cycles.py`

Sweeps cycles of concentration for a fixed makeup analysis and prints makeup
demand, blowdown, and the resulting basin LSI -- the water-savings vs. scaling
trade-off. See the [Cycles of concentration](../docs/cycles.md) doc for the
underlying mass balance.

```text
cycles    makeup  blowdown  basin LSI  tendency
     2     20.50     10.05       0.31  balanced
     3     15.38      4.93       0.64  scale_forming
     4     13.67      3.22       0.88  scale_forming
     5     12.81      2.36       1.07  scale_forming
     6     12.30      1.85       1.22  scale_forming
     7     11.96      1.51       1.34  scale_forming
     8     11.72      1.26       1.45  scale_forming
```

Each cookbook script ends with an **"Adapting this to your water type"** block:
swap in your own analyses (keeping the library's units), and, if you keep a
recurring water-type preset, fork the library on GitHub and add it.
