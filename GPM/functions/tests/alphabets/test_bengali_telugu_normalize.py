"""Bengali/Telugu Normalisierung — Matra-Strip und Whitelist."""

from __future__ import annotations

import sys
import unicodedata
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from alphabets.bengali.map import CHAR_BENGALI_SET
from alphabets.bengali.normalize import normalize_bengali
from alphabets.normalize import prepare_substrate
from alphabets.profiles import AlphabetProfile
from alphabets.telugu.map import CHAR_TELUGU_SET
from alphabets.telugu.normalize import normalize_telugu


def _has_mn(text: str) -> bool:
    return any(unicodedata.category(ch) == "Mn" for ch in text)


class TestBengaliTeluguNormalize(unittest.TestCase):
    def test_bengali_matra_stripped(self) -> None:
        raw = "ব\u09BE\u09B2"
        out = normalize_bengali(raw)
        self.assertFalse(_has_mn(out))
        self.assertTrue(all(ch in CHAR_BENGALI_SET for ch in out))
        self.assertNotIn("\u09BE", out)

    def test_telugu_matra_stripped(self) -> None:
        raw = "త\u0C46\u0C32"
        out = normalize_telugu(raw)
        self.assertFalse(_has_mn(out))
        self.assertTrue(all(ch in CHAR_TELUGU_SET for ch in out))
        self.assertNotIn("\u0C46", out)

    def test_unknown_mn_never_in_substrate(self) -> None:
        bengali = prepare_substrate("ব\u0982", AlphabetProfile.BENGALI)
        self.assertTrue(all(ch in CHAR_BENGALI_SET for ch in bengali))
        telugu = prepare_substrate("త\u0C02", AlphabetProfile.TELUGU)
        self.assertTrue(all(ch in CHAR_TELUGU_SET for ch in telugu))


if __name__ == "__main__":
    unittest.main()
