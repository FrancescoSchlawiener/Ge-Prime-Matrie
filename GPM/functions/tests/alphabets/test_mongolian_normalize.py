"""Mongolian Normalisierung — Positionsform, FVS, Whitelist."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from alphabets.mongolian.map import CHAR_MONGOLIAN_SET
from alphabets.mongolian.normalize import normalize_mongolian
from alphabets.profiles import AlphabetProfile
from gpm_types.si.substance import substance_for_profile


class TestMongolianNormalize(unittest.TestCase):
    def test_isolated_forms_preserved(self) -> None:
        word = "\u1820\u1821\u1828"
        norm = normalize_mongolian(word)
        self.assertEqual(norm, word)
        substance_for_profile(norm, AlphabetProfile.MONGOLIAN)

    def test_fvs_ignored(self) -> None:
        with_fvs = "\u1820\u180B\u1821\u180C\u1828"
        norm = normalize_mongolian(with_fvs)
        self.assertEqual(norm, "\u1820\u1821\u1828")

    def test_zwj_zwnj_ignored(self) -> None:
        with_joiners = "\u1820\u200C\u1821\u200D\u1828"
        norm = normalize_mongolian(with_joiners)
        self.assertEqual(norm, "\u1820\u1821\u1828")

    def test_whitelist_airtight(self) -> None:
        polluted = "\u1820\u0041\u1821\u1828"
        norm = normalize_mongolian(polluted)
        self.assertEqual(norm, "\u1820\u1821\u1828")
        self.assertTrue(all(ch in CHAR_MONGOLIAN_SET for ch in norm))


if __name__ == "__main__":
    unittest.main()
