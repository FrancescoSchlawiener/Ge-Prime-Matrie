"""Golden regression tests for DTW — window deadlock, score invariants."""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from ge_prime.dtw import adaptive_window, dtw_similarity
from ge_prime.i_curve import (
    STRUCTURAL_CELL_TWIN_THRESHOLD,
    analyze_pair,
    compare_cell_geometry,
    compare_i_curves,
    extract_cell_geometry,
    extract_i_curve_from_text,
    extract_substance_curve,
)
from ge_prime.substance_align import compare_substance_sequences
from gpm.compiler import compile_text


def _log_failure(cmp: dict, label: str) -> str:
    return (
        f"{label}: geometry={cmp.get('geometry_score')} "
        f"dtw_cost={cmp.get('dtw_cost')} dtw_failed={cmp.get('dtw_failed')} "
        f"dtw_window={cmp.get('dtw_window')} "
        f"mae={cmp.get('geometry_score_mae')} dtw={cmp.get('geometry_score_dtw')}"
    )


class TestDtwRegression(unittest.TestCase):
    def test_adaptive_window_covers_length_mismatch(self):
        window = adaptive_window(100, 50)
        self.assertGreaterEqual(window, abs(100 - 50))

    def test_length_extreme_no_deadlock(self):
        seq_a = [{"position": i, "i_ratio": 0.5, "substance": 30, "delta_ratio": 0.0} for i in range(100)]
        seq_b = [{"position": i, "i_ratio": 0.5, "substance": 30, "delta_ratio": 0.0} for i in range(50)]
        cmp = compare_i_curves(seq_a, seq_b)
        self.assertFalse(cmp["dtw_failed"], _log_failure(cmp, "word"))
        self.assertIsNotNone(cmp["dtw_cost"])

    def test_identical_german_high_word_dtw(self):
        text = "Der schnelle braune Fuchs springt."
        result = analyze_pair(text_a=text, text_b=text)
        cmp = result["comparison"]
        self.assertFalse(cmp["dtw_failed"], _log_failure(cmp, "identical"))
        self.assertGreaterEqual(cmp["geometry_score_dtw"], 0.99)
        subst = cmp["substance_geometry"]
        self.assertFalse(subst["dtw_failed"])
        self.assertGreaterEqual(subst["geometry_score"], 0.99)

    def test_insertion_word_dtw_not_zero(self):
        base = "Eins zwei drei vier fünf sechs sieben acht neun zehn."
        inserted = "Eins zwei EXTRA drei vier fünf sechs sieben acht neun zehn."
        cmp = analyze_pair(text_a=base, text_b=inserted)["comparison"]
        self.assertFalse(cmp["dtw_failed"], _log_failure(cmp, "insertion"))
        self.assertGreater(cmp["geometry_score_dtw"], 0.5)

    def test_cell_twins_high_cell_dtw_low_literal(self):
        original = "One two three four five six seven eight nine ten eleven twelve."
        synonym = "Alpha beta gamma delta epsilon zeta eta theta iota kappa lambda mu."
        result = analyze_pair(text_a=original, text_b=synonym)
        cmp = result["comparison"]
        cell = cmp["cell_geometry"]
        self.assertFalse(cell["dtw_failed"], _log_failure(cell, "cell_twins"))
        self.assertGreaterEqual(cell["geometry_score"], 0.75)
        self.assertLess(cmp["literal_match_ratio"], 0.6)

    def test_substance_parallel_listen_silent(self):
        doc_a, _, _ = compile_text("Listen Silent")
        doc_b, _, _ = compile_text("Silent Listen")
        seq_a = extract_substance_curve(doc_a)
        seq_b = extract_substance_curve(doc_b)
        cmp = compare_substance_sequences(seq_a, seq_b, literal_match_ratio=0.0)
        self.assertFalse(cmp["dtw_failed"])
        self.assertGreaterEqual(cmp["geometry_score"], 0.75)

    def test_unrelated_not_failed_but_lower_scores(self):
        result = analyze_pair(
            text_a="Alpha Beta Gamma",
            text_b="Xylophon Zebra",
        )
        cmp = result["comparison"]
        self.assertFalse(cmp["dtw_failed"], _log_failure(cmp, "unrelated"))
        self.assertLess(cmp["geometry_score"], 0.85)

    def test_dtw_module_legacy_window_can_fail(self):
        seq_a = [{"v": i} for i in range(100)]
        seq_b = [{"v": i} for i in range(50)]
        legacy = dtw_similarity(seq_a, seq_b, lambda a, b: abs(a["v"] - b["v"]) / 100, window_mode="legacy")
        adaptive = dtw_similarity(seq_a, seq_b, lambda a, b: abs(a["v"] - b["v"]) / 100, window_mode="adaptive")
        self.assertTrue(legacy.failed)
        self.assertFalse(adaptive.failed)

    def test_empty_curves_mark_failed(self):
        cmp = compare_i_curves([], [])
        self.assertTrue(cmp["dtw_failed"])
        cell = compare_cell_geometry([], [])
        self.assertTrue(cell["dtw_failed"])


if __name__ == "__main__":
    unittest.main()
