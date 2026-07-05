"""Katakana — 46 Gojuon-Zeichen."""

from __future__ import annotations

from typing import Final

from alphabets.hiragana.map import HIRAGANA_LAST_PRIME
from alphabets.katakana.frequency import KATAKANA_FREQUENCY_DESC
from alphabets.lex import build_lex_order
from alphabets.primes import last_prime_in_block, next_prime_block

_KATAKANA_SYMBOLS: Final[tuple[str, ...]] = (
    "ア", "イ", "ウ", "エ", "オ", "カ", "キ", "ク", "ケ", "コ", "サ", "シ", "ス",
    "セ", "ソ", "タ", "チ", "ツ", "テ", "ト", "ナ", "ニ", "ヌ", "ネ", "ノ", "ハ",
    "ヒ", "フ", "ヘ", "ホ", "マ", "ミ", "ム", "メ", "モ", "ヤ", "ユ", "ヨ", "ラ",
    "リ", "ル", "レ", "ロ", "ワ", "ヲ", "ン",
)

_KATAKANA_PRIMES: Final[tuple[int, ...]] = next_prime_block(
    len(_KATAKANA_SYMBOLS), after=HIRAGANA_LAST_PRIME
)
KATAKANA_LAST_PRIME: Final[int] = last_prime_in_block(_KATAKANA_PRIMES)

ALPHA_KATAKANA: Final[dict[str, int]] = dict(zip(_KATAKANA_SYMBOLS, _KATAKANA_PRIMES))
CHAR_KATAKANA: Final[dict[int, str]] = {v: k for k, v in ALPHA_KATAKANA.items()}
ALPHA_KATAKANA_LEX_ORDER: Final[tuple[str, ...]] = build_lex_order(
    _KATAKANA_SYMBOLS, KATAKANA_FREQUENCY_DESC
)
CHAR_KATAKANA_SET: Final[frozenset[str]] = frozenset(ALPHA_KATAKANA.keys())
