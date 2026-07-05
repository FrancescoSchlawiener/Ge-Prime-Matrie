"""Tests für Hybrid Gap-Erhaltungs-Invariante."""

import unittest

from alphabets import AlphabetProfile
from analysis.code.compile import compile_hybrid, verify_hybrid_reversibility
from analysis.code.decompile import reconstruct_hybrid


class TestCodeHybridGaps(unittest.TestCase):
    def _assert_hybrid(self, source: str) -> None:
        self.assertTrue(verify_hybrid_reversibility(source, AlphabetProfile.OG))
        doc = compile_hybrid(source, AlphabetProfile.OG)
        out = reconstruct_hybrid(doc)
        self.assertEqual(out, source, f"hybrid roundtrip failed:\n{source!r}\n{out!r}")

    def test_blank_line_before_fence(self):
        self._assert_hybrid("Title\n\n```py\nif True: pass\n```\n")

    def test_space_after_closing_fence(self):
        self._assert_hybrid("```py\nx=1\n``` \n\nTail")

    def test_tilde_fence(self):
        self._assert_hybrid("Intro\n\n~~~js\nconst x = 1;\n~~~\n")

    def test_two_fences_tight(self):
        self._assert_hybrid("A\n```py\nx=1\n```\n```js\ny=2\n```\nB")

    def test_prose_vs_code_if(self):
        src = "If prose\n\n```py\nif True:\n    pass\n```\n"
        self._assert_hybrid(src)
        doc = compile_hybrid(src, AlphabetProfile.OG)
        self.assertIsNotNone(doc.registry)
        c_keys = [
            e.key_bytes.decode("utf-8", errors="replace")
            for e in doc.registry.c_entries
        ]
        self.assertIn("if", c_keys)


if __name__ == "__main__":
    unittest.main()
