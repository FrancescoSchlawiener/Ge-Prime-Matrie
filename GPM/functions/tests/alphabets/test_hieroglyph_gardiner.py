"""Gardiner-Map und Logogramm-Leak-Verbot für Aesthetic Hieroglyphs."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from alphabets.aesthetic_hieroglyphs.gardiner_map import GLYPH_TO_UNILITERAL
from alphabets.aesthetic_hieroglyphs.map import CHAR_AESTHETIC_HIEROGLYPHS_SET
from alphabets.aesthetic_hieroglyphs.normalize import normalize_aesthetic_hieroglyphs
from alphabets.profiles import AlphabetProfile
from alphabets.registry import prime_map_for_profile
from gpm_types.si.substance import substance_for_profile

_N = "\U00013196"
_R = "\U0001308B"
_A = "\U0001313F"
# Gebäude-Logogramm (nicht uniliteral, nicht in Gardiner-Map)
_IDEOGRAM = "\U00013211"


class TestHieroglyphGardiner(unittest.TestCase):
    def test_gardiner_variant_maps_to_uniliteral(self) -> None:
        variant = "\U00013197"
        self.assertIn(variant, GLYPH_TO_UNILITERAL)
        norm = normalize_aesthetic_hieroglyphs(variant)
        self.assertEqual(norm, _N)

    def test_ideogram_silently_discarded(self) -> None:
        norm = normalize_aesthetic_hieroglyphs(_IDEOGRAM)
        self.assertEqual(norm, "")

    def test_mixed_input_only_uniliterals_remain(self) -> None:
        variant = "\U00013197"
        raw = _A + _IDEOGRAM + variant + _R
        norm = normalize_aesthetic_hieroglyphs(raw)
        self.assertEqual(norm, _A + _N + _R)
        self.assertEqual(len(norm), 3)

    def test_no_logogram_leak_in_substance(self) -> None:
        norm = normalize_aesthetic_hieroglyphs(_A + _IDEOGRAM + _N)
        prime_map = prime_map_for_profile(AlphabetProfile.AESTHETIC_HIEROGLYPHS)
        self.assertTrue(all(ch in prime_map for ch in norm))
        substance_for_profile(norm, AlphabetProfile.AESTHETIC_HIEROGLYPHS)

    def test_unmapped_glyph_never_passes_through(self) -> None:
        unmapped = "\U00013001"
        self.assertNotIn(unmapped, CHAR_AESTHETIC_HIEROGLYPHS_SET)
        self.assertNotIn(unmapped, GLYPH_TO_UNILITERAL)
        norm = normalize_aesthetic_hieroglyphs(_A + unmapped + _R)
        self.assertEqual(norm, _A + _R)


if __name__ == "__main__":
    unittest.main()
