"""Tamil — 30 Zeichen (12 Vokale + 18 Konsonanten)."""

from __future__ import annotations

from typing import Final

from alphabets.gurmukhi.map import GURMUKHI_LAST_PRIME
from alphabets.lex import build_lex_order
from alphabets.primes import last_prime_in_block, next_prime_block
from alphabets.tamil.frequency import TAMIL_FREQUENCY_DESC

_TAMIL_SYMBOLS: Final[tuple[str, ...]] = (
    "அ", "ஆ", "இ", "ஈ", "உ", "ஊ", "எ", "ஏ", "ஐ", "ஒ", "ஓ", "ஔ",
    "க", "ங", "ச", "ஞ", "ட", "ண", "த", "ந", "ப", "ம", "ய", "ர", "ல", "வ", "ழ", "ள", "ற", "ன",
)

_TAMIL_PRIMES: Final[tuple[int, ...]] = next_prime_block(
    len(_TAMIL_SYMBOLS), after=GURMUKHI_LAST_PRIME
)
TAMIL_LAST_PRIME: Final[int] = last_prime_in_block(_TAMIL_PRIMES)

ALPHA_TAMIL: Final[dict[str, int]] = dict(zip(_TAMIL_SYMBOLS, _TAMIL_PRIMES))
CHAR_TAMIL: Final[dict[int, str]] = {v: k for k, v in ALPHA_TAMIL.items()}
ALPHA_TAMIL_LEX_ORDER: Final[tuple[str, ...]] = build_lex_order(
    _TAMIL_SYMBOLS, TAMIL_FREQUENCY_DESC
)
CHAR_TAMIL_SET: Final[frozenset[str]] = frozenset(ALPHA_TAMIL.keys())
