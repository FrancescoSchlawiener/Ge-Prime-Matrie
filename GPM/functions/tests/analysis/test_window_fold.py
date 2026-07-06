"""Tests für window_fold — ExponentWindow und Guard."""

import unittest

from alphabets import AlphabetProfile
from analysis.algebra.window_fold import ExponentWindow, fold_window_from_token_exponents, window_similarity
from analysis.compile.compiler import compile_text
from analysis.index.substance_index import build_substance_index, window_fingerprint


class TestWindowFold(unittest.TestCase):
    def test_covers_partial_order(self):
        big = ExponentWindow({2: 3, 5: 2})
        small = ExponentWindow({2: 1, 5: 1})
        self.assertTrue(big.covers(small))
        self.assertFalse(small.covers(big))

    def test_fold_max_lcm_direction(self):
        a = ExponentWindow({2: 1, 3: 2})
        b = ExponentWindow({2: 3, 5: 1})
        merged = a.fold_max(b)
        self.assertEqual(merged.exponents[2], 3)
        self.assertEqual(merged.exponents[3], 2)
        self.assertEqual(merged.exponents[5], 1)

    def test_substance_index_uses_algebra_fold(self):
        doc, _ = compile_text("Hallo Welt", AlphabetProfile.OG)
        idx = build_substance_index(doc)
        fp = window_fingerprint(idx, 0, len(doc.tokens))
        self.assertIsInstance(fp, ExponentWindow)

    def test_window_similarity_same_doc(self):
        doc, _ = compile_text("Alpha Beta", AlphabetProfile.OG)
        idx = build_substance_index(doc)
        w = window_fingerprint(idx, 0, 2)
        score, reason = window_similarity(
            w,
            w,
            profile_a=AlphabetProfile.OG,
            profile_b=AlphabetProfile.OG,
        )
        self.assertIsNone(reason)
        self.assertGreater(score, 0.0)


if __name__ == "__main__":
    unittest.main()
