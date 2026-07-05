"""Amharic — 34 Ge'ez-Basiszeichen."""

from __future__ import annotations

from typing import Final

from alphabets.amharic.frequency import AMHARIC_FREQUENCY_DESC
from alphabets.lex import build_lex_order
from alphabets.primes import last_prime_in_block, next_prime_block
from alphabets.tamil.map import TAMIL_LAST_PRIME

_AMHARIC_BASES: Final[tuple[str, ...]] = (
    "ሀ", "ለ", "ሐ", "መ", "ሠ", "ረ", "ሰ", "ሸ", "ቀ", "ቈ", "በ", "ቨ", "ተ", "ቸ",
    "ኀ", "ነ", "ኘ", "አ", "ከ", "ኸ", "ወ", "ዐ", "ዘ", "ዠ", "የ", "ደ", "ጀ", "ገ",
    "ጠ", "ጨ", "ጰ", "ጸ", "ፀ", "ፈ",
)

_AMHARIC_PRIMES: Final[tuple[int, ...]] = next_prime_block(
    len(_AMHARIC_BASES), after=TAMIL_LAST_PRIME
)
AMHARIC_LAST_PRIME: Final[int] = last_prime_in_block(_AMHARIC_PRIMES)

ALPHA_AMHARIC: Final[dict[str, int]] = dict(zip(_AMHARIC_BASES, _AMHARIC_PRIMES))
CHAR_AMHARIC: Final[dict[int, str]] = {v: k for k, v in ALPHA_AMHARIC.items()}
ALPHA_AMHARIC_LEX_ORDER: Final[tuple[str, ...]] = build_lex_order(
    _AMHARIC_BASES, AMHARIC_FREQUENCY_DESC
)
CHAR_AMHARIC_SET: Final[frozenset[str]] = frozenset(ALPHA_AMHARIC.keys())

# Silbe (U+1200–U+137F) → Basis-Konsonant
_SYLLABLE_TO_BASE: Final[dict[str, str]] = {}
for _base in _AMHARIC_BASES:
    _ord_base = ord(_base)
    for _offset in range(8):
        _syllable = chr(_ord_base + _offset)
        if "\u1200" <= _syllable <= "\u137F":
            _SYLLABLE_TO_BASE[_syllable] = _base
