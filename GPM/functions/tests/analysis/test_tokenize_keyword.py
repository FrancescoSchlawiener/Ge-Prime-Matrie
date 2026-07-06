"""Tests für keyword- und flat-Tokenizer."""

import unittest

from alphabets import AlphabetProfile
from analysis.blocks.registry import DocumentRegistry
from analysis.code.compile import verify_reversibility


class TestTokenizeKeyword(unittest.TestCase):
    def test_ruby_def_end(self):
        src = "def foo\n  1\nend\n"
        reg = DocumentRegistry(profile=AlphabetProfile.OG)
        self.assertTrue(verify_reversibility(src, "rb", reg))

    def test_shell_if_fi(self):
        src = "if true; then echo hi; fi\n"
        reg = DocumentRegistry(profile=AlphabetProfile.OG)
        self.assertTrue(verify_reversibility(src, "sh", reg))

    def test_sql_begin_end(self):
        src = "BEGIN\n  SELECT 1;\nEND;\n"
        reg = DocumentRegistry(profile=AlphabetProfile.OG)
        self.assertTrue(verify_reversibility(src, "sql", reg))


class TestTokenizeFlat(unittest.TestCase):
    def test_json_object(self):
        src = '{"a": 1, "b": [2]}\n'
        reg = DocumentRegistry(profile=AlphabetProfile.OG)
        self.assertTrue(verify_reversibility(src, "json", reg))

    def test_toml(self):
        src = "[section]\nkey = 1\n"
        reg = DocumentRegistry(profile=AlphabetProfile.OG)
        self.assertTrue(verify_reversibility(src, "toml", reg))

    def test_markdown(self):
        src = "# Title\n\nParagraph.\n"
        reg = DocumentRegistry(profile=AlphabetProfile.OG)
        self.assertTrue(verify_reversibility(src, "markdown", reg))


if __name__ == "__main__":
    unittest.main()
