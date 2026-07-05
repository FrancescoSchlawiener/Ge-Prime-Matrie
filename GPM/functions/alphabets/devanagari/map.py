"""Devanagari — 46 Kernzeichen (13 Vokale + 33 Konsonanten)."""

from __future__ import annotations

from typing import Final

from alphabets.devanagari.frequency import DEVANAGARI_FREQUENCY_DESC
from alphabets.hebrew.map import HEBREW_LAST_PRIME
from alphabets.lex import build_lex_order
from alphabets.primes import last_prime_in_block, next_prime_block

_DEVANAGARI_SYMBOLS: Final[tuple[str, ...]] = (
    "अ", "आ", "इ", "ई", "उ", "ऊ", "ए", "ऐ", "ओ", "औ", "ऋ", "ं", "ः",
    "क", "ख", "ग", "घ", "ङ", "च", "छ", "ज", "झ", "ञ", "ट", "ठ", "ड", "ढ",
    "ण", "त", "थ", "द", "ध", "न", "प", "फ", "ब", "भ", "म", "य", "र", "ल",
    "व", "श", "ष", "स", "ह",
)

_DEVANAGARI_PRIMES: Final[tuple[int, ...]] = next_prime_block(
    len(_DEVANAGARI_SYMBOLS), after=HEBREW_LAST_PRIME
)
DEVANAGARI_LAST_PRIME: Final[int] = last_prime_in_block(_DEVANAGARI_PRIMES)

ALPHA_DEVANAGARI: Final[dict[str, int]] = dict(zip(_DEVANAGARI_SYMBOLS, _DEVANAGARI_PRIMES))
CHAR_DEVANAGARI: Final[dict[int, str]] = {v: k for k, v in ALPHA_DEVANAGARI.items()}
ALPHA_DEVANAGARI_LEX_ORDER: Final[tuple[str, ...]] = build_lex_order(
    _DEVANAGARI_SYMBOLS, DEVANAGARI_FREQUENCY_DESC
)
CHAR_DEVANAGARI_SET: Final[frozenset[str]] = frozenset(ALPHA_DEVANAGARI.keys())
