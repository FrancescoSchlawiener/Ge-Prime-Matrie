"""Thai — 44 Konsonanten + 8 Kern-Vokale."""

from __future__ import annotations

from typing import Final

from alphabets.devanagari.map import DEVANAGARI_LAST_PRIME
from alphabets.lex import build_lex_order
from alphabets.primes import last_prime_in_block, next_prime_block
from alphabets.thai.frequency import THAI_FREQUENCY_DESC

_THAI_SYMBOLS: Final[tuple[str, ...]] = (
    "ก", "ข", "ค", "ฆ", "ง", "จ", "ฉ", "ช", "ซ", "ฌ", "ญ", "ฎ", "ฏ", "ฑ",
    "ฒ", "ณ", "ด", "ต", "ท", "ธ", "น", "บ", "ป", "ผ", "ฝ", "พ", "ฟ", "ภ",
    "ม", "ย", "ร", "ล", "ว", "ศ", "ษ", "ส", "ห", "ฬ", "อ", "ฮ",
    "ะ", "า", "ิ", "ี", "ึ", "ื", "ุ", "ู",
)

_THAI_PRIMES: Final[tuple[int, ...]] = next_prime_block(
    len(_THAI_SYMBOLS), after=DEVANAGARI_LAST_PRIME
)
THAI_LAST_PRIME: Final[int] = last_prime_in_block(_THAI_PRIMES)

ALPHA_THAI: Final[dict[str, int]] = dict(zip(_THAI_SYMBOLS, _THAI_PRIMES))
CHAR_THAI: Final[dict[int, str]] = {v: k for k, v in ALPHA_THAI.items()}
ALPHA_THAI_LEX_ORDER: Final[tuple[str, ...]] = build_lex_order(
    _THAI_SYMBOLS, THAI_FREQUENCY_DESC
)
CHAR_THAI_SET: Final[frozenset[str]] = frozenset(ALPHA_THAI.keys())
