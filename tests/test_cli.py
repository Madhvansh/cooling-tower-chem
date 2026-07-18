"""Tests for the ctchem command-line interface."""

import json

import pytest

from cooling_tower_chem.cli import main


def test_report_json(capsys):
    rc = main([
        "report", "--ph", "8.2", "--temp", "32", "--calcium", "450",
        "--alkalinity", "250", "--conductivity", "2400",
        "--chloride", "180", "--sulfate", "120", "--json",
    ])
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["lsi"]["tendency"] == "scale_forming"
    assert "larson_skold_index" in payload


def test_lsi_text(capsys):
    rc = main([
        "lsi", "--ph", "7.5", "--temp", "25", "--tds", "400",
        "--calcium", "240", "--alkalinity", "180",
    ])
    assert rc == 0
    out = capsys.readouterr().out.strip()
    assert out.startswith("LSI = +0.190")


def test_psi_requires_no_ph(capsys):
    rc = main([
        "psi", "--temp", "25", "--tds", "400",
        "--calcium", "240", "--alkalinity", "180", "--json",
    ])
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["psi"] == pytest.approx(6.776, abs=1e-3)


def test_invalid_value_returns_error_code(capsys):
    rc = main([
        "lsi", "--ph", "7.5", "--temp", "25", "--tds", "0",
        "--calcium", "240", "--alkalinity", "180",
    ])
    assert rc == 2
    assert "error:" in capsys.readouterr().err


def test_conductivity_and_tds_mutually_exclusive():
    with pytest.raises(SystemExit):
        main([
            "lsi", "--ph", "7.5", "--temp", "25", "--tds", "400",
            "--conductivity", "600", "--calcium", "240", "--alkalinity", "180",
        ])
