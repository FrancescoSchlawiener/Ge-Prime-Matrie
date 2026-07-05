"""Gardiner-Varianten → 24 Uniliterale (Katalognummer-Mapping)."""

from __future__ import annotations

from typing import Final

from alphabets.aesthetic_hieroglyphs.map import CHAR_AESTHETIC_HIEROGLYPHS_SET

# Ur-Phoneme (24 registrierte Uniliterale)
_A = "\U0001313F"
_I = "\U000131CB"
_Y = "\U0001336D"
_AA = "\U00013253"
_B = "\U000130C0"
_P = "\U000132EA"
_F = "\U00013191"
_M = "\U000130D4"
_N = "\U00013196"
_R = "\U0001308B"
_H = "\U00013250"
_H2 = "\U0001321B"
_X = "\U0001330D"
_X2 = "\U00013121"
_S = "\U000132F4"
_S2 = "\U000132BD"
_Q = "\U000132C3"
_K = "\U000133A1"
_G = "\U000133BC"
_T = "\U000133CF"
_T2 = "\U0001337F"
_D = "\U000130A7"
_D2 = "\U0001336F"
_W = "\U00013037"

GLYPH_TO_UNILITERAL: Final[dict[str, str]] = {
    # N (water) — Gardiner N35/N17/N16 Varianten
    "\U00013197": _N,
    "\U00013195": _N,
    "\U00013198": _N,
    # R (mouth) — D21 Varianten
    "\U0001308C": _R,
    "\U0001308D": _R,
    # M (owl) — G43/G42 Varianten
    "\U0001313E": _M,
    "\U00013140": _M,
    # A (vulture) — G1 Varianten
    "\U0001313D": _A,
    "\U00013141": _A,
    # I (reed) — M17/M18
    "\U000131CC": _I,
    # W (chick) — G40/G41
    "\U00013038": _W,
    "\U00013039": _W,
    # B (foot) — D58/D59
    "\U000130C1": _B,
    # D (hand) — D46/D47
    "\U000130A8": _D,
    # K ( basket) — V28 variants
    "\U000133A2": _K,
}

# Nur Einträge deren Ziel in der 24er-Whitelist liegt
assert all(v in CHAR_AESTHETIC_HIEROGLYPHS_SET for v in GLYPH_TO_UNILITERAL.values())
