"""Cyrillic alphabet — eigener Primblock."""

from __future__ import annotations

from typing import Final

from alphabets.cyrillic.frequency import CYRILLIC_FREQUENCY_DESC
from alphabets.lex import build_lex_order

_CYRILLIC_SYMBOLS: Final[tuple[str, ...]] = (
    "А", "Б", "В", "Г", "Д", "Е", "Ё", "Ж", "З", "И", "Й", "К", "Л", "М",
    "Н", "О", "П", "Р", "С", "Т", "У", "Ф", "Х", "Ц", "Ч", "Ш", "Щ", "Ъ",
    "Ы", "Ь", "Э", "Ю", "Я",
)

_CYRILLIC_PRIMES: Final[tuple[int, ...]] = (
    241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 317,
    331, 337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397, 401, 409,
    419, 421, 431, 433, 439,
)
CYRILLIC_LAST_PRIME: Final[int] = _CYRILLIC_PRIMES[-1]

ALPHA_CYRILLIC: Final[dict[str, int]] = dict(zip(_CYRILLIC_SYMBOLS, _CYRILLIC_PRIMES))
CHAR_CYRILLIC: Final[dict[int, str]] = {v: k for k, v in ALPHA_CYRILLIC.items()}
ALPHA_CYRILLIC_LEX_ORDER: Final[tuple[str, ...]] = build_lex_order(
    _CYRILLIC_SYMBOLS, CYRILLIC_FREQUENCY_DESC
)
CHAR_CYRILLIC_SET: Final[frozenset[str]] = frozenset(ALPHA_CYRILLIC.keys())
