import sys
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from alpha_roman import ALPHA_ROMAN_LEX_ORDER
from perm_lut import (
    ALPHA_ROMAN_SINGLETON_LUTS,
    MAX_LUT_BUILD_LENGTH,
    build_permutation_lut,
    get_permutation_lut,
)
from permutation import perm_index


class TestPermLut(unittest.TestCase):
    def test_hallo_lut_size(self):
        lut = build_permutation_lut(Counter("HALLO"))
        self.assertEqual(lut.perm_space, 60)

    def test_hallo_lut_matches_perm_index(self):
        seq = "HALLO"
        lut = get_permutation_lut(Counter(seq))
        self.assertEqual(lut.index_of(seq), perm_index(list(seq), Counter(seq)))

    def test_singleton_luts_27(self):
        self.assertEqual(len(ALPHA_ROMAN_SINGLETON_LUTS), 27)
        for sym in ALPHA_ROMAN_LEX_ORDER:
            self.assertEqual(ALPHA_ROMAN_SINGLETON_LUTS[sym].entries, (sym,))

    def test_max_lut_build_length_blocks_large(self):
        counts = Counter({chr(65 + i): 1 for i in range(MAX_LUT_BUILD_LENGTH + 1)})
        with self.assertRaises(ValueError):
            build_permutation_lut(counts)


if __name__ == "__main__":
    unittest.main()
