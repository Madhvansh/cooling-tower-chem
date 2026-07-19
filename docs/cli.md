# Command line

Installing the package provides a `ctchem` command.

## Full report

```console
$ ctchem report --ph 8.2 --temp 32 --calcium 450 --alkalinity 250 \
      --conductivity 2400 --chloride 180 --sulfate 120
pH of saturation (pHs): 6.821
LSI: 1.379  [scale_forming]
    LSI +1.38: scale-forming; calcium carbonate will tend to precipitate.
RSI: 5.443  [severely_scale_forming]
    RSI 5.44: heavy scale formation expected.
PSI: 5.59  [scale_forming]
    PSI 5.59: scale-forming tendency.
AGGRESSIVENESS INDEX: 13.251  [balanced]
    AI 13.25: non-aggressive water.
LARSON SKOLD INDEX: 1.516  [severely_corrosive]
    Larson-Skold 1.52: high corrosion rates on mild steel expected.
```

## A single index

```console
$ ctchem lsi --ph 7.5 --temp 25 --tds 400 --calcium 240 --alkalinity 180
LSI = +0.190
```

The `psi` subcommand takes no `--ph` (the Puckorius index uses an equilibrium pH):

```console
$ ctchem psi --temp 25 --tds 400 --calcium 240 --alkalinity 180
PSI = +6.776
```

## Precipitation potential (CCPP)

The `ccpp` subcommand reports the mass of CaCO₃ that must precipitate (`+`) or
dissolve (`−`) to reach calcite saturation, in mg/L as CaCO₃:

```console
$ ctchem ccpp --ph 8.0 --temp 30 --calcium 900 --alkalinity 250 --tds 2000
CCPP = +88.28 mg/L as CaCO3
```

CCPP is sensitive to the ionic strength, and the TDS estimate is only a rough
guide, so pass `--ionic-strength` (mol/L) to override it with a measured or
model-derived value. See [CCPP](ccpp.md) for the method and caveats.

## JSON output

Add `--json` to any command for machine-readable output:

```console
$ ctchem lsi --ph 7.5 --temp 25 --tds 400 --calcium 240 --alkalinity 180 --json
{"lsi": 0.19}
```

Provide either `--tds` (mg/L) or `--conductivity` (µS/cm); they are mutually
exclusive. Invalid inputs exit non-zero with a clear error message.
