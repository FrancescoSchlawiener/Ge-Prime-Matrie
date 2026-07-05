"""Parametrisierte Round-Trip-Matrix für py/js/html."""

import unittest

from alphabets import AlphabetProfile
from analysis.blocks.registry import DocumentRegistry
from analysis.code.compile import compile_source, verify_reversibility
from analysis.code.decompile import reconstruct_source


class TestCodeLanguages(unittest.TestCase):
    def _assert_roundtrip(self, source: str, lang: str) -> None:
        reg = DocumentRegistry(profile=AlphabetProfile.OG)
        mod = compile_source(source, lang, reg)
        out = reconstruct_source(mod, reg)
        self.assertEqual(out, source, f"{lang} roundtrip failed")
        self.assertTrue(verify_reversibility(source, lang, reg))

    def test_py_comment(self):
        self._assert_roundtrip("x = 1  # note\n", "py")

    def test_py_docstring(self):
        self._assert_roundtrip('"""doc"""\n', "py")

    def test_py_pass_block(self):
        self._assert_roundtrip("if True:\n    pass\n", "py")

    def test_js_line_comment(self):
        self._assert_roundtrip("const x = 1; // note\n", "js")

    def test_js_block_comment(self):
        self._assert_roundtrip("/* block */\nconst x = 1;\n", "js")

    def test_js_arrow(self):
        self._assert_roundtrip("const f = () => 1;\n", "js")

    def test_js_array_index(self):
        self._assert_roundtrip("arr[i]", "js")

    def test_js_template_unicode(self):
        self._assert_roundtrip('const s = `\\u1F600`;\n', "js")

    def test_html_comment(self):
        self._assert_roundtrip("<!-- comment -->\n<div></div>\n", "html")

    def test_html_attributes_spacing(self):
        self._assert_roundtrip('<div class="a"></div>\n', "html")

    def test_html_void_tag(self):
        self._assert_roundtrip("<br>\n", "html")

    def test_html_text_node(self):
        self._assert_roundtrip("<p>Hello</p>\n", "html")


if __name__ == "__main__":
    unittest.main()
