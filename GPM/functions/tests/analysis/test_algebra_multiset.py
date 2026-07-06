"""Tests für analysis/algebra/multiset.py."""

import unittest

from alphabets import AlphabetProfile
from analysis.algebra.multiset import anagram_class_key, perm_compatible
from gpm_types.si.codec import encode_si


class TestAlgebraMultiset(unittest.TestCase):
    def test_anagram_class_key_stable(self):
        s, _ = encode_si("LISTEN", AlphabetProfile.OG)
        k1 = anagram_class_key(s, AlphabetProfile.OG)
        k2 = anagram_class_key(s, AlphabetProfile.OG)
        self.assertEqual(k1, k2)

    def test_perm_compatible_same_word(self):
        s, _ = encode_si("ABC", AlphabetProfile.OG)
        self.assertTrue(perm_compatible(s, s, AlphabetProfile.OG))


if __name__ == "__main__":
    unittest.main()
