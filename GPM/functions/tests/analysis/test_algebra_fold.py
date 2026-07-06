"""Tests für analysis/algebra/fold.py."""

import math
import unittest

from alphabets import AlphabetProfile
from analysis.algebra.fold import fold_gcd, fold_lcm, fold_lcm_span, passes_kgv_gate
from analysis.binary.search import search_by_lcm
from analysis.compile.compiler import compile_text


class TestAlgebraFold(unittest.TestCase):
    def test_fold_lcm_matches_search(self):
        doc, _ = compile_text("LISTEN LISTEN", AlphabetProfile.OG)
        folded = fold_lcm([doc.header[0].substance, doc.header[0].substance])
        result = search_by_lcm(doc, "LISTEN", "LISTEN")
        self.assertEqual(folded, result["lcm_value"])

    def test_fold_gcd(self):
        self.assertEqual(fold_gcd([12, 18, 24]), math.gcd(12, math.gcd(18, 24)))

    def test_fold_lcm_span(self):
        self.assertEqual(fold_lcm_span([2, 3, 4]), fold_lcm([2, 3, 4]))

    def test_passes_kgv_gate(self):
        self.assertTrue(passes_kgv_gate(12, 3))
        self.assertFalse(passes_kgv_gate(10, 3))
        self.assertTrue(passes_kgv_gate(5, 1))


if __name__ == "__main__":
    unittest.main()
