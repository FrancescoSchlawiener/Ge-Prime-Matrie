"""Tests für Sparkline-Downsampling."""

import unittest

from analysis.ui.sparkline import (
    build_preview_points,
    dedupe_neighbors,
    downsample_curve_points,
)


class TestSparkline(unittest.TestCase):
    PREVIEW_LIMIT = 50

    def test_dedupe_neighbors(self):
        a, b = {"x": 1}, {"x": 2}
        out = dedupe_neighbors([a, a, b, b])
        self.assertEqual(len(out), 2)
        self.assertIs(out[0], a)
        self.assertIs(out[1], b)

    def test_downsample_preserves_endpoints(self):
        points = [{"position": i} for i in range(100)]
        out = downsample_curve_points(points, limit=10)
        self.assertIs(out[0], points[0])
        self.assertIs(out[-1], points[-1])
        self.assertLessEqual(len(out), 12)

    def test_build_preview_tail_anchor(self):
        points = [{"position": i} for i in range(100)]
        preview, truncated = build_preview_points(points, preview_limit=self.PREVIEW_LIMIT)
        self.assertTrue(truncated)
        self.assertEqual(len(preview), self.PREVIEW_LIMIT + 1)
        self.assertIs(preview[0], points[0])
        self.assertIs(preview[-1], points[-1])

    def test_build_preview_no_duplicate_tail(self):
        points = [{"position": i} for i in range(self.PREVIEW_LIMIT)]
        preview, truncated = build_preview_points(points, preview_limit=self.PREVIEW_LIMIT)
        self.assertFalse(truncated)
        self.assertEqual(len(preview), self.PREVIEW_LIMIT)
        self.assertIs(preview[-1], points[-1])


if __name__ == "__main__":
    unittest.main()
