"""Tests für profil-aware Substanz-Vergleiche."""

import unittest

from alphabets import AlphabetProfile
from analysis.substance.compare import (
    compare_substances,
    substance_ggt_kgv_similarity,
)
from gpm_types.si import encode_si


class TestSubstanceCompare(unittest.TestCase):
    def setUp(self):
        self.profile = AlphabetProfile.OG

    def test_listen_silent_anagram_similarity(self):
        s1, _ = encode_si("LISTEN", self.profile)
        s2, _ = encode_si("SILENT", self.profile)
        self.assertEqual(s1, s2)
        sim = substance_ggt_kgv_similarity(s1, s2)
        self.assertAlmostEqual(sim, 1.0, places=6)

    def test_compare_substances_fields(self):
        s1, _ = encode_si("LISTEN", self.profile)
        s2, _ = encode_si("SILENT", self.profile)
        result = compare_substances(s1, s2, self.profile)
        self.assertEqual(result["gcd_value"], s1)
        self.assertEqual(result["lcm_value"], s1)
        self.assertAlmostEqual(result["ggt_kgv_similarity"], 1.0, places=6)

    def test_different_words_partial_overlap(self):
        s1, _ = encode_si("HALLO", self.profile)
        s2, _ = encode_si("OLLAH", self.profile)
        self.assertEqual(s1, s2)
        sim = substance_ggt_kgv_similarity(s1, s2)
        self.assertAlmostEqual(sim, 1.0, places=6)


if __name__ == "__main__":
    unittest.main()
