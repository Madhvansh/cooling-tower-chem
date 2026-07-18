# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `CoolingTower` object: evaporation/drift/blowdown/makeup balance and a
  `concentrated()` projection of makeup chemistry at N cycles.
- Unit conversions (`convert`): mg/L-of-ion ↔ mg/L-as-CaCO3, grains/gallon, and
  Celsius/Fahrenheit.
- Runnable examples under `examples/`.

## [0.1.0] - 2026-07-19

### Added
- Saturation / corrosion indices: `ph_of_saturation`,
  `langelier_saturation_index` (LSI), `ryznar_stability_index` (RSI),
  `puckorius_scaling_index` (PSI), `larson_skold_index`, and
  `aggressiveness_index`.
- Cooling-tower water balance: `cycles_of_concentration`, `evaporation_loss`,
  `drift_loss`, `blowdown_loss`, `makeup_water`, `cycles_from_flows`,
  `water_saved_by_increasing_cycles`, and TDS ↔ conductivity conversion.
- Interpretation helpers (`interpret_lsi` and friends) returning a `Tendency`
  and a human-readable description.
- `WaterSample` convenience wrapper with a JSON-serializable `report()`.
- `ctchem` command-line interface.
- Test suite covering reference values, mass-balance identities, interpretation
  bands, and input validation.

[Unreleased]: https://github.com/Madhvansh/cooling-tower-chem/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/Madhvansh/cooling-tower-chem/releases/tag/v0.1.0
