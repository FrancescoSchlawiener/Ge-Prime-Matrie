"""Georgian — 33 Mkhedruli-Buchstaben."""

from __future__ import annotations

from typing import Final

from alphabets.armenian.map import ARMENIAN_LAST_PRIME
from alphabets.georgian.frequency import GEORGIAN_FREQUENCY_DESC
from alphabets.lex import build_lex_order
from alphabets.primes import last_prime_in_block, next_prime_block

_GEORGIAN_SYMBOLS: Final[tuple[str, ...]] = (
    "ა", "ბ", "გ", "დ", "ე", "ვ", "ზ", "თ", "ი", "კ", "ლ", "მ", "ნ", "ო",
    "პ", "ჟ", "რ", "ს", "ტ", "უ", "ფ", "ქ", "ღ", "ყ", "შ", "ჩ", "ც", "ძ",
    "წ", "ჭ", "ხ", "ჯ", "ჰ",
)

_GEORGIAN_PRIMES: Final[tuple[int, ...]] = next_prime_block(
    len(_GEORGIAN_SYMBOLS), after=ARMENIAN_LAST_PRIME
)
GEORGIAN_LAST_PRIME: Final[int] = last_prime_in_block(_GEORGIAN_PRIMES)

ALPHA_GEORGIAN: Final[dict[str, int]] = dict(zip(_GEORGIAN_SYMBOLS, _GEORGIAN_PRIMES))
CHAR_GEORGIAN: Final[dict[int, str]] = {v: k for k, v in ALPHA_GEORGIAN.items()}
ALPHA_GEORGIAN_LEX_ORDER: Final[tuple[str, ...]] = build_lex_order(
    _GEORGIAN_SYMBOLS, GEORGIAN_FREQUENCY_DESC
)
CHAR_GEORGIAN_SET: Final[frozenset[str]] = frozenset(ALPHA_GEORGIAN.keys())
