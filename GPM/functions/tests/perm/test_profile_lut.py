"""Profil-LUT — Lazy-Singleton-Gebot."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from alphabets.profiles import AlphabetProfile
from alphabets.arabic.map import ALPHA_ARABIC_LEX_ORDER
from perm.lut import (
    ALPHA_ROMAN_SINGLETON_LUTS,
    _SINGLETON_LUTS,
    get_singleton_lut,
)


class TestProfileLut(unittest.TestCase):
    def setUp(self) -> None:
        _SINGLETON_LUTS.clear()

    def test_roman_eager_on_import(self) -> None:
        self.assertEqual(len(ALPHA_ROMAN_SINGLETON_LUTS), 27)

    def test_lazy_singleton_luts_empty_initially(self) -> None:
        fresh: dict = {}
        self.assertEqual(len(fresh), 0)
        sym = ALPHA_ARABIC_LEX_ORDER[0]
        get_singleton_lut(sym, AlphabetProfile.ARABIC)
        self.assertIn(AlphabetProfile.ARABIC, _SINGLETON_LUTS)
        self.assertNotIn(AlphabetProfile.THAI, _SINGLETON_LUTS)
        self.assertNotIn(AlphabetProfile.HANGUL, _SINGLETON_LUTS)

    def test_arabic_lazy_only(self) -> None:
        _SINGLETON_LUTS.pop(AlphabetProfile.ARABIC, None)
        sym = ALPHA_ARABIC_LEX_ORDER[0]
        get_singleton_lut(sym, AlphabetProfile.ARABIC)
        self.assertIn(AlphabetProfile.ARABIC, _SINGLETON_LUTS)
        self.assertNotIn(AlphabetProfile.THAI, _SINGLETON_LUTS)

    def test_greek_lazy_on_first_access(self) -> None:
        from alphabets.greek.map import ALPHA_GREEK_LEX_ORDER

        sym = ALPHA_GREEK_LEX_ORDER[0]
        get_singleton_lut(sym, AlphabetProfile.GREEK)
        self.assertIn(AlphabetProfile.GREEK, _SINGLETON_LUTS)
        self.assertNotIn(AlphabetProfile.DEVANAGARI, _SINGLETON_LUTS)


if __name__ == "__main__":
    unittest.main()
