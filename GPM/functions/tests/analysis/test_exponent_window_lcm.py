"""Härtungs-Invariante F-A — exponent_window_to_substance zentralisiert."""

import unittest

from alphabets import AlphabetProfile
from analysis.algebra.window_fold import ExponentWindow, exponent_window_to_substance
from analysis.index.substance_index import _fingerprint_lcm_value, window_fingerprint
from analysis.compile.compiler import compile_text
from analysis.index.substance_index import build_substance_index, get_substance_index
from analysis.search.spectroscope import spectroscope_analyze


class TestExponentWindowLcm(unittest.TestCase):
    def test_delegates_from_substance_index(self):
        window = ExponentWindow({2: 3, 5: 1})
        self.assertEqual(_fingerprint_lcm_value(window), exponent_window_to_substance(window))

    def test_spectroscope_target_matches_window_fold(self):
        doc, _ = compile_text("Hallo Welt.", AlphabetProfile.OG)
        idx = build_substance_index(doc)
        fp = window_fingerprint(idx, 0, len(doc.tokens))
        self.assertEqual(exponent_window_to_substance(fp), _fingerprint_lcm_value(fp))

    def test_document_window_consistency(self):
        doc, _ = compile_text("ABC DEF GHI.", AlphabetProfile.OG)
        idx = get_substance_index(doc)
        fp = window_fingerprint(idx, 0, 2)
        lcm_val = exponent_window_to_substance(fp)
        self.assertGreater(lcm_val, 1)


if __name__ == "__main__":
    unittest.main()
