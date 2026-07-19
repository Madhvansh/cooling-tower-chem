---
description: Free interactive Langelier Saturation Index (LSI) calculator with Ryznar (RSI), Puckorius (PSI), and Calcium Carbonate Precipitation Potential (CCPP). Compute cooling-tower water stability in your browser, cross-checked against the cooling-tower-chem Python library.
---

# Water Stability Calculator (LSI, RSI, PSI, CCPP)

This is an interactive **Langelier Saturation Index calculator** that also reports the
**Ryznar Stability Index (RSI)**, the **Puckorius (Practical) Scaling Index (PSI)**, and the
**Calcium Carbonate Precipitation Potential (CCPP)** for cooling-tower and process water.
Enter a pH, temperature, calcium hardness, total alkalinity, and TDS, and it tells you
whether the water tends to **scale** or **corrode** — and, via CCPP, roughly *how much*
calcium carbonate is at stake.

The math runs entirely in your browser (nothing is uploaded). Every formula is a faithful
port of the [`cooling-tower-chem`](index.md) Python library, using the same constants and
the same interpretation bands, and the numbers are
[cross-checked against the library](#cross-checked-against-the-library) on this page. For the
full-analysis Python API, the `ctchem` command line, and the cooling-tower
[cycles of concentration](indices.md#cooling-tower-water-balance) / blowdown balance, see the
rest of the docs.

<style>
#ctc-calc {
  --ctc-corr-2:#1565c0; --ctc-corr-1:#1e88e5; --ctc-bal:#2e7d32;
  --ctc-scale-1:#ef6c00; --ctc-scale-2:#c62828;
  border:1px solid var(--md-default-fg-color--lightest);
  border-radius:.4rem; padding:1rem 1.1rem 1.15rem;
  margin:1.2rem 0; background:var(--md-default-bg-color);
}
#ctc-calc .ctc-grid { display:grid; grid-template-columns:1fr 1fr; gap:1.1rem 1.4rem; }
@media (max-width:44rem){ #ctc-calc .ctc-grid { grid-template-columns:1fr; } }
#ctc-calc h3 { margin:.1rem 0 .7rem; font-size:.82rem; text-transform:uppercase;
  letter-spacing:.06em; color:var(--md-default-fg-color--light); }
#ctc-calc .ctc-field { margin-bottom:.75rem; }
#ctc-calc label { display:block; font-size:.74rem; font-weight:600;
  color:var(--md-default-fg-color--light); margin-bottom:.2rem; }
#ctc-calc .ctc-unit { font-weight:400; opacity:.75; }
#ctc-calc input[type=number], #ctc-calc select {
  width:100%; box-sizing:border-box; padding:.4rem .5rem; font-size:.9rem;
  color:var(--md-default-fg-color); background:var(--md-code-bg-color);
  border:1px solid var(--md-default-fg-color--lighter); border-radius:.25rem;
  -moz-appearance:textfield;
}
#ctc-calc .ctc-temp-row { display:flex; gap:.5rem; }
#ctc-calc .ctc-temp-row input { flex:1 1 auto; }
#ctc-calc .ctc-temp-row select { flex:0 0 5.2rem; width:auto; }
#ctc-calc input:focus, #ctc-calc select:focus {
  outline:none; border-color:var(--md-accent-fg-color, #009485); }
#ctc-calc .ctc-msg { color:var(--ctc-scale-2); font-size:.8rem;
  min-height:1.1rem; margin-top:.1rem; }
#ctc-calc .ctc-card { border:1px solid var(--md-default-fg-color--lightest);
  border-left-width:5px; border-radius:.3rem; padding:.55rem .7rem;
  margin-bottom:.6rem; background:var(--md-code-bg-color); }
#ctc-calc .ctc-card:last-child { margin-bottom:0; }
#ctc-calc .ctc-card-top { display:flex; align-items:baseline;
  justify-content:space-between; gap:.5rem; flex-wrap:wrap; }
#ctc-calc .ctc-name { font-weight:700; font-size:.9rem; }
#ctc-calc .ctc-name small { font-weight:400; opacity:.7; }
#ctc-calc .ctc-val { font-variant-numeric:tabular-nums; font-weight:700;
  font-size:1.15rem; letter-spacing:-.01em; }
#ctc-calc .ctc-badge { display:inline-block; font-size:.66rem; font-weight:700;
  text-transform:uppercase; letter-spacing:.04em; color:#fff;
  padding:.08rem .4rem; border-radius:1rem; vertical-align:middle; }
#ctc-calc .ctc-desc { font-size:.78rem; color:var(--md-default-fg-color--light);
  margin-top:.25rem; line-height:1.35; }
#ctc-calc .t-severely_corrosive { border-left-color:var(--ctc-corr-2); }
#ctc-calc .t-severely_corrosive .ctc-badge { background:var(--ctc-corr-2); }
#ctc-calc .t-corrosive { border-left-color:var(--ctc-corr-1); }
#ctc-calc .t-corrosive .ctc-badge { background:var(--ctc-corr-1); }
#ctc-calc .t-balanced { border-left-color:var(--ctc-bal); }
#ctc-calc .t-balanced .ctc-badge { background:var(--ctc-bal); }
#ctc-calc .t-scale_forming { border-left-color:var(--ctc-scale-1); }
#ctc-calc .t-scale_forming .ctc-badge { background:var(--ctc-scale-1); }
#ctc-calc .t-severely_scale_forming { border-left-color:var(--ctc-scale-2); }
#ctc-calc .t-severely_scale_forming .ctc-badge { background:var(--ctc-scale-2); }
#ctc-calc .ctc-selftest { margin-top:.9rem; font-size:.75rem;
  color:var(--md-default-fg-color--light); }
#ctc-calc .ctc-selftest b { color:var(--ctc-bal); }
#ctc-calc .ctc-selftest.ctc-fail b { color:var(--ctc-scale-2); }
</style>

<div id="ctc-calc">
  <div class="ctc-grid">
    <div class="ctc-inputs">
      <h3>Water analysis</h3>
      <div class="ctc-field">
        <label for="ctc-ph">pH</label>
        <input type="number" id="ctc-ph" value="8.2" step="0.1" inputmode="decimal">
      </div>
      <div class="ctc-field">
        <label for="ctc-temp">Temperature</label>
        <div class="ctc-temp-row">
          <input type="number" id="ctc-temp" value="32" step="1" inputmode="decimal">
          <select id="ctc-tunit" aria-label="Temperature unit">
            <option value="C" selected>&deg;C</option>
            <option value="F">&deg;F</option>
          </select>
        </div>
      </div>
      <div class="ctc-field">
        <label for="ctc-ca">Calcium hardness <span class="ctc-unit">mg/L as CaCO&#8323;</span></label>
        <input type="number" id="ctc-ca" value="450" step="10" min="0" inputmode="decimal">
      </div>
      <div class="ctc-field">
        <label for="ctc-alk">Total alkalinity <span class="ctc-unit">mg/L as CaCO&#8323;</span></label>
        <input type="number" id="ctc-alk" value="250" step="10" min="0" inputmode="decimal">
      </div>
      <div class="ctc-field">
        <label for="ctc-tds">Total dissolved solids <span class="ctc-unit">mg/L</span></label>
        <input type="number" id="ctc-tds" value="1560" step="50" min="0" inputmode="decimal">
      </div>
      <div class="ctc-msg" id="ctc-msg"></div>
    </div>
    <div class="ctc-outputs">
      <h3>Results</h3>
      <div id="ctc-results"></div>
    </div>
  </div>
  <div class="ctc-selftest" id="ctc-selftest">Running self-test&hellip;</div>
</div>

<script>
(function () {
  "use strict";

  // ---- Constants: identical to src/cooling_tower_chem/indices.py & advanced.py ----
  var CACO3_MOLAR_MASS_MG = 100086.9; // mg per mol
  var CACO3_EQUIV_MG = 50043.45;      // mg per equivalent
  var A_DAVIES_25C = 0.509;
  var log10 = Math.log10, sqrt = Math.sqrt, pow = Math.pow;

  // ---- indices.py ----
  function phOfSaturation(tC, tds, ca, alk) {
    var a = (log10(tds) - 1.0) / 10.0;
    var b = -13.12 * log10(tC + 273.15) + 34.55;
    var c = log10(ca) - 0.4;
    var d = log10(alk);
    return (9.3 + a + b) - (c + d);
  }
  function lsiOf(ph, tC, tds, ca, alk) { return ph - phOfSaturation(tC, tds, ca, alk); }
  function rsiOf(ph, tC, tds, ca, alk) { return 2.0 * phOfSaturation(tC, tds, ca, alk) - ph; }
  function psiOf(tC, tds, ca, alk) {
    var phs = phOfSaturation(tC, tds, ca, alk);
    var phEq = 1.465 * log10(alk) + 4.54;
    return 2.0 * phs - phEq;
  }

  // ---- balance.py ----
  function ionicStrengthFromTds(tds) { return tds * 2.5e-5; }

  // ---- convert.py ----
  function fahrenheitToCelsius(f) { return (f - 32.0) * 5.0 / 9.0; }

  // ---- advanced.py: CCPP (Plummer & Busenberg 1982 + Davies; closed-system bisection) ----
  function plummerBusenberg(tC) {
    var t = tC + 273.15, t2 = t * t, lt = log10(t);
    var lk1 = -356.3094 - 0.06091964 * t + 21834.37 / t + 126.8339 * lt - 1684915.0 / t2;
    var lk2 = -107.8871 - 0.032528 * t + 5151.79 / t + 38.92561 * lt - 563713.9 / t2;
    var lksp = -171.9065 - 0.077993 * t + 2839.319 / t + 71.595 * lt;
    var lkw = -4470.99 / t + 6.0875 - 0.01706 * t;
    return [pow(10, lk1), pow(10, lk2), pow(10, lksp), pow(10, lkw)];
  }
  function daviesGamma(mu) {
    var si = sqrt(mu), br = si / (1.0 + si) - 0.3 * mu;
    return [pow(10, -A_DAVIES_25C * 1.0 * br), pow(10, -A_DAVIES_25C * 4.0 * br)];
  }
  function ccppOf(ph, tC, ca, alk, tds, ionicStrength) {
    var mu = (ionicStrength == null) ? ionicStrengthFromTds(tds) : ionicStrength;
    var pb = plummerBusenberg(tC), k1 = pb[0], k2 = pb[1], ksp = pb[2], kw = pb[3];
    var g = daviesGamma(mu), g1 = g[0], g2 = g[1];
    var ck1 = k1 / g1, ck2 = k2 * g1 / g2, cksp = ksp / (g2 * g2), ckw = kw / g1;

    function a12(h) {
      var denom = h * h + h * ck1 + ck1 * ck2;
      return [h * ck1 / denom, ck1 * ck2 / denom];
    }
    function alkalinity(h, ct) {
      var a = a12(h);
      return ct * (a[0] + 2.0 * a[1]) + ckw / h - h / g1;
    }
    function equilibriumH(ct, alkTarget) {
      var low = 1e-14, high = 1.0, mid;
      for (var i = 0; i < 200; i++) {
        mid = sqrt(low * high);
        if (alkalinity(mid, ct) > alkTarget) low = mid; else high = mid;
        if (high - low < 1e-18) break;
      }
      return sqrt(low * high);
    }
    var hI = pow(10, -ph), aI = a12(hI);
    var alkTotal = alk / CACO3_EQUIV_MG, caTotal = ca / CACO3_MOLAR_MASS_MG;
    var ctInitial = (alkTotal - ckw / hI + hI / g1) / (aI[0] + 2.0 * aI[1]);

    function gap(x) {
      var ctEq = ctInitial - x;
      var hEq = equilibriumH(ctEq, alkTotal - 2.0 * x);
      var a2 = a12(hEq)[1];
      return (caTotal - x) * ctEq * a2 - cksp;
    }
    var low, high, mid;
    if (gap(0.0) >= 0.0) {
      low = 0.0; high = Math.min(caTotal, ctInitial) * (1.0 - 1e-12);
    } else {
      low = -1e-9; high = 0.0; var ok = false;
      for (var j = 0; j < 200; j++) {
        if (gap(low) > 0.0) { ok = true; break; }
        low *= 2.0;
      }
      if (!ok) throw new Error("could not bracket the calcite equilibrium state");
    }
    for (var k = 0; k < 200; k++) {
      mid = 0.5 * (low + high);
      if (gap(mid) > 0.0) low = mid; else high = mid;
      if (high - low < 1e-18) break;
    }
    return 0.5 * (low + high) * CACO3_MOLAR_MASS_MG;
  }

  // ---- interpret.py (bands + wording ported verbatim) ----
  function fmtPlus(x, dp) { var r = x.toFixed(dp); return (r.charAt(0) === "-" ? "" : "+") + r; }

  function interpretLsi(v) {
    var s = fmtPlus(v, 2);
    if (v <= -2.0) return ["severely_corrosive", "LSI " + s + ": severely undersaturated and aggressive; expect rapid dissolution of protective carbonate films."];
    if (v < -0.5) return ["corrosive", "LSI " + s + ": corrosive tendency; water will tend to dissolve calcium carbonate."];
    if (v <= 0.5) return ["balanced", "LSI " + s + ": near saturation (balanced to slightly scale-forming) - the usual target band."];
    if (v <= 1.5) return ["scale_forming", "LSI " + s + ": scale-forming; calcium carbonate will tend to precipitate."];
    return ["severely_scale_forming", "LSI " + s + ": heavily supersaturated; expect rapid scaling without inhibitor or blowdown control."];
  }
  function interpretRsi(v) {
    var s = v.toFixed(2);
    if (v < 5.5) return ["severely_scale_forming", "RSI " + s + ": heavy scale formation expected."];
    if (v < 6.2) return ["scale_forming", "RSI " + s + ": scale-forming tendency."];
    if (v <= 7.0) return ["balanced", "RSI " + s + ": approximately balanced - the target band."];
    if (v < 8.5) return ["corrosive", "RSI " + s + ": corrosive tendency."];
    return ["severely_corrosive", "RSI " + s + ": severely corrosive water."];
  }
  function interpretPsi(v) {
    var r = interpretRsi(v);
    return [r[0], r[1].replace("RSI", "PSI")];
  }
  function ccppNote(v) {
    if (v > 0.05) return ["scale_forming", "CCPP " + fmtPlus(v, 1) + " mg/L as CaCO₃: supersaturated; calcite tends to deposit (scaling)."];
    if (v < -0.05) return ["corrosive", "CCPP " + fmtPlus(v, 1) + " mg/L as CaCO₃: undersaturated; calcite tends to dissolve (aggressive)."];
    return ["balanced", "CCPP " + fmtPlus(v, 1) + " mg/L as CaCO₃: at calcite saturation."];
  }
  var TENDENCY_LABEL = {
    severely_corrosive: "Severely corrosive", corrosive: "Corrosive", balanced: "Balanced",
    scale_forming: "Scale-forming", severely_scale_forming: "Severely scale-forming"
  };

  // ---- UI wiring ----
  function $(id) { return document.getElementById(id); }
  var els = {
    ph: $("ctc-ph"), temp: $("ctc-temp"), tunit: $("ctc-tunit"), ca: $("ctc-ca"),
    alk: $("ctc-alk"), tds: $("ctc-tds"), msg: $("ctc-msg"), results: $("ctc-results")
  };
  var lastUnit = "C";

  function card(name, sub, valueText, tendency, desc) {
    return '<div class="ctc-card t-' + tendency + '">' +
      '<div class="ctc-card-top">' +
      '<span class="ctc-name">' + name + ' <small>' + sub + '</small></span>' +
      '<span><span class="ctc-val">' + valueText + '</span> ' +
      '<span class="ctc-badge">' + TENDENCY_LABEL[tendency] + '</span></span>' +
      '</div><div class="ctc-desc">' + desc + '</div></div>';
  }

  function compute() {
    var ph = parseFloat(els.ph.value);
    var tRaw = parseFloat(els.temp.value);
    var ca = parseFloat(els.ca.value);
    var alk = parseFloat(els.alk.value);
    var tds = parseFloat(els.tds.value);
    var tC = (els.tunit.value === "F") ? fahrenheitToCelsius(tRaw) : tRaw;

    var bad = [];
    if (!isFinite(ph)) bad.push("pH");
    if (!isFinite(tRaw)) bad.push("temperature");
    if (!(ca > 0)) bad.push("calcium hardness");
    if (!(alk > 0)) bad.push("alkalinity");
    if (!(tds > 0)) bad.push("TDS");
    if (isFinite(tC) && tC <= -273.15) { bad.push("temperature"); }

    if (bad.length) {
      els.msg.textContent = "Enter positive values (a logarithm is taken) for: " + bad.join(", ") + ".";
      els.results.innerHTML = "";
      return;
    }
    els.msg.textContent = "";

    var lsi = lsiOf(ph, tC, tds, ca, alk);
    var rsi = rsiOf(ph, tC, tds, ca, alk);
    var psi = psiOf(tC, tds, ca, alk);
    var html = "";
    var iL = interpretLsi(lsi);
    html += card("LSI", "Langelier", fmtPlus(lsi, 2), iL[0], iL[1]);
    var iR = interpretRsi(rsi);
    html += card("RSI", "Ryznar", rsi.toFixed(2), iR[0], iR[1]);
    var iP = interpretPsi(psi);
    html += card("PSI", "Puckorius", psi.toFixed(2), iP[0], iP[1]);
    try {
      var ccpp = ccppOf(ph, tC, ca, alk, tds, null);
      var iC = ccppNote(ccpp);
      html += card("CCPP", "mg/L as CaCO₃", fmtPlus(ccpp, 1), iC[0], iC[1]);
    } catch (e) {
      html += card("CCPP", "mg/L as CaCO₃", "&mdash;", "balanced",
        "CCPP could not be bracketed for these inputs. It is available in the Python library.");
    }
    els.results.innerHTML = html;
  }

  // Convert the shown temperature when the unit toggles, so it stays physical.
  els.tunit.addEventListener("change", function () {
    var v = parseFloat(els.temp.value);
    if (isFinite(v)) {
      if (lastUnit === "C" && els.tunit.value === "F") {
        els.temp.value = Math.round((v * 9.0 / 5.0 + 32.0) * 10) / 10;
      } else if (lastUnit === "F" && els.tunit.value === "C") {
        els.temp.value = Math.round(fahrenheitToCelsius(v) * 10) / 10;
      }
    }
    lastUnit = els.tunit.value;
    compute();
  });
  ["ph", "temp", "ca", "alk", "tds"].forEach(function (k) {
    els[k].addEventListener("input", compute);
  });

  // ---- Self-test: assert the in-browser port matches the Python library ----
  // Expected values produced by .venv python from cooling_tower_chem (see the
  // "Cross-checked against the library" table below).
  var REFERENCE_CASES = [
    { name: "A", in: { ph: 8.2, t: 32, tds: 1560, ca: 450, alk: 250 }, exp: { lsi: 1.378656, rsi: 5.442689, psi: 5.589707, ccpp: 66.590781 } },
    { name: "B", in: { ph: 7.5, t: 25, tds: 400, ca: 240, alk: 180 }, exp: { lsi: 0.189863, rsi: 7.120275, psi: 6.776301, ccpp: 17.498128 } },
    { name: "C", in: { ph: 8.0, t: 30, tds: 2000, ca: 900, alk: 250 }, exp: { lsi: 1.431427, rsi: 5.137146, psi: 5.084164, ccpp: 88.276897 } },
    { name: "D", in: { ph: 7.0, t: 20, tds: 150, ca: 50, alk: 40 }, exp: { lsi: -1.698360, rsi: 10.396719, psi: 10.509701, ccpp: -17.328811 } }
  ];
  function selfTest() {
    var passed = 0, maxErr = 0;
    for (var i = 0; i < REFERENCE_CASES.length; i++) {
      var c = REFERENCE_CASES[i], p = c.in, e = c.exp;
      var got = {
        lsi: lsiOf(p.ph, p.t, p.tds, p.ca, p.alk),
        rsi: rsiOf(p.ph, p.t, p.tds, p.ca, p.alk),
        psi: psiOf(p.t, p.tds, p.ca, p.alk),
        ccpp: ccppOf(p.ph, p.t, p.ca, p.alk, p.tds, null)
      };
      var ok = true;
      for (var key in e) {
        var d = Math.abs(got[key] - e[key]);
        if (d > maxErr) maxErr = d;
        if (d > 0.01) ok = false;
        if (typeof console !== "undefined" && console.assert) {
          console.assert(d <= 0.01, "ctchem self-test " + c.name + "." + key +
            " diff " + d.toExponential(2));
        }
      }
      if (ok) passed++;
    }
    var el = $("ctc-selftest");
    var allOk = (passed === REFERENCE_CASES.length);
    el.className = "ctc-selftest" + (allOk ? "" : " ctc-fail");
    el.innerHTML = (allOk ? "&#10003; " : "&#9888; ") +
      "Cross-checked against the Python library: <b>" + passed + "/" +
      REFERENCE_CASES.length + "</b> reference cases match (max deviation " +
      maxErr.toExponential(1) + ", tolerance 0.01).";
    return allOk;
  }

  compute();
  selfTest();
})();
</script>

## How it's computed

Every value above comes from the same formulas the Python library uses, ported unchanged.
The shared building block is the **pH of saturation** (`pHs`), the standard analytical form
of Langelier's equation:

```text
pHs = (9.3 + A + B) - (C + D)
A   = (log10(TDS) - 1) / 10
B   = -13.12 * log10(T_kelvin) + 34.55
C   = log10(calcium_hardness_as_CaCO3) - 0.4
D   = log10(total_alkalinity_as_CaCO3)
```

| Index | Formula | Source |
|---|---|---|
| **LSI** (Langelier Saturation Index) | `LSI = pH - pHs` | Langelier, W. F. (1936), *J. AWWA* 28(10) |
| **RSI** (Ryznar Stability Index) | `RSI = 2*pHs - pH` | Ryznar, J. W. (1944), *J. AWWA* 36(4) |
| **PSI** (Puckorius Scaling Index) | `PSI = 2*pHs - pH_eq`, with `pH_eq = 1.465*log10(alkalinity) + 4.54` | Puckorius & Brooke (1991), *Corrosion* 47(4) |
| **CCPP** (Calcium Carbonate Precipitation Potential) | closed-system carbonate equilibrium solved to `[Ca][CO3] = Ksp`, in mg/L as CaCO₃ | Plummer & Busenberg (1982); Wojtowicz (2001) |

The PSI deliberately replaces the measured pH with an **equilibrium pH** driven only by
alkalinity, which makes it a better fit for the highly buffered, recirculating water typical
of cooling towers. CCPP goes beyond the *direction* the indices give and estimates the
*quantity* of calcium carbonate that would precipitate (`+`) or dissolve (`−`) to reach
calcite saturation; it is solved iteratively with the Plummer & Busenberg equilibrium
constants and a Davies activity model (ionic strength estimated as `μ ≈ 2.5×10⁻⁵ · TDS`).

The interpretation bands (LSI target ≈ 0 to +1; RSI/PSI `< 6` scaling, `6–7` balanced,
`> 7` corrosive) and their wording are ported verbatim from the library's
`interpret` module. For the full derivation, the Stiff-Davis index for high-salinity water,
and the cooling-tower water balance, see **[Indices & the science](indices.md)** and
**[CCPP](ccpp.md)**.

!!! note
    These are **screening calculations**, not a substitute for site-specific engineering
    judgment or a jar test. Band edges vary between published sources (some Ryznar tables put
    the balanced/corrosive boundary at 6.8 rather than 7.0), so treat values near a boundary
    as borderline. CCPP in particular is a semi-quantitative screen: its magnitude is
    dominated by the ionic-strength (activity) correction, and the dependency-free Davies
    model carries no ion pairing, so it tends to over-predict precipitation for hard,
    high-TDS water relative to a full speciation model such as PHREEQC. See the
    [interpretation guidance](indices.md) for details.

## Run the same numbers in Python

The calculator is a browser port of [`cooling-tower-chem`](index.md). To compute the same
indices in a script, notebook, or pipeline — and get input validation, the Stiff-Davis and
Larson-Skold indices, unit conversions, and the cooling-tower water balance — install the
library:

```bash
# From source (the first PyPI release is pending):
pip install git+https://github.com/Madhvansh/cooling-tower-chem
```

```python
from cooling_tower_chem import WaterSample

# The default inputs of the calculator above (TDS 1560 mg/L).
sample = WaterSample(
    ph=8.2, temperature_c=32,
    calcium_hardness=450, total_alkalinity=250,  # mg/L as CaCO3
    tds=1560,
)
print(round(sample.lsi(), 2))   # 1.38  -> scale-forming
print(round(sample.rsi(), 2))   # 5.44  -> heavy scale
print(round(sample.psi(), 2))   # 5.59
print(round(sample.ccpp(), 1))  # 66.6  mg/L as CaCO3
```

Installing the package also gives you the `ctchem` command line, which reproduces the same
figures:

```console
$ ctchem report --ph 8.2 --temp 32 --calcium 450 --alkalinity 250 --tds 1560
pH of saturation (pHs): 6.821
LSI: 1.379  [scale_forming]
    LSI +1.38: scale-forming; calcium carbonate will tend to precipitate.
RSI: 5.443  [severely_scale_forming]
    RSI 5.44: heavy scale formation expected.
...

$ ctchem ccpp --ph 8.2 --temp 32 --calcium 450 --alkalinity 250 --tds 1560
CCPP = +66.59 mg/L as CaCO3
```

See the [Command line](cli.md) page for every subcommand and `--json` output.

## Cross-checked against the library

To keep the browser calculator honest, this page runs a **self-test on load**: it computes
four reference cases with the in-page JavaScript and asserts each matches values produced by
the `cooling-tower-chem` Python library (`.venv` CPython) to within 0.01. The badge under the
calculator reports the result; the observed maximum deviation is on the order of `1e-6`.

| Case | Inputs (pH, °C, TDS, Ca, Alk) | LSI | RSI | PSI | CCPP (mg/L as CaCO₃) |
|---|---|---|---|---|---|
| A | 8.2, 32, 1560, 450, 250 | +1.38 | 5.44 | 5.59 | +66.6 |
| B | 7.5, 25, 400, 240, 180 | +0.19 | 7.12 | 6.78 | +17.5 |
| C | 8.0, 30, 2000, 900, 250 | +1.43 | 5.14 | 5.08 | +88.3 |
| D | 7.0, 20, 150, 50, 40 | −1.70 | 10.40 | 10.51 | −17.3 |

The JavaScript and Python columns agree on all four cases (the table shows the rounded Python
values; the self-test compares against the full-precision figures).
