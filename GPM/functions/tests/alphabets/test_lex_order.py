"""Querschnitt — LEX-Reihenfolge vs Unicode-Sort."""

from __future__ import annotations

import sys
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from alphabets.cyrillic.frequency import CYRILLIC_FREQUENCY_DESC
from alphabets.cyrillic.map import ALPHA_CYRILLIC_LEX_ORDER
from alphabets.profiles import AlphabetProfile
from alphabets.registry import lex_order_for_profile
from alphabets.roman.frequency import ROMAN_FREQUENCY_DESC
from alphabets.roman.map import ALPHA_ROMAN_LEX_ORDER
from perm.multiset import perm_decode, perm_index


class TestLexOrder(unittest.TestCase):
    def test_roman_most_frequent_at_bottom(self) -> None:
        self.assertEqual(ALPHA_ROMAN_LEX_ORDER[-1], ROMAN_FREQUENCY_DESC[0])

    def test_cyrillic_most_frequent_at_bottom(self) -> None:
        self.assertEqual(ALPHA_CYRILLIC_LEX_ORDER[-1], CYRILLIC_FREQUENCY_DESC[0])

    def test_cyrillic_yo_lex_differs_from_unicode_sort(self) -> None:
        lex = lex_order_for_profile(AlphabetProfile.CYRILLIC)
        unicode_order = sorted({"Ё", "А", "Б"})
        lex_order = sorted({"Ё", "А", "Б"}, key=lambda c: lex.index(c))
        self.assertNotEqual(lex_order, unicode_order)

    def test_perm_roundtrip_with_lex(self) -> None:
        lex = lex_order_for_profile(AlphabetProfile.ROMAN)
        seq = "HALLO"
        counts = Counter(seq)
        idx = perm_index(list(seq), counts, lex_order=lex)
        decoded = "".join(perm_decode(counts, idx, lex_order=lex))
        self.assertEqual(decoded, seq)


if __name__ == "__main__":
    unittest.main()
