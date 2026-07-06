"""Härtungs-Invariante F-B — log_jaccard_basis_blend kanonisch."""

import unittest

from alphabets import AlphabetProfile
from analysis.algebra.fusion import log_jaccard_basis_blend
from analysis.algebra.window_fold import ExponentWindow, window_similarity


class TestLogJaccardBlend(unittest.TestCase):
    def test_window_similarity_uses_fusion_helper(self):
        a = ExponentWindow({2: 4, 3: 1})
        b = ExponentWindow({2: 3, 5: 2})
        score, _ = window_similarity(a, b, profile_a=AlphabetProfile.OG, profile_b=AlphabetProfile.OG)
        from analysis.algebra.log_profile import log_gcd_similarity, log_jaccard_primes

        ca = a.as_counter()
        cb = b.as_counter()
        expected = log_jaccard_basis_blend(log_gcd_similarity(ca, cb), log_jaccard_primes(ca, cb))
        self.assertAlmostEqual(score, expected)


if __name__ == "__main__":
    unittest.main()
