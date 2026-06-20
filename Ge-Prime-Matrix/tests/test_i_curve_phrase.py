import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from ge_prime.i_curve import analyze_pair


class TestICurvePhrase(unittest.TestCase):
    def test_hierarchy_comparison_includes_phrase(self):
        text = "Hallo Welt. Noch ein Satz hier."
        result = analyze_pair(text_a=text, text_b=text)
        hc = result["hierarchy_comparison"]
        self.assertIn("phrase", hc["semantic"])
        self.assertIn("geometry_score", hc["semantic"]["phrase"])
        self.assertEqual(hc["semantic"]["phrase"]["method"], "dtw")


if __name__ == "__main__":
    unittest.main()
