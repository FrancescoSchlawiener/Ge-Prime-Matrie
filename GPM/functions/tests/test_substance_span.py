"""Tests für kgV-Span-Gates."""

import unittest

from alphabets import AlphabetProfile
from analysis.compile.compiler import compile_text
from analysis.span.substance_span import local_kgv, passes_kgv_gate


class TestSubstanceSpan(unittest.TestCase):
    def test_local_kgv_empty_span(self):
        doc, _ = compile_text("Hallo Welt", AlphabetProfile.OG)
        self.assertEqual(local_kgv(doc, 0, 0), 0)

    def test_local_kgv_two_tokens(self):
        doc, _ = compile_text("Hallo Welt", AlphabetProfile.OG)
        kgv = local_kgv(doc, 0, 2)
        s0 = doc.header[doc.tokens[0].word_id].substance
        s1 = doc.header[doc.tokens[1].word_id].substance
        import math

        self.assertEqual(kgv, math.lcm(s0, s1))

    def test_passes_kgv_gate_target_one(self):
        self.assertTrue(passes_kgv_gate(100, 1))

    def test_passes_kgv_gate_modulo(self):
        self.assertTrue(passes_kgv_gate(12, 4))
        self.assertFalse(passes_kgv_gate(6, 4))
        self.assertFalse(passes_kgv_gate(1, 5))


if __name__ == "__main__":
    unittest.main()
