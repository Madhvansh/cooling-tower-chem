"""Command-line interface: ``ctchem``.

Compute a full water-chemistry report from the terminal::

    ctchem report --ph 8.2 --temp 32 --calcium 450 --alkalinity 250 \\
        --conductivity 2400 --chloride 180 --sulfate 120

    ctchem lsi --ph 7.5 --temp 25 --tds 400 --calcium 240 --alkalinity 180

Use ``--json`` for machine-readable output.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence

from . import __version__
from .sample import WaterSample


def _add_saturation_args(parser: argparse.ArgumentParser, need_ph: bool = True) -> None:
    if need_ph:
        parser.add_argument("--ph", type=float, required=True, help="measured pH")
    parser.add_argument(
        "--temp", type=float, required=True, help="temperature in degrees C"
    )
    parser.add_argument(
        "--calcium",
        type=float,
        required=True,
        help="calcium hardness, mg/L as CaCO3",
    )
    parser.add_argument(
        "--alkalinity",
        type=float,
        required=True,
        help="total alkalinity, mg/L as CaCO3",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--tds", type=float, help="total dissolved solids, mg/L")
    group.add_argument(
        "--conductivity", type=float, help="conductivity, uS/cm (converted to TDS)"
    )


def _sample_from_args(args: argparse.Namespace) -> WaterSample:
    return WaterSample(
        ph=getattr(args, "ph", 7.0),
        temperature_c=args.temp,
        calcium_hardness=args.calcium,
        total_alkalinity=args.alkalinity,
        tds=args.tds,
        conductivity_us_cm=args.conductivity,
        chloride=getattr(args, "chloride", None),
        sulfate=getattr(args, "sulfate", None),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ctchem",
        description="Water-stability and corrosion indices for cooling towers.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p_report = sub.add_parser("report", help="all indices with interpretation")
    _add_saturation_args(p_report)
    p_report.add_argument("--chloride", type=float, help="chloride, mg/L (for Larson-Skold)")
    p_report.add_argument("--sulfate", type=float, help="sulfate, mg/L (for Larson-Skold)")
    p_report.add_argument("--json", action="store_true", help="emit JSON")

    for name, help_text in (
        ("lsi", "Langelier Saturation Index"),
        ("rsi", "Ryznar Stability Index"),
        ("psi", "Puckorius Scaling Index"),
    ):
        p = sub.add_parser(name, help=help_text)
        _add_saturation_args(p, need_ph=(name != "psi"))
        p.add_argument("--json", action="store_true", help="emit JSON")

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        sample = _sample_from_args(args)
        if args.command == "report":
            result = sample.report()
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                _print_report(result)
        else:
            value = {
                "lsi": sample.lsi,
                "rsi": sample.rsi,
                "psi": sample.psi,
            }[args.command]()
            if args.json:
                print(json.dumps({args.command: round(value, 3)}))
            else:
                print(f"{args.command.upper()} = {value:+.3f}")
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


def _print_report(result: dict) -> None:
    print(f"pH of saturation (pHs): {result['ph_of_saturation']}")
    for key in ("lsi", "rsi", "psi", "aggressiveness_index", "larson_skold_index"):
        entry = result.get(key)
        if entry is None:
            continue
        print(f"{key.replace('_', ' ').upper()}: {entry['value']}  [{entry['tendency']}]")
        print(f"    {entry['description']}")


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
