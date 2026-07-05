import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from sequence_key import Lut, Sk, Sp, sequence_key_via_lut
from substrate_og import S


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


if __name__ == "__main__":
    unittest.main()
