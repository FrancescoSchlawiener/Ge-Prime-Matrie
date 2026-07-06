"""Blocker-Tests — Härtungs-Invariante D-B (I×S-Kopplung)."""

import unittest

from analysis.algebra.substance_kernel import coupled_point_distance, coupled_point_similarity


class TestCoupledInvariants(unittest.TestCase):
    def test_substance_collapse_zero(self):
        self.assertEqual(coupled_point_similarity(1.0, 0.0), 0.0)
        self.assertEqual(coupled_point_similarity(0.99, 0.0), 0.0)

    def test_both_zero(self):
        self.assertEqual(coupled_point_similarity(0.0, 0.0), 0.0)

    def test_multiplicative(self):
        self.assertAlmostEqual(coupled_point_similarity(0.8, 0.5), 0.4, places=6)

    def test_distance_complement(self):
        self.assertAlmostEqual(
            coupled_point_distance(0.8, 0.5),
            1.0 - coupled_point_similarity(0.8, 0.5),
            places=6,
        )

    def test_substance_zero_distance_one(self):
        self.assertEqual(coupled_point_distance(1.0, 0.0), 1.0)


if __name__ == "__main__":
    unittest.main()
