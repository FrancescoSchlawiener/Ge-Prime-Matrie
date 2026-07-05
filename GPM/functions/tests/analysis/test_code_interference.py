"""Tests für NL/Code-Interferenz-Verbot (Absicherung A)."""

import unittest

from alphabets import AlphabetProfile
from analysis.blocks.context import COrigin, NL_CONTEXT
from analysis.blocks.kinds import PointerKind
from analysis.blocks.registry import DocumentRegistry
from analysis.compile.compiler import compile_text


class TestCodeInterference(unittest.TestCase):
    def test_nl_keyword_c_rejected(self):
        reg = DocumentRegistry(profile=AlphabetProfile.OG)
        with self.assertRaises(ValueError):
            reg.intern(PointerKind.C, "if", context=NL_CONTEXT)
        with self.assertRaises(ValueError):
            reg.intern(PointerKind.C, "for", context=NL_CONTEXT)

    def test_nl_prose_keywords_stay_s_tokens(self):
        doc, _ = compile_text("If you want to for loop", AlphabetProfile.OG)
        self.assertEqual(len(doc.tokens), 6)
        for token in doc.tokens:
            self.assertEqual(token.payload_kind.value, "S")

    def test_geom_c_allowed_in_nl(self):
        from analysis.blocks.context import COrigin

        reg = DocumentRegistry(profile=AlphabetProfile.OG)
        ptr = reg.intern(PointerKind.C, b"\x01\x02", origin=COrigin.GEOM, context=NL_CONTEXT)
        self.assertEqual(ptr, 0)

    def test_code_if_is_c_in_python(self):
        from analysis.code.compile import compile_source

        reg = DocumentRegistry(profile=AlphabetProfile.OG)
        compile_source("if True:\n    pass\n", "py", reg)
        c_keys = [e.key_bytes.decode("utf-8", errors="replace") for e in reg.c_entries]
        self.assertIn("if", c_keys)

    def test_compile_hybrid_runs(self):
        from analysis.code.compile import compile_hybrid

        doc = compile_hybrid("If prose\n\n```py\nif True:\n    pass\n```\n", AlphabetProfile.OG)
        self.assertIsNotNone(doc.registry)


if __name__ == "__main__":
    unittest.main()
