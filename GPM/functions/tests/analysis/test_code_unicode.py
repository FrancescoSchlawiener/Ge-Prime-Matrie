"""Tests für Code-Tokenizer Unicode-Härtung (Absicherung B)."""

import unittest

from alphabets import AlphabetProfile
from alphabets.unicode_utils import SurrogateCodepointError, assert_no_surrogates
from analysis.blocks.registry import DocumentRegistry
from analysis.code.compile import compile_source
from analysis.code.tokenizer import tokenize_source


class TestCodeUnicode(unittest.TestCase):
    def test_surrogate_rejected(self):
        bad = "hello\ud800world"
        with self.assertRaises(SurrogateCodepointError):
            assert_no_surrogates(bad)

    def test_js_tokenize(self):
        result = tokenize_source("function foo() { return 1; }", "js")
        self.assertGreater(len(result.tokens), 0)

    def test_html_compile(self):
        reg = DocumentRegistry(profile=AlphabetProfile.OG)
        mod = compile_source("<div>Hi</div>", "html", reg)
        self.assertIsNotNone(mod)

    def test_python_compile_runs(self):
        reg = DocumentRegistry(profile=AlphabetProfile.OG)
        src = "def foo():\n    return 1\n"
        mod = compile_source(src, "py", reg)
        self.assertIsNotNone(mod)

    def test_verify_reversibility_unicode(self):
        from analysis.code.compile import verify_reversibility

        reg = DocumentRegistry(profile=AlphabetProfile.OG)
        src = 'x = "hello 🌍"\n'
        self.assertTrue(verify_reversibility(src, "py", reg))


if __name__ == "__main__":
    unittest.main()
