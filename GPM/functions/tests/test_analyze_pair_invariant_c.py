import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from alphabets import AlphabetProfile
from analysis.compile.compiler import compile_text
from analysis.curves.compare import AxisWeights, analyze_pair, fuse_axis_scores


class TestAnalyzePairInvariantC(unittest.TestCase):
    def test_default_weights_sum_to_one(self):
        weights = AxisWeights()
        weights.validate()
        norm = weights.normalized()
        self.assertAlmostEqual(sum(norm.values()), 1.0, places=9)

    def test_full_weights_sum_to_one(self):
        weights = AxisWeights.full()
        weights.validate()

    def test_geometry_score_bounded(self):
        profile = AlphabetProfile.OG
        d1, _ = compile_text("Hallo Welt", profile)
        d2, _ = compile_text("Hallo Welt", profile)
        result = analyze_pair(d1, d2)
        self.assertGreaterEqual(result["geometry_score"], 0.0)
        self.assertLessEqual(result["geometry_score"], 1.0)

    def test_scale_invariance_fuse(self):
        scores = {"substance": 0.8, "token_i": 0.6, "cell_i": 0.7, "hierarchy": 0.5}
        w1 = AxisWeights()
        w2 = AxisWeights(substance=0.5, token_i=0.7, cell_i=0.5, hierarchy=0.3)
        self.assertAlmostEqual(
            fuse_axis_scores(scores, w1),
            fuse_axis_scores(scores, w2),
            places=6,
        )

    def test_listen_silent_regression(self):
        profile = AlphabetProfile.OG
        d1, _ = compile_text("LISTEN", profile)
        d2, _ = compile_text("SILENT", profile)
        result = analyze_pair(d1, d2)
        self.assertAlmostEqual(result["axis_scores"]["substance"], 1.0, places=4)
        self.assertLess(result["axis_scores"]["token_i"], 1.0)
        self.assertTrue(result["substance_parallel"])


if __name__ == "__main__":
    unittest.main()
