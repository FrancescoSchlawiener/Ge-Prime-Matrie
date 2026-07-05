"""SMP-Codepoint-Integrität für SMP-Alphabet-Profile."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from alphabets.aesthetic_hieroglyphs.normalize import normalize_aesthetic_hieroglyphs
from alphabets.gothic.normalize import normalize_gothic
from alphabets.old_italic.normalize import normalize_old_italic
from alphabets.old_persian.normalize import normalize_old_persian
from alphabets.old_turkic.normalize import normalize_old_turkic
from alphabets.phoenician.normalize import normalize_phoenician
from alphabets.profiles import AlphabetProfile
from alphabets.ugaritic.normalize import normalize_ugaritic
from alphabets.unicode_utils import SurrogateCodepointError
from gpm_types.si.substance import substance_for_profile


class TestSmpCodepoints(unittest.TestCase):
    def test_phoenician_atomic_codepoints(self) -> None:
        raw = "\U00010901\U00010913\U00010914"
        norm = normalize_phoenician(raw)
        self.assertEqual(len(norm), 3)
        for ch in norm:
            self.assertGreaterEqual(ord(ch), 0x10000)
            self.assertNotIn(ord(ch), range(0xD800, 0xE000))
        substance_for_profile(norm, AlphabetProfile.PHOENICIAN)

    def test_ugaritic_atomic_codepoints(self) -> None:
        raw = "\U00010381\U00010393\U00010394"
        norm = normalize_ugaritic(raw)
        self.assertEqual(len(norm), 3)
        for ch in norm:
            self.assertGreaterEqual(ord(ch), 0x10000)
        substance_for_profile(norm, AlphabetProfile.UGARITIC)

    def test_gothic_atomic_codepoints(self) -> None:
        raw = "\U00010331\U00010342\U00010343"
        norm = normalize_gothic(raw)
        self.assertEqual(len(norm), 3)
        for ch in norm:
            self.assertGreaterEqual(ord(ch), 0x10000)
        substance_for_profile(norm, AlphabetProfile.GOTHIC)

    def test_whitelist_no_fragmentation(self) -> None:
        lone_surrogate = "\uD800"
        with self.assertRaises(SurrogateCodepointError):
            normalize_phoenician("a" + lone_surrogate)

    def test_old_persian_atomic_codepoints(self) -> None:
        raw = "\U000103A0\U000103A1\U000103A2"
        norm = normalize_old_persian(raw)
        self.assertEqual(len(norm), 3)
        for ch in norm:
            self.assertGreaterEqual(ord(ch), 0x10000)
        substance_for_profile(norm, AlphabetProfile.OLD_PERSIAN)

    def test_old_italic_atomic_codepoints(self) -> None:
        raw = "\U00010300\U00010301\U00010302"
        norm = normalize_old_italic(raw)
        self.assertEqual(len(norm), 3)
        for ch in norm:
            self.assertGreaterEqual(ord(ch), 0x10000)
        substance_for_profile(norm, AlphabetProfile.OLD_ITALIC)

    def test_old_turkic_atomic_codepoints(self) -> None:
        raw = "\U00010C00\U00010C01\U00010C02"
        norm = normalize_old_turkic(raw)
        self.assertEqual(len(norm), 3)
        for ch in norm:
            self.assertGreaterEqual(ord(ch), 0x10000)
        substance_for_profile(norm, AlphabetProfile.OLD_TURKIC)

    def test_aesthetic_hieroglyphs_atomic_codepoints(self) -> None:
        raw = "\U00013196\U0001308B\U0001313F"
        norm = normalize_aesthetic_hieroglyphs(raw)
        self.assertEqual(len(norm), 3)
        for ch in norm:
            self.assertGreaterEqual(ord(ch), 0x10000)
        substance_for_profile(norm, AlphabetProfile.AESTHETIC_HIEROGLYPHS)


if __name__ == "__main__":
    unittest.main()
