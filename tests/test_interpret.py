"""Tests for the interpretation bands."""

from cooling_tower_chem import (
    Tendency,
    interpret_aggressiveness,
    interpret_larson_skold,
    interpret_lsi,
    interpret_psi,
    interpret_rsi,
    interpret_stiff_davis,
)


def test_lsi_bands():
    assert interpret_lsi(-3.0)[0] is Tendency.SEVERELY_CORROSIVE
    assert interpret_lsi(-1.0)[0] is Tendency.CORROSIVE
    assert interpret_lsi(0.0)[0] is Tendency.BALANCED
    assert interpret_lsi(0.3)[0] is Tendency.BALANCED
    assert interpret_lsi(1.0)[0] is Tendency.SCALE_FORMING
    assert interpret_lsi(2.5)[0] is Tendency.SEVERELY_SCALE_FORMING


def test_rsi_bands():
    assert interpret_rsi(5.0)[0] is Tendency.SEVERELY_SCALE_FORMING
    assert interpret_rsi(6.0)[0] is Tendency.SCALE_FORMING
    assert interpret_rsi(6.5)[0] is Tendency.BALANCED
    assert interpret_rsi(7.5)[0] is Tendency.CORROSIVE
    assert interpret_rsi(9.0)[0] is Tendency.SEVERELY_CORROSIVE


def test_psi_reuses_rsi_bands_but_relabels():
    tendency, text = interpret_psi(6.5)
    assert tendency is Tendency.BALANCED
    assert "PSI" in text and "RSI" not in text


def test_stiff_davis_reuses_lsi_bands_but_relabels():
    tendency, text = interpret_stiff_davis(1.0)
    assert tendency is Tendency.SCALE_FORMING
    assert "S&DSI" in text and "LSI" not in text
    assert interpret_stiff_davis(-1.0)[0] is Tendency.CORROSIVE


def test_larson_skold_bands():
    assert interpret_larson_skold(0.5)[0] is Tendency.BALANCED
    assert interpret_larson_skold(1.0)[0] is Tendency.CORROSIVE
    assert interpret_larson_skold(2.0)[0] is Tendency.SEVERELY_CORROSIVE


def test_aggressiveness_bands():
    assert interpret_aggressiveness(9.0)[0] is Tendency.SEVERELY_CORROSIVE
    assert interpret_aggressiveness(11.0)[0] is Tendency.CORROSIVE
    assert interpret_aggressiveness(12.5)[0] is Tendency.BALANCED


def test_tendency_str_is_value():
    assert str(Tendency.BALANCED) == "balanced"


def test_descriptions_are_nonempty_strings():
    for fn, val in (
        (interpret_lsi, 0.2),
        (interpret_rsi, 6.5),
        (interpret_psi, 6.5),
        (interpret_larson_skold, 0.5),
        (interpret_aggressiveness, 12.5),
    ):
        tendency, text = fn(val)
        assert isinstance(text, str) and text
