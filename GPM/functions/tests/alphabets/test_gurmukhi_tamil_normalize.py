"""Gurmukhi/Tamil Normalisierung — Mn-Strip und Whitelist."""

from __future__ import annotations

import sys
import unicodedata
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from alphabets.gurmukhi.map import CHAR_GURMUKHI_SET
from alphabets.gurmukhi.normalize import normalize_gurmukhi
from alphabets.normalize import is_valid_substrate, prepare_substrate
from alphabets.profiles import AlphabetProfile
from alphabets.tamil.map import CHAR_TAMIL_SET
from alphabets.tamil.normalize import normalize_tamil


def _has_mn(text: str) -> bool:
    return any(unicodedata.category(ch) == "Mn" for ch in text)


class TestGurmukhiTamilNormalize(unittest.TestCase):
    def test_gurmukhi_bindi_stripped(self) -> None:
        raw = "ਪ\u0A02ਜਾਬ"
        out = normalize_gurmukhi(raw)
        self.assertFalse(_has_mn(out))
        self.assertTrue(all(ch in CHAR_GURMUKHI_SET for ch in out))
        self.assertNotIn("\u0A02", out)

    def test_tamil_pulli_stripped(self) -> None:
        raw = "க\u0BCDமல"
        out = normalize_tamil(raw)
        self.assertFalse(_has_mn(out))
        self.assertTrue(all(ch in CHAR_TAMIL_SET for ch in out))
        self.assertNotIn("\u0BCD", out)

    def test_unknown_mn_never_in_substrate(self) -> None:
        gurmukhi_extra = prepare_substrate("ਕ\u0A02", AlphabetProfile.GURMUKHI)
        self.assertTrue(all(ch in CHAR_GURMUKHI_SET for ch in gurmukhi_extra))
        tamil_extra = prepare_substrate("க\u0B82", AlphabetProfile.TAMIL)
        self.assertTrue(all(ch in CHAR_TAMIL_SET for ch in tamil_extra))
        if gurmukhi_extra:
            self.assertTrue(is_valid_substrate(gurmukhi_extra, AlphabetProfile.GURMUKHI))


if __name__ == "__main__":
    unittest.main()
