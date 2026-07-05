"""Tests für orthogonale DTW-Fusion (Absicherung C)."""

import unittest

from alphabets import AlphabetProfile
from analysis.compile.compiler import compile_text
from analysis.curves.compare import analyze_pair


class TestCurvesFusion(unittest.TestCase):
    def test_listen_silent_substance_parallel(self):
        profile = AlphabetProfile.OG
        d1, _ = compile_text("LISTEN", profile)
        d2, _ = compile_text("SILENT", profile)
        result = analyze_pair(d1, d2)
        self.assertAlmostEqual(result["axis_scores"]["substance"], 1.0, places=4)
        self.assertLess(result["axis_scores"]["token_i"], 1.0)
        self.assertTrue(result["substance_parallel"])

    def test_identical_text_high_geometry(self):
        profile = AlphabetProfile.OG
        d1, _ = compile_text("Hallo Welt", profile)
        d2, _ = compile_text("Hallo Welt", profile)
        result = analyze_pair(d1, d2)
        self.assertGreaterEqual(result["geometry_score"], 0.85)


if __name__ == "__main__":
    unittest.main()
