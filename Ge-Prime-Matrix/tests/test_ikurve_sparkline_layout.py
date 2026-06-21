"""Python-Parity für Zone-2-Sparkline-Layout (app.js resolveSparklineEnd / computePairedChartLayout)."""

from __future__ import annotations

import unittest


def resolve_sparkline_end(points, index_key, point_count=None):
    if point_count is not None and point_count > 0:
        return point_count - 1
    if not points:
        return 0
    return max(p.get(index_key, 0) for p in points)


def compute_paired_chart_layout(end_a, end_b, chart_scale):
    def union_layout(max_index):
        return {
            "a": {"maxIndex": max_index, "scrollable": False, "widthRatio": 1},
            "b": {"maxIndex": max_index, "scrollable": False, "widthRatio": 1},
        }

    if end_a <= 0 and end_b <= 0:
        return union_layout(1)
    if chart_scale == "shorter" and end_a > 0 and end_b > 0 and end_a != end_b:
        short_end = min(end_a, end_b)
        long_end = max(end_a, end_b)
        width_ratio = long_end / short_end
        if end_a < end_b:
            return {
                "a": {"maxIndex": end_a, "scrollable": False, "widthRatio": 1},
                "b": {"maxIndex": end_b, "scrollable": True, "widthRatio": width_ratio},
            }
        return {
            "a": {"maxIndex": end_a, "scrollable": True, "widthRatio": width_ratio},
            "b": {"maxIndex": end_b, "scrollable": False, "widthRatio": 1},
        }
    return union_layout(max(end_a, end_b, 1))


class TestIcurveSparklineLayout(unittest.TestCase):
    def test_extent_prefers_point_count(self):
        preview = [{"position": i} for i in range(30)]
        self.assertEqual(resolve_sparkline_end(preview, "position", 200), 199)

    def test_extent_max_index_in_points_without_count(self):
        points = [{"sentence_index": 0}, {"sentence_index": 5}, {"sentence_index": 3}]
        self.assertEqual(resolve_sparkline_end(points, "sentence_index", None), 5)

    def test_extent_empty_points(self):
        self.assertEqual(resolve_sparkline_end([], "position", None), 0)

    def test_shorter_scale_scroll_on_b_when_b_longer(self):
        layout = compute_paired_chart_layout(50, 120, "shorter")
        self.assertFalse(layout["a"]["scrollable"])
        self.assertTrue(layout["b"]["scrollable"])
        self.assertEqual(layout["a"]["maxIndex"], 50)
        self.assertEqual(layout["b"]["maxIndex"], 120)
        self.assertAlmostEqual(layout["b"]["widthRatio"], 120 / 50)

    def test_shorter_scale_scroll_on_a_when_a_longer(self):
        layout = compute_paired_chart_layout(200, 80, "shorter")
        self.assertTrue(layout["a"]["scrollable"])
        self.assertFalse(layout["b"]["scrollable"])
        self.assertAlmostEqual(layout["a"]["widthRatio"], 200 / 80)

    def test_shorter_equal_length_no_scroll(self):
        layout = compute_paired_chart_layout(40, 40, "shorter")
        self.assertFalse(layout["a"]["scrollable"])
        self.assertFalse(layout["b"]["scrollable"])
        self.assertEqual(layout["a"]["maxIndex"], 40)
        self.assertEqual(layout["b"]["maxIndex"], 40)

    def test_union_never_scrolls(self):
        layout = compute_paired_chart_layout(50, 120, "union")
        self.assertFalse(layout["a"]["scrollable"])
        self.assertFalse(layout["b"]["scrollable"])
        self.assertEqual(layout["a"]["maxIndex"], 120)
        self.assertEqual(layout["b"]["maxIndex"], 120)

    def test_preview_fallback_extent_bug_regression(self):
        preview_a = [{"position": i} for i in range(30)]
        end_a = resolve_sparkline_end(preview_a, "position", 200)
        end_b = resolve_sparkline_end([{"position": 49}], "position", 50)
        self.assertEqual(end_a, 199)
        self.assertEqual(end_b, 49)
        layout = compute_paired_chart_layout(end_a, end_b, "shorter")
        self.assertTrue(layout["a"]["scrollable"])
        self.assertFalse(layout["b"]["scrollable"])


if __name__ == "__main__":
    unittest.main()
