import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from ge_prime.compare import substance_log_distance, substance_log_similarity
from ge_prime.substance_align import (
    compare_substance_sequences,
    extract_substance_curve,
)
from gpm.compiler import compile_text


class TestSubstanceAlign(unittest.TestCase):
    def test_extract_curve_has_ggt_kgv_fields(self):
        doc, _, _ = compile_text("Alpha Beta Gamma")
        curve = extract_substance_curve(doc)
        self.assertEqual(len(curve), 3)
        self.assertEqual(curve[0]["ggt_kgv_ratio"], 0.0)
        self.assertEqual(curve[0]["s_ratio"], 0.0)
        self.assertIn("ggt", curve[1])
        self.assertIn("kgv", curve[1])
        self.assertGreaterEqual(curve[1]["ggt_kgv_ratio"], 0.0)
        self.assertEqual(curve[1]["ggt_kgv_ratio"], curve[1]["s_ratio"])

    def test_extract_curve_has_s_ratio(self):
        doc, _, _ = compile_text("Alpha Beta Gamma")
        curve = extract_substance_curve(doc)
        self.assertEqual(len(curve), 3)
        self.assertEqual(curve[0]["s_ratio"], 0.0)
        self.assertGreaterEqual(curve[1]["s_ratio"], 0.0)

    def test_identical_sequences_high_score(self):
        text = "Listen Silent Test"
        doc, _, _ = compile_text(text)
        seq = extract_substance_curve(doc)
        cmp = compare_substance_sequences(seq, seq)
        self.assertGreaterEqual(cmp["geometry_score"], 0.99)
        self.assertTrue(cmp["aligned"])

    def test_anagram_shadow_count(self):
        doc_a, _, _ = compile_text("Listen")
        doc_b, _, _ = compile_text("Silent")
        seq_a = extract_substance_curve(doc_a)
        seq_b = extract_substance_curve(doc_b)
        cmp = compare_substance_sequences(seq_a, seq_b)
        self.assertEqual(cmp["anagram_shadow_count"], 1)

    def test_anagram_point_distance_zero(self):
        doc_a, _, _ = compile_text("Listen")
        doc_b, _, _ = compile_text("Silent")
        seq_a = extract_substance_curve(doc_a)
        seq_b = extract_substance_curve(doc_b)
        s_a = seq_a[0]["substance"]
        s_b = seq_b[0]["substance"]
        self.assertAlmostEqual(substance_log_similarity(s_a, s_b), 1.0, places=6)
        self.assertAlmostEqual(substance_log_distance(s_a, s_b), 0.0, places=6)

    def test_substance_parallel_synonym_like(self):
        doc_a, _, _ = compile_text("Listen Silent")
        doc_b, _, _ = compile_text("Silent Listen")
        cmp = compare_substance_sequences(
            extract_substance_curve(doc_a),
            extract_substance_curve(doc_b),
            literal_match_ratio=0.0,
        )
        self.assertGreaterEqual(cmp["geometry_score"], 0.75)
        self.assertTrue(cmp["substance_parallel"])


if __name__ == "__main__":
    unittest.main()
