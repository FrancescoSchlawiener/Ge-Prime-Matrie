"""Tests für offset classifiers und tier fusion."""

import unittest

from analysis.algebra.offset import classify_structural_offset, structural_twin_key
from analysis.algebra.tier_fusion import fuse_tier_scores


class TestOffsetAndFusion(unittest.TestCase):
    def test_rigid_offset(self):
        self.assertEqual(classify_structural_offset(0.9, 0.9), "rigid")

    def test_elastic_offset(self):
        self.assertEqual(classify_structural_offset(0.3, 0.9), "elastic")

    def test_twin_key(self):
        key = structural_twin_key((1, 2, 1), 3, 6)
        self.assertEqual(key, ((1, 2, 1), 3, 6))

    def test_fusion_respects_zero_reason(self):
        self.assertEqual(
            fuse_tier_scores(basis=0.5, structure=0.8, curve=0.9, zero_reason="gate"),
            0.5,
        )

    def test_fusion_additive(self):
        fused = fuse_tier_scores(basis=0.4, structure=0.6, curve=0.8)
        self.assertGreater(fused, 0.4)
        self.assertLessEqual(fused, 1.0)


if __name__ == "__main__":
    unittest.main()
