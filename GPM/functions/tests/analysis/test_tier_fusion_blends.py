"""F-B — Structure/Curve-Tier über fusion.py."""

import unittest

from analysis.algebra.fusion import (
    WEIGHTS_CURVE_TIER,
    WEIGHTS_STRUCTURE_TIER,
    fuse_curve_tier,
    fuse_structure_tier,
    fuse_weighted_scores,
)


class TestTierFusionBlends(unittest.TestCase):
    def test_structure_tier_weights(self):
        score = fuse_structure_tier(0.8, 0.6, True)
        expected = fuse_weighted_scores(
            {"meta": 0.8, "relation": 0.6, "bitmask": 1.0},
            WEIGHTS_STRUCTURE_TIER,
        )
        self.assertAlmostEqual(score, expected)

    def test_curve_tier_weights(self):
        score = fuse_curve_tier(0.7, 0.5)
        expected = fuse_weighted_scores(
            {"i_curve": 0.7, "substance": 0.5},
            WEIGHTS_CURVE_TIER,
        )
        self.assertAlmostEqual(score, expected)


if __name__ == "__main__":
    unittest.main()
