"""Tests für nl/col_prefix/EOF-Invariante im Code-Pfad."""

import unittest

from alphabets import AlphabetProfile
from analysis.blocks.registry import DocumentRegistry
from analysis.code.compile import compile_source, verify_reversibility
from analysis.code.decompile import reconstruct_source


class TestCodeNlInvariant(unittest.TestCase):
    def setUp(self):
        self.reg = DocumentRegistry(profile=AlphabetProfile.OG)

    def _assert_roundtrip(self, source: str, lang: str) -> None:
        reg = DocumentRegistry(profile=AlphabetProfile.OG)
        mod = compile_source(source, lang, reg)
        self.assertIn("trailing_whitespace", mod.meta)
        out = reconstruct_source(mod, reg)
        self.assertEqual(out, source, f"roundtrip failed for {lang!r}")
        self.assertTrue(verify_reversibility(source, lang, reg))

    def test_no_whitespace_in_registry(self):
        src = "def foo():\n    return 1\n"
        compile_source(src, "py", self.reg)
        for entry in self.reg.s_entries:
            self.assertTrue(entry.word_canonical.strip())

    def test_py_indent_with_eof_newline(self):
        self._assert_roundtrip("def foo():\n    return 1\n", "py")

    def test_js_eof_newline(self):
        self._assert_roundtrip("function f() {}\n", "js")

    def test_js_inline_spacing(self):
        self._assert_roundtrip("a + b", "js")

    def test_eof_trailing_spaces(self):
        self._assert_roundtrip("x = 1  \n\n", "py")

    def test_eof_spaces_after_newline(self):
        self._assert_roundtrip("return 1\n    ", "py")

    def test_html_eof(self):
        self._assert_roundtrip("<div></div>\n ", "html")


if __name__ == "__main__":
    unittest.main()
