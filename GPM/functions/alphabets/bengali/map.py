"""Bengali — 35 Basis-Konsonanten."""

from __future__ import annotations

from typing import Final

from alphabets.bengali.frequency import BENGALI_FREQUENCY_DESC
from alphabets.lex import build_lex_order
from alphabets.primes import last_prime_in_block, next_prime_block
from alphabets.tifinagh.map import TIFINAGH_LAST_PRIME

_BENGALI_SYMBOLS: Final[tuple[str, ...]] = (
    "ক", "খ", "গ", "ঘ", "ঙ", "চ", "ছ", "জ", "ঝ", "ঞ", "ট", "ঠ", "ড", "ঢ", "ণ",
    "ত", "থ", "দ", "ধ", "ন", "প", "ফ", "ব", "ভ", "ম", "য", "র", "ল", "শ", "ষ",
    "স", "হ", "ড়", "ঢ়", "য়",
)

_BENGALI_PRIMES: Final[tuple[int, ...]] = next_prime_block(
    len(_BENGALI_SYMBOLS), after=TIFINAGH_LAST_PRIME
)
BENGALI_LAST_PRIME: Final[int] = last_prime_in_block(_BENGALI_PRIMES)

ALPHA_BENGALI: Final[dict[str, int]] = dict(zip(_BENGALI_SYMBOLS, _BENGALI_PRIMES))
CHAR_BENGALI: Final[dict[int, str]] = {v: k for k, v in ALPHA_BENGALI.items()}
ALPHA_BENGALI_LEX_ORDER: Final[tuple[str, ...]] = build_lex_order(
    _BENGALI_SYMBOLS, BENGALI_FREQUENCY_DESC
)
CHAR_BENGALI_SET: Final[frozenset[str]] = frozenset(ALPHA_BENGALI.keys())
