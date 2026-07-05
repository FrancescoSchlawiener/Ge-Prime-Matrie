import sys
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from permutation import perm_decode, perm_index, perm_fits_width, perm_space


class TestPermutation(unittest.TestCase):
    def test_papa_isst_papa(self):
        counts = Counter({0: 2, 1: 1})
        seq = [0, 1, 0]
        self.assertEqual(perm_space(counts), 3)
        self.assertEqual(perm_index(seq, counts), 2)
        self.assertEqual(perm_decode(counts, 2), seq)

    def test_roundtrip_all_indices(self):
        counts = Counter({0: 2, 1: 2, 2: 1})
        for i in range(1, perm_space(counts) + 1):
            seq = perm_decode(counts, i)
            self.assertEqual(perm_index(seq, counts), i)

    def test_perm_fits_width_og(self):
        self.assertTrue(perm_fits_width(60))
        self.assertTrue(perm_fits_width(1))


if __name__ == "__main__":
    unittest.main()
