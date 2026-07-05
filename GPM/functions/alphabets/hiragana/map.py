"""Hiragana — 46 Gojuon-Zeichen."""

from __future__ import annotations

from typing import Final

from alphabets.hangul.map import HANGUL_LAST_PRIME
from alphabets.hiragana.frequency import HIRAGANA_FREQUENCY_DESC
from alphabets.lex import build_lex_order
from alphabets.primes import last_prime_in_block, next_prime_block

_HIRAGANA_SYMBOLS: Final[tuple[str, ...]] = (
    "あ", "い", "う", "え", "お", "か", "き", "く", "け", "こ", "さ", "し", "す",
    "せ", "そ", "た", "ち", "つ", "て", "と", "な", "に", "ぬ", "ね", "の", "は",
    "ひ", "ふ", "へ", "ほ", "ま", "み", "む", "め", "も", "や", "ゆ", "よ", "ら",
    "り", "る", "れ", "ろ", "わ", "を", "ん",
)

_HIRAGANA_PRIMES: Final[tuple[int, ...]] = next_prime_block(
    len(_HIRAGANA_SYMBOLS), after=HANGUL_LAST_PRIME
)
HIRAGANA_LAST_PRIME: Final[int] = last_prime_in_block(_HIRAGANA_PRIMES)

ALPHA_HIRAGANA: Final[dict[str, int]] = dict(zip(_HIRAGANA_SYMBOLS, _HIRAGANA_PRIMES))
CHAR_HIRAGANA: Final[dict[int, str]] = {v: k for k, v in ALPHA_HIRAGANA.items()}
ALPHA_HIRAGANA_LEX_ORDER: Final[tuple[str, ...]] = build_lex_order(
    _HIRAGANA_SYMBOLS, HIRAGANA_FREQUENCY_DESC
)
CHAR_HIRAGANA_SET: Final[frozenset[str]] = frozenset(ALPHA_HIRAGANA.keys())
