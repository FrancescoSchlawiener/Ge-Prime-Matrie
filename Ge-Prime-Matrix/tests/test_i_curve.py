import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from ge_prime.i_curve import (
    MAX_I_CURVE_TOKENS,
    RESPONSE_POINT_LIMIT,
    STRUCTURAL_CELL_TWIN_THRESHOLD,
    analyze_pair,
    compare_cell_geometry,
    compare_i_curves,
    downsample_curve_points,
    extract_cell_geometry,
    extract_i_curve_from_text,
    normalize_skeleton,
    skeleton_signature,
    summarize_curve,
    _cell_distance,
)
from gpm.compiler import compile_text


class TestICurve(unittest.TestCase):
    def test_i_curve_points_include_substance(self):
        curve = extract_i_curve_from_text("Hello world")
        for point in curve:
            self.assertIn("substance", point)
            self.assertGreaterEqual(point["substance"], 1)

    def test_cell_geometry_includes_kgv_fields(self):
        doc, _, _ = compile_text("One two three. Four five six.")
        cells = extract_cell_geometry(doc)
        self.assertGreater(len(cells), 0)
        self.assertIn("cell_substance", cells[0])
        self.assertIn("ggt_kgv_ratio", cells[1] if len(cells) > 1 else cells[0])

    def test_extract_length_matches_tokens(self):
        text = "The cat sat on the mat."
        curve = extract_i_curve_from_text(text)
        doc, _, stats = compile_text(text)
        self.assertEqual(len(curve), stats.total_tokens)
        self.assertEqual(summarize_curve(curve)["token_count"], len(curve))

    def test_i_ratio_in_unit_interval(self):
        curve = extract_i_curve_from_text("Hello world test")
        for point in curve:
            self.assertGreaterEqual(point["i_ratio"], 0.0)
            self.assertLessEqual(point["i_ratio"], 1.0)
            self.assertGreaterEqual(point["perm_index"], 1)
            self.assertGreaterEqual(point["perm_space"], 1)

    def test_identical_texts_high_geometry(self):
        text = "Der schnelle braune Fuchs springt."
        result = analyze_pair(text_a=text, text_b=text)
        cmp = result["comparison"]
        self.assertTrue(cmp["aligned"])
        self.assertGreaterEqual(cmp["geometry_score"], 0.99)
        self.assertAlmostEqual(cmp["geometry_score"], cmp["geometry_score_dtw"], places=3)
        self.assertGreaterEqual(cmp["literal_match_ratio"], 0.99)
        self.assertTrue(cmp["fester_offset_erkannt"])

    def test_word_geometry_dtw_primary_method(self):
        text = "Der schnelle braune Fuchs springt."
        cmp = analyze_pair(text_a=text, text_b=text)["comparison"]
        self.assertEqual(cmp["word_geometry"]["method"], "dtw_primary")

    def test_unrelated_texts_lower_geometry(self):
        result = analyze_pair(
            text_a="Alpha Beta Gamma Delta",
            text_b="Xylophon Zebra Quartz",
        )
        self.assertLess(result["comparison"]["geometry_score"], 0.85)

    def test_sliding_window_when_lengths_differ(self):
        short = extract_i_curve_from_text("One two three")
        long = extract_i_curve_from_text("One two three four five six")
        cmp = compare_i_curves(short, long)
        self.assertFalse(cmp["aligned"])
        self.assertGreaterEqual(cmp["best_offset"], 0)
        self.assertGreater(cmp["geometry_score"], 0.0)

    def test_token_limit_raises(self):
        words = " ".join(f"word{i}" for i in range(MAX_I_CURVE_TOKENS + 1))
        with self.assertRaises(ValueError):
            analyze_pair(text_a=words, text_b="hello")

    def test_snake_case_text_compiles(self):
        text = "hello_world foo_bar"
        result = analyze_pair(text_a=text, text_b=text)
        self.assertGreaterEqual(result["comparison"]["geometry_score"], 0.99)

    def test_normalize_skeleton_list_vs_tuple(self):
        a = {"skeleton": [3, 1, 1], "perm_index": 2, "perm_space": 6, "i_satz_ratio": 0.5}
        b = {"skeleton": (3, 1, 1), "perm_index": 2, "perm_space": 6, "i_satz_ratio": 0.5}
        self.assertEqual(normalize_skeleton([3, 1, 1]), normalize_skeleton((3, 1, 1)))
        self.assertEqual(skeleton_signature(a), skeleton_signature(b))
        self.assertEqual(_cell_distance(a, b), 0.0)

    def test_cell_distance_diff_perm_index(self):
        a = {"skeleton": [1, 2], "perm_index": 1, "perm_space": 2, "i_satz_ratio": 0.5}
        b = {"skeleton": [1, 2], "perm_index": 2, "perm_space": 2, "i_satz_ratio": 0.5}
        self.assertGreater(_cell_distance(a, b), 0.0)

    def test_identical_cells_match_count(self):
        text = "Der schnelle braune Fuchs springt. Er rennt schnell."
        doc, _, _ = compile_text(text)
        cells = extract_cell_geometry(doc)
        cmp = compare_cell_geometry(cells, cells)
        self.assertTrue(cmp["aligned"])
        self.assertEqual(cmp["match_count"], len(cells))
        self.assertGreaterEqual(cmp["geometry_score"], 0.99)
        self.assertEqual(cmp["method"], "dtw")

    def test_structural_cell_twins_synonym_replacement(self):
        original = "One two three four five six seven eight nine ten eleven twelve."
        synonym = "Alpha beta gamma delta epsilon zeta eta theta iota kappa lambda mu."
        result = analyze_pair(text_a=original, text_b=synonym)
        cmp = result["comparison"]
        cell_cmp = cmp["cell_geometry"]
        self.assertLess(cmp["literal_match_ratio"], 0.6)
        self.assertGreaterEqual(cell_cmp["geometry_score"], STRUCTURAL_CELL_TWIN_THRESHOLD)
        self.assertTrue(cmp["structural_cell_twins"])

    def test_insertion_dtw_beats_rigid_word_offset(self):
        base = "Eins zwei drei vier fünf sechs sieben acht neun zehn."
        inserted = "Eins zwei EXTRA drei vier fünf sechs sieben acht neun zehn."
        result = analyze_pair(text_a=base, text_b=inserted)
        word_cmp = result["comparison"]
        self.assertFalse(word_cmp["aligned"])
        self.assertIn("geometry_score_dtw", word_cmp)
        self.assertIn("word_geometry", word_cmp)
        self.assertEqual(word_cmp["word_geometry"]["method"], "dtw_primary")
        self.assertGreaterEqual(
            word_cmp["geometry_score_dtw"],
            word_cmp["geometry_score_mae"],
        )
        self.assertTrue(word_cmp["elastische_streckung"] is False)
        self.assertFalse(word_cmp["fester_offset_erkannt"])
        self.assertFalse(word_cmp["hybride_modifikation"])
        self.assertAlmostEqual(word_cmp["geometry_score"], word_cmp["geometry_score_dtw"], places=3)

    def test_analyze_pair_includes_substance_and_relation(self):
        text = "Der schnelle braune Fuchs springt."
        result = analyze_pair(text_a=text, text_b=text)
        self.assertIn("substance_geometry", result["comparison"])
        self.assertIn("relation_comparison", result)
        self.assertIn("substance_score", result["plagiarism_assessment"])

    def test_downsample_curve_points(self):
        points = [{"position": i, "i_ratio": i / 3000} for i in range(3000)]
        out = downsample_curve_points(points, limit=RESPONSE_POINT_LIMIT)
        stride = max(1, len(points) // RESPONSE_POINT_LIMIT)
        self.assertLessEqual(len(out), RESPONSE_POINT_LIMIT + 2)
        self.assertIs(out[0], points[0])
        self.assertIs(out[-1], points[-1])
        for i in range(1, len(out) - 1):
            self.assertNotEqual(out[i], out[i + 1])
        self.assertIn(points[stride], out)

    def _js_downsample_parity(self, points: list[dict], limit: int) -> list[dict]:
        """Repliziert downsampleSparklinePoints aus ikurve_lab.js."""
        if not points or len(points) <= limit:
            return points
        stride = max(1, len(points) // limit)
        out = [points[0]]
        for i in range(stride, len(points), stride):
            out.append(points[i])
        if out[-1] is not points[-1]:
            out.append(points[-1])
        deduped = [out[0]]
        for point in out[1:]:
            if point is not deduped[-1]:
                deduped.append(point)
        return deduped

    def test_downsample_curve_points_js_parity(self):
        points = [{"position": i, "i_ratio": i / 3000} for i in range(3000)]
        py_out = downsample_curve_points(points, limit=RESPONSE_POINT_LIMIT)
        js_out = self._js_downsample_parity(points, RESPONSE_POINT_LIMIT)
        self.assertEqual([p["position"] for p in py_out], [p["position"] for p in js_out])

    def test_sparkline_payload_tail_anchor(self):
        from ge_prime.config import API_PREVIEW_POINT_LIMIT
        from ge_prime.sparkline import build_preview_points

        points = [{"position": i} for i in range(100)]
        preview, truncated = build_preview_points(points, preview_limit=API_PREVIEW_POINT_LIMIT)
        self.assertTrue(truncated)
        self.assertEqual(len(preview), API_PREVIEW_POINT_LIMIT + 1)
        self.assertIs(preview[0], points[0])
        self.assertIs(preview[-1], points[-1])

    def test_sparkline_payload_no_duplicate_tail(self):
        from ge_prime.config import API_PREVIEW_POINT_LIMIT
        from ge_prime.sparkline import build_preview_points

        points = [{"position": i} for i in range(API_PREVIEW_POINT_LIMIT)]
        preview, truncated = build_preview_points(points, preview_limit=API_PREVIEW_POINT_LIMIT)
        self.assertFalse(truncated)
        self.assertEqual(len(preview), API_PREVIEW_POINT_LIMIT)
        self.assertIs(preview[-1], points[-1])

    def test_hierarchy_built_once_per_document(self):
        from unittest.mock import patch

        from ge_prime.hierarchy import build_document_hierarchy, extract_sentence_curve, get_hierarchy

        doc, _, _ = compile_text("One two three. Four five six.")
        doc.hierarchy = None
        doc.interval_index = None
        calls = 0
        original = build_document_hierarchy

        def counting(document):
            nonlocal calls
            calls += 1
            return original(document)

        with patch("ge_prime.hierarchy.build_document_hierarchy", side_effect=counting):
            get_hierarchy(doc)
            get_hierarchy(doc)
            extract_sentence_curve(doc)
        self.assertEqual(calls, 1)


if __name__ == "__main__":
    unittest.main()
