import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from alphabets import AlphabetProfile
from analysis.compile.compiler import compile_text
from analysis.curves.compare import analyze_pair_full


class TestAnalyzePairFull(unittest.TestCase):
    def test_full_includes_meta_and_validation(self):
        profile = AlphabetProfile.OG
        d1, _ = compile_text("Hallo Welt.", profile)
        d2, _ = compile_text("Hallo Welt.", profile)
        result = analyze_pair_full(d1, d2)
        self.assertIn("comparison", result)
        self.assertIn("meta_a", result)
        self.assertIn("meta_b", result)
        self.assertIn("validation_pipeline", result)
        self.assertIn("literal_match_ratio", result["comparison"])
        self.assertGreaterEqual(result["geometry_score"], 0.85)

    def test_full_listen_silent_literal_low(self):
        profile = AlphabetProfile.OG
        d1, _ = compile_text("LISTEN", profile)
        d2, _ = compile_text("SILENT", profile)
        result = analyze_pair_full(d1, d2)
        self.assertLess(result["comparison"]["literal_match_ratio"], 1.0)
        self.assertIn("substance_geometry", result["comparison"])


if __name__ == "__main__":
    unittest.main()
