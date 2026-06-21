"""Python-Parity für Zone-2-Sparkline-Layout (app.js resolveSparklineEnd / computePairedChartLayout)."""

from __future__ import annotations

import unittest


def resolve_sparkline_end(points, index_key, point_count=None):
    if point_count is not None and point_count > 0:
        return point_count - 1
    if not points:
        return 0
    return max(p.get(index_key, 0) for p in points)


def compute_paired_chart_layout(end_a, end_b, chart_scale, span_a=0, span_b=0):
    def safe_max(end):
        return max(end, 1)

    def union_layout(max_index):
        safe = safe_max(max_index)
        return {
            "a": {"maxIndex": safe, "scrollable": False, "widthRatio": 1},
            "b": {"maxIndex": safe, "scrollable": False, "widthRatio": 1},
        }

    if span_a <= 0 and span_b <= 0:
        return union_layout(1)
    if chart_scale == "shorter" and span_a > 0 and span_b > 0 and span_a != span_b:
        width_ratio = max(span_a, span_b) / min(span_a, span_b)
        if span_a < span_b:
            return {
                "a": {"maxIndex": safe_max(end_a), "scrollable": False, "widthRatio": 1},
                "b": {"maxIndex": safe_max(end_b), "scrollable": True, "widthRatio": width_ratio},
            }
        return {
            "a": {"maxIndex": safe_max(end_a), "scrollable": True, "widthRatio": width_ratio},
            "b": {"maxIndex": safe_max(end_b), "scrollable": False, "widthRatio": 1},
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
        layout = compute_paired_chart_layout(50, 120, "shorter", 51, 121)
        self.assertFalse(layout["a"]["scrollable"])
        self.assertTrue(layout["b"]["scrollable"])
        self.assertEqual(layout["a"]["maxIndex"], 50)
        self.assertEqual(layout["b"]["maxIndex"], 120)
        self.assertAlmostEqual(layout["b"]["widthRatio"], 121 / 51)

    def test_shorter_scale_scroll_on_a_when_a_longer(self):
        layout = compute_paired_chart_layout(200, 80, "shorter", 201, 81)
        self.assertTrue(layout["a"]["scrollable"])
        self.assertFalse(layout["b"]["scrollable"])
        self.assertAlmostEqual(layout["a"]["widthRatio"], 201 / 81)

    def test_shorter_equal_length_no_scroll(self):
        layout = compute_paired_chart_layout(40, 40, "shorter", 41, 41)
        self.assertFalse(layout["a"]["scrollable"])
        self.assertFalse(layout["b"]["scrollable"])
        self.assertEqual(layout["a"]["maxIndex"], 40)
        self.assertEqual(layout["b"]["maxIndex"], 40)

    def test_union_never_scrolls(self):
        layout = compute_paired_chart_layout(50, 120, "union", 51, 121)
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
        layout = compute_paired_chart_layout(end_a, end_b, "shorter", 200, 50)
        self.assertTrue(layout["a"]["scrollable"])
        self.assertFalse(layout["b"]["scrollable"])

    def test_shorter_scale_single_line_vs_many(self):
        """Raum > Zeile: 1 Zeile (end=0) vs 20 Zeilen — kürzere Seite ohne Scroll."""
        layout = compute_paired_chart_layout(0, 19, "shorter", 1, 20)
        self.assertFalse(layout["a"]["scrollable"])
        self.assertTrue(layout["b"]["scrollable"])
        self.assertEqual(layout["a"]["maxIndex"], 1)
        self.assertAlmostEqual(layout["b"]["widthRatio"], 20.0)

    def test_union_single_line_max_index_safe(self):
        layout = compute_paired_chart_layout(0, 0, "union", 1, 1)
        self.assertEqual(layout["a"]["maxIndex"], 1)
        self.assertEqual(layout["b"]["maxIndex"], 1)


if __name__ == "__main__":
    unittest.main()
