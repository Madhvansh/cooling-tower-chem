# Indices & the science

All indices use the classical water-chemistry conventions: calcium hardness and
total alkalinity in **mg/L as CaCO₃**, TDS and ions in **mg/L**, temperature in
**°C**.

## pH of saturation (pHs)

The shared building block, using the standard analytical form of Langelier's
equation:

$$
pH_s = (9.3 + A + B) - (C + D)
$$

$$
A = \frac{\log_{10}(\text{TDS}) - 1}{10}, \quad
B = -13.12 \cdot \log_{10}(T_K) + 34.55
$$

$$
C = \log_{10}(\text{Ca as CaCO}_3) - 0.4, \quad
D = \log_{10}(\text{alkalinity as CaCO}_3)
$$

where \(T_K = {}^{\circ}\!C + 273.15\).

## Saturation / stability indices

| Index | Definition | Reads as |
|---|---|---|
| **Langelier (LSI)** | `pH − pHs` | `> 0` scaling, `< 0` corrosive; a small positive value (~0 to +1) is the usual target |
| **Ryznar (RSI)** | `2·pHs − pH` | `< 6` scaling, `6–7` balanced, `> 7` corrosive |
| **Puckorius (PSI)** | `2·pHs − pH_eq`, with `pH_eq = 1.465·log₁₀(alk) + 4.54` | better fit for buffered recirculating water; uses an equilibrium pH, not the measured pH |
| **Larson-Skold** | `(Cl⁻ + SO₄²⁻) / alkalinity` (equivalents) | corrosivity toward mild steel: `< 0.8` low, `0.8–1.2` elevated, `> 1.2` high |
| **Aggressiveness (AI)** | `pH + log₁₀(Ca · alkalinity)` | AWWA screen: `≥ 12` non-aggressive, `10–12` moderate, `< 10` aggressive |
| **Stiff-Davis (S&DSI)** | `pH − pHs`, with `pHs = pCa + pAlk + K(μ, T)` | the LSI extended to high ionic strength (brines, seawater, concentrated blowdown) |

The Stiff-Davis index replaces the LSI's temperature/TDS terms with an
ionic-strength-dependent constant `K` (ASTM D4582 / USBR 2013 curve fit). Use it
for high-salinity water (TDS ≳ 10,000 mg/L); for ordinary water the LSI is the
right screen. Ionic strength is estimated as `μ ≈ 2.5×10⁻⁵ · TDS`.

These indices give a direction, not a quantity. For the actual mass of calcium
carbonate involved, the [CCPP](ccpp.md) reports the mg/L of CaCO₃ that must
precipitate or dissolve to reach calcite saturation.

Interpretation thresholds are conventional screening bands; edges vary between
sources (some Ryznar tables put the balanced/corrosive boundary at 6.8 rather
than 7.0), so treat values near a boundary as borderline.

## Cooling-tower water balance

For an evaporative tower, the four streams relate as:

- **Makeup** `M = E + B + D` (evaporation + blowdown + drift)
- **Cycles of concentration** `CoC = M / (B + D)`
- **Blowdown** to hold a target CoC: `B = E / (CoC − 1) − D`

`evaporation_loss` uses a first-principles energy balance and returns the
theoretical (100 % latent-heat) maximum; real towers evaporate ~75–90 % of that,
so apply a heat-rejection factor for field estimates.

## References

- Langelier, W. F. (1936). *The Analytical Control of Anti-Corrosion Water Treatment.* J. AWWA 28(10).
- Ryznar, J. W. (1944). *A New Index for Determining Amount of Calcium Carbonate Scale Formed by a Water.* J. AWWA 36(4).
- Puckorius, P. R. & Brooke, J. M. (1991). *A New Practical Index for Calcium Carbonate Scale Prediction in Cooling Tower Systems.* Corrosion 47(4).
- Larson, T. E. & Skold, R. V. (1958). *Laboratory Studies Relating Mineral Quality of Water to Corrosion of Steel and Cast Iron.* Corrosion 14(6).
- Stiff, H. A. & Davis, L. E. (1952). *A Method for Predicting the Tendency of Oil Field Waters to Deposit Calcium Carbonate.* Petroleum Transactions AIME 195:213. (K constant: ASTM D4582; USBR, 2013.)

!!! note
    These indices are screening guides, not a substitute for site-specific
    engineering judgment.
