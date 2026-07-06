"""Blocker-Tests — Härtungs-Invariante D-A (sparse_counter O(k))."""

import unittest
from collections import Counter

from analysis.algebra.sparse_counter import counter_cosine, counter_jaccard, counter_overlap


class TestSparseCounterInvariants(unittest.TestCase):
    def test_cosine_disjoint_keys_zero(self):
        a = Counter({2: 100, 3: 50})
        b = Counter({97: 200, 101: 80})
        self.assertEqual(counter_cosine(a, b), 0.0)

    def test_cosine_intersection_only_dot(self):
        a = Counter({2: 3, 5: 1})
        b = Counter({2: 1, 5: 4, 7: 99})
        dot = 3 * 1 + 1 * 4
        norm_a = 9 + 1
        norm_b = 1 + 16 + 9801
        import math

        expected = dot / math.sqrt(norm_a * norm_b)
        self.assertAlmostEqual(counter_cosine(a, b), min(1.0, expected), places=6)

    def test_jaccard_o_k(self):
        a = Counter({2: 2, 3: 1})
        b = Counter({2: 1, 3: 3})
        inter = min(2, 1) + min(1, 3)
        union = max(2, 1) + max(1, 3)
        self.assertAlmostEqual(counter_jaccard(a, b), inter / union, places=6)

    def test_overlap_matches_profile_semantics(self):
        a = Counter({2: 4, 3: 2})
        b = Counter({2: 2, 3: 2})
        inter = 2 + 2
        denom = min(6, 4)
        self.assertAlmostEqual(counter_overlap(a, b), inter / denom, places=6)


if __name__ == "__main__":
    unittest.main()
