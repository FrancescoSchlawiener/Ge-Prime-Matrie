"""Javanese Normalisierung — Pasangan, FVS, Whitelist."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from alphabets.javanese.map import CHAR_JAVANESE_SET
from alphabets.javanese.normalize import normalize_javanese
from alphabets.profiles import AlphabetProfile
from gpm_types.si.substance import substance_for_profile


class TestJavaneseNormalize(unittest.TestCase):
    def test_hanacaraka_core_preserved(self) -> None:
        word = "\uA992\uA993\uA994"
        norm = normalize_javanese(word)
        self.assertEqual(norm, word)
        substance_for_profile(norm, AlphabetProfile.JAVANESE)

    def test_pasangan_stripped(self) -> None:
        with_pasangan = "\uA992\uA9BC\uA993"
        norm = normalize_javanese(with_pasangan)
        self.assertEqual(norm, "\uA992\uA993")

    def test_wyanjana_stripped(self) -> None:
        with_vowel = "\uA992\uA9B4\uA993"
        norm = normalize_javanese(with_vowel)
        self.assertEqual(norm, "\uA992\uA993")

    def test_whitelist_airtight(self) -> None:
        polluted = "\uA992A\uA993"
        norm = normalize_javanese(polluted)
        self.assertEqual(norm, "\uA992\uA993")
        self.assertTrue(all(ch in CHAR_JAVANESE_SET for ch in norm))


if __name__ == "__main__":
    unittest.main()
