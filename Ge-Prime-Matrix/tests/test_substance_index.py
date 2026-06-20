import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from gpm.compiler import compile_text
from ge_prime.spectroscope import spectroscope_analyze
from ge_prime.substance_index import (
    build_substance_index,
    window_fingerprint,
)


def _reference_lcm(document, start: int, width: int) -> int:
    substances = [
        document.header[document.tokens[start + i].word_id].substance
        for i in range(width)
    ]
    result = substances[0] if substances else 1
    for s in substances[1:]:
        result = math.lcm(result, s)
    return result


class TestSubstanceIndex(unittest.TestCase):
    def test_sparse_map_only_document_primes(self):
        text = "Hallo Welt Test"
        doc, _, _ = compile_text(text)
        index = build_substance_index(doc)
        self.assertGreater(len(index.exp_by_prime), 0)
        self.assertLess(len(index.exp_by_prime), 500)
        for prime, series in index.exp_by_prime.items():
            self.assertEqual(len(series), len(doc.tokens))
            self.assertIsInstance(prime, int)

    def test_window_fingerprint_matches_reference_lcm(self):
        text = "Alpha Beta Gamma Delta"
        doc, _, _ = compile_text(text)
        index = build_substance_index(doc)
        width = 2
        for start in range(0, len(doc.tokens) - width + 1):
            fp = window_fingerprint(index, start, start + width)
            ref = _reference_lcm(doc, start, width)
            window_lcm = 1
            for prime, exp in fp.exponents.items():
                window_lcm = math.lcm(window_lcm, prime**exp)
            self.assertEqual(window_lcm, ref, msg=f"start={start}")

    def test_spectroscope_scan_runs(self):
        text = "Das ist ein Test. Noch ein Satz."
        doc, _, _ = compile_text(text)
        result = spectroscope_analyze(
            doc, token_start=0, token_end=2, modes=["substance_divisor"]
        )
        self.assertIn("matches", result)
        self.assertIn("target", result)


if __name__ == "__main__":
    unittest.main()
