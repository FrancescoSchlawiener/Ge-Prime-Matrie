import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from sequence_key import Lut, Sk, Sk_lut, Sp, sequence_key_via_lut
from substrate_og import S
from alphabets.profiles import AlphabetProfile
from gpm_types.si.codec import permutation_index_for_profile
from tools.benchmark_patterns import build_unique
from alphabets.lex import lex_order_for_profile
from perm.lut import get_permutation_lut, lut_index_of_sequence
from collections import Counter


class TestSequenceKey(unittest.TestCase):
    def test_sk_differs_for_permutations(self):
        self.assertNotEqual(Sk("ABC"), Sk("CBA"))

    def test_sp_differs_for_anagrams(self):
        self.assertNotEqual(Sp("ABC"), Sp("CBA"))

    def test_sp_not_equal_commutative_s(self):
        self.assertEqual(S("ABC"), S("CBA"))
        self.assertNotEqual(Sp("ABC"), Sp("CBA"))

    def test_lut_size_hallo(self):
        self.assertEqual(Lut("HALLO").perm_space, 60)

    def test_sequence_key_via_lut(self):
        lut, idx = sequence_key_via_lut("HALLO")
        self.assertEqual(lut.sequence_at(idx), "HALLO")

    def test_sequence_key_via_lut_roman_default(self):
        _, idx_default = sequence_key_via_lut("HALLO")
        _, idx_roman = sequence_key_via_lut("HALLO", AlphabetProfile.ROMAN)
        self.assertEqual(idx_default, idx_roman)

    def test_sk_lut_matches_substrate(self):
        self.assertEqual(Sk_lut("HALLO"), tuple("HALLO"))

    def test_lut_index_matches_perm_index_hallo(self):
        seq = "HALLO"
        idx_lut = sequence_key_via_lut(seq, AlphabetProfile.ROMAN)[1]
        idx_perm = permutation_index_for_profile(seq, AlphabetProfile.ROMAN)
        self.assertEqual(idx_lut, idx_perm)

    def test_greek_profile_lex_differs_from_codepoint_fallback(self):
        profile = AlphabetProfile.GREEK
        seq = build_unique(lex_order_for_profile(profile), 3)
        lut_fallback = get_permutation_lut(Counter(seq))
        idx_fallback = lut_index_of_sequence(lut_fallback, seq)
        idx_profile = sequence_key_via_lut(seq, profile)[1]
        self.assertNotEqual(idx_fallback, idx_profile)


if __name__ == "__main__":
    unittest.main()
