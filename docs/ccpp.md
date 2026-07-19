# Calcium Carbonate Precipitation Potential (CCPP)

The [saturation indices](indices.md) (LSI, RSI, S&DSI, …) tell you the
*direction* a water leans — scaling or corrosive — but not *how much* calcium
carbonate is at stake. **CCPP** is the quantitative complement: the mass of
CaCO₃, in **mg/L as CaCO₃**, that must precipitate (positive) or dissolve
(negative) to bring the water to exact calcite saturation (`SI = 0`).

- `CCPP > 0` — supersaturated; calcite tends to deposit (scaling).
- `CCPP < 0` — undersaturated; calcite tends to dissolve (aggressive).
- `CCPP ≈ 0` — at saturation.

## Method

There is no closed form in the general case, so the equilibrium is solved
iteratively. The water is treated as a **closed system**: as CaCO₃ is deposited
or dissolved, the total (carbonate) alkalinity and the CO₂-acidity are held
conservative. Removing one mole of CaCO₃ removes one mole of calcium, one mole of
total carbonate, and **two equivalents of alkalinity** — so the CO₂-acidity
`2·CT − Alk` is unchanged. The routine searches for the amount `x` (mol/L)
exchanged such that the residual water sits exactly on `[Ca][CO₃] = Ksp`, then

```text
CCPP (mg/L as CaCO3) = x · 100086.9
```

Equilibrium constants are the Plummer & Busenberg (1982) temperature fits
(`T` in kelvin); at 25 °C they give `pK1 = 6.352`, `pK2 = 10.329`,
`pKsp(calcite) = 8.480`, `log Kw = −13.995`. They are converted to conditional
(concentration) constants with single-ion activity coefficients from the Davies
equation:

```text
log γ = −A · z² · ( √I / (1 + √I) − 0.3·I ),   A = 0.509 (25 °C)
```

## Ionic strength matters

CCPP's magnitude is dominated by the activity correction, so it is **sensitive to
the ionic strength**. Supply `ionic_strength` (mol/L) when you have a measured or
model-derived value; otherwise it is estimated from TDS as `I = 2.5×10⁻⁵ · TDS`,
which is only a rough guide. The dependency-free Davies model also carries no ion
pairing (CaHCO₃⁺, CaCO₃(aq)), so for hard, high-TDS water it tends to
over-predict precipitation relative to a full speciation model such as PHREEQC.
Treat CCPP as a semi-quantitative screen.

## Usage

```python
from cooling_tower_chem import calcium_carbonate_precipitation_potential

# Warm, hard recirculating basin water
ccpp = calcium_carbonate_precipitation_potential(
    ph=8.0, temperature_c=30,
    calcium_hardness=900,   # mg/L as CaCO3
    total_alkalinity=250,   # mg/L as CaCO3
    tds=2000,               # mg/L  (-> ionic strength 0.05 mol/L)
)
print(round(ccpp, 1))   # +88.3  -> strongly scale-forming
```

From a `WaterSample`, or the command line:

```python
from cooling_tower_chem import WaterSample

s = WaterSample(ph=8.0, temperature_c=30, calcium_hardness=900,
                total_alkalinity=250, tds=2000)
s.ccpp()                    # +88.3
s.ccpp(ionic_strength=0.30) # supply a measured ionic strength instead
```

```console
$ ctchem ccpp --ph 8.0 --temp 30 --calcium 900 --alkalinity 250 --tds 2000
CCPP = +88.28 mg/L as CaCO3
```

## Worked examples (Wojtowicz 2001)

Closed-system examples at 26.7 °C and 100 mg/L as CaCO₃ alkalinity, quoted at
TDS 5000 (ionic strength ≈ 0.24 mol/L). This library reproduces each published
figure to within ~0.1 mg/L:

| Initial pH | Calcium (mg/L as CaCO₃) | CCPP (mg/L as CaCO₃) |
|---|---|---|
| 7.0 | 4786 | 25.2 |
| 7.5 | 1514 | 14.1 |
| 8.0 |  479 |  7.1 |

## References

- Plummer, L. N. & Busenberg, E. (1982). *The solubilities of calcite, aragonite and vaterite in CO₂–H₂O solutions between 0 and 90 °C.* Geochim. Cosmochim. Acta 46(6), 1011–1040.
- Wojtowicz, J. A. (2001). *The Calcium Carbonate Precipitation Potential (CCPP) and its Use in Pool Water Balance.* J. Swimming Pool & Spa Industry 2(2), 23–29.
- Rossum, J. R. & Merrill, D. T. (1983). *An Evaluation of the Calcium Carbonate Saturation Indexes.* J. AWWA 75(1), 95–100.
- Standard Methods for the Examination of Water and Wastewater, Method 2330.
- Tang, C. et al. (2021). *Prediction of Calcium Carbonate Precipitation Potential.* Water 13(1), 42.

See the [API reference](api.md) for the full signature and validation rules.

!!! note
    CCPP is a screening estimate, not a substitute for a full speciation model
    or a jar test. Its accuracy is bounded by the closed-system assumption and
    the Davies activity model (valid to an ionic strength of about 0.5 mol/L).
