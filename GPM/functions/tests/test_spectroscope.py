import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from alphabets import AlphabetProfile
from analysis.compile.compiler import compile_text, normalize_text_nfc
from analysis.search.spectroscope import spectroscope_analyze, spectroscope_from_text


class TestSpectroscope(unittest.TestCase):
    def test_crossfire_separate_scores(self):
        text = "Hallo Welt. Das ist ein Test.\nZweite Zeile hier."
        doc, _ = compile_text(text, AlphabetProfile.OG)
        result = spectroscope_analyze(
            doc,
            token_start=0,
            token_end=2,
            modes=["structural_twin"],
        )
        for match in result["matches"]:
            layer = match.get("layer")
            if layer == "semantic":
                self.assertIn("score_semantic", match)
            if layer == "structural":
                self.assertIn("score_structural", match)

    def test_spectroscope_from_text_selection(self):
        text = "Alpha Beta Gamma."
        result = spectroscope_from_text(text, selection_start=0, selection_end=5, modes=["anagram_shadow"])
        self.assertIn("target", result)
        self.assertIn("matches", result)
        self.assertIn("token_char_map", result)

    def test_spectroscope_nfd_selection_after_nfc_wash(self):
        nfd = "Gr\u0061\u0308ser wachsen."
        nfc = normalize_text_nfc(nfd)
        result = spectroscope_from_text(
            nfd,
            selection_start=0,
            selection_end=len(nfc),
            modes=["substance_divisor"],
        )
        self.assertGreaterEqual(result["target"]["token_end"], result["target"]["token_start"])


if __name__ == "__main__":
    unittest.main()
