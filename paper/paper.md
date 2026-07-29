---
title: 'cooling-tower-chem: a dependency-free Python library for cooling-tower and process-water chemistry'
tags:
  - Python
  - water treatment
  - cooling towers
  - water chemistry
  - corrosion
  - scaling
  - process engineering
authors:
  - name: Madhvansh Choksi
    orcid: 0009-0009-8169-6970
    affiliation: 1
affiliations:
  - name: Independent researcher, India
    index: 1
date: 25 July 2026
bibliography: paper.bib
---

# Summary

`cooling-tower-chem` is a small Python library that computes the water-stability,
scaling and corrosion indices used in industrial cooling-water treatment, together
with the mass-balance quantities that govern how a cooling tower is operated. It
implements the Langelier Saturation Index [@langelier1936], the Ryznar Stability
Index [@ryznar1944], the Puckorius Scaling Index [@puckorius1991], the
Larson–Skold corrosion ratio [@larson1958], the Stiff–Davis index for saline
waters [@astmD4582; @usbr2013], the AWWA Aggressiveness Index, and a thermodynamic
Calcium Carbonate Precipitation Potential (CCPP) built on the calcite solubility
fits of @plummer1982. Alongside the indices it provides cooling-tower water
balance — evaporation, drift, blowdown, makeup and cycles of concentration — and
the unit conversions (ion to CaCO₃ equivalents, mg/L to grains per gallon,
conductivity to TDS) that field data arrives in.

The library has no runtime dependencies beyond the Python standard library, is
typed, and ships a command-line interface (`ctchem`), a documented API, runnable
examples, and an interactive browser calculator. Every formula carries an inline
citation to the primary source it came from, so a result can be traced from a
returned number back to the paper that defines it.

# Statement of need

Cooling towers consume a large share of industrial water, and the decisions that
govern that consumption — how many cycles of concentration to run, whether the
circulating water is scaling or corrosive, how much inhibitor to dose — are made
from a handful of well-established indices. Those indices are more than half a
century old and are taught in every water-treatment course, yet the open-source
Python ecosystem has almost no tooling for them. Practitioners generally reach
for proprietary vendor calculators, spreadsheets passed between colleagues, or
one of the many free web calculators that show a number without stating which
formulation or temperature correlation produced it. None of these are citable,
version-controlled, testable, or reviewable.

This matters because the indices are not interchangeable and are not uniformly
defined. The Ryznar and Puckorius indices share a functional form but take
different pH inputs, and confusing them changes the operating conclusion.
Saturation-pH correlations differ between sources [@rossum1983]. The Stiff–Davis
constant is a curve fit that must be attributed [@usbr2013]. A spreadsheet that
silently picks one convention gives an answer that cannot be audited.

`cooling-tower-chem` exists to make these calculations reproducible and
inspectable: a dependency-free import, a stated source for every formula, and a
test suite that includes worked examples taken from the literature. Its intended
users are process and utilities engineers who need a scriptable calculation,
researchers who need a citable implementation in a paper or teaching notebook,
and developers building larger water-treatment tooling who would otherwise
reimplement these formulas themselves. The library was factored out of TGF, an
advisory cooling-tower toolkit by the same author, precisely so that the
chemistry could be reviewed, tested and cited independently of the application
that first needed it.

# Functionality

The public API is organised into five groups: `indices` (saturation and
corrosion indices), `advanced` (CCPP), `balance` (evaporation, drift, blowdown,
makeup, cycles), `convert` (unit and equivalent-weight conversions), and
`interpret` (mapping an index value to a scaling/corrosion tendency with a
plain-language explanation). Two convenience classes, `WaterSample` and
`CoolingTower`, wrap a full analysis so that a typical screening report is a
single call. The same calculations are reachable from the shell:

```
ctchem report --ph 7.5 --temp 29.3 --calcium 269 --alkalinity 255 --tds 800
```

The same entry point is reachable as `python -m cooling_tower_chem`, which does
not depend on the install's script directory being on `PATH`.

Inputs are validated — non-physical temperatures, non-positive concentrations
and non-finite values raise rather than propagate silently into an index.

# Quality control

The library is tested by 112 unit tests, including worked examples reproduced
from the source literature, and runs in continuous integration on CPython 3.9
through 3.13. It is distributed on PyPI using Trusted Publishing with Sigstore
build-provenance attestations, so a released artifact can be verified back to the
workflow run that built it. The project carries an OpenSSF Best Practices badge,
and documentation is published as a static site with an interactive calculator
whose results are cross-checked against the library's own outputs.

# References
