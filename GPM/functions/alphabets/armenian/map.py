"""Armenian — 38 Mkhedruli-Buchstaben."""

from __future__ import annotations

from typing import Final

from alphabets.armenian.frequency import ARMENIAN_FREQUENCY_DESC
from alphabets.katakana.map import KATAKANA_LAST_PRIME
from alphabets.lex import build_lex_order
from alphabets.primes import last_prime_in_block, next_prime_block

_ARMENIAN_SYMBOLS: Final[tuple[str, ...]] = (
    "Ա", "Բ", "Գ", "Դ", "Ե", "Զ", "Է", "Ը", "Թ", "Ժ", "Ի", "Լ", "Խ", "Ծ",
    "Կ", "Հ", "Ձ", "Ղ", "Ճ", "Մ", "Յ", "Ն", "Շ", "Ո", "Չ", "Պ", "Ջ", "Ռ",
    "Ս", "Վ", "Տ", "Ր", "Ց", "Ւ", "Փ", "Ք", "Օ", "Ֆ",
)

_ARMENIAN_PRIMES: Final[tuple[int, ...]] = next_prime_block(
    len(_ARMENIAN_SYMBOLS), after=KATAKANA_LAST_PRIME
)
ARMENIAN_LAST_PRIME: Final[int] = last_prime_in_block(_ARMENIAN_PRIMES)

ALPHA_ARMENIAN: Final[dict[str, int]] = dict(zip(_ARMENIAN_SYMBOLS, _ARMENIAN_PRIMES))
CHAR_ARMENIAN: Final[dict[int, str]] = {v: k for k, v in ALPHA_ARMENIAN.items()}
ALPHA_ARMENIAN_LEX_ORDER: Final[tuple[str, ...]] = build_lex_order(
    _ARMENIAN_SYMBOLS, ARMENIAN_FREQUENCY_DESC
)
CHAR_ARMENIAN_SET: Final[frozenset[str]] = frozenset(ALPHA_ARMENIAN.keys())
