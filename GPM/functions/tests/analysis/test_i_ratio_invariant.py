"""Härtungs-Invariante E-B — i_ratio_similarity Guard und [0,1]-Range."""

import unittest

from analysis.algebra.i_metrics import i_ratio_distance, i_ratio_similarity


class TestIRatioInvariant(unittest.TestCase):
    def test_guard_clamps_out_of_range(self):
        self.assertEqual(i_ratio_similarity(1.5, 0.0), 0.0)

    def test_identical_ratios(self):
        self.assertAlmostEqual(i_ratio_similarity(0.3, 0.3), 1.0)

    def test_symmetry(self):
        self.assertEqual(i_ratio_similarity(0.2, 0.7), i_ratio_similarity(0.7, 0.2))

    def test_distance_complement(self):
        a, b = 0.4, 0.9
        self.assertAlmostEqual(i_ratio_distance(a, b), abs(a - b))

    def test_range_bounded(self):
        for a in (0.0, 0.25, 0.5, 1.0, 1.5):
            for b in (0.0, 0.33, 0.66, 1.0, 2.0):
                sim = i_ratio_similarity(a, b)
                self.assertGreaterEqual(sim, 0.0)
                self.assertLessEqual(sim, 1.0)


if __name__ == "__main__":
    unittest.main()
