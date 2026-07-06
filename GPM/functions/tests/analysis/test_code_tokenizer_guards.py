"""Guard A/B — Case-Preservation und Multiline-Kommentare."""

import unittest

from alphabets import AlphabetProfile
from analysis.blocks.registry import DocumentRegistry
from analysis.code.compile import compile_source, verify_reversibility
from analysis.code.decompile import reconstruct_source
from analysis.code.tokenizer import tokenize_source
from analysis.code.tokens import tokenize_results_equal


class TestCodeTokenizerGuards(unittest.TestCase):
    def _assert_sql_roundtrip(self, source: str) -> None:
        reg = DocumentRegistry(profile=AlphabetProfile.OG)
        self.assertTrue(verify_reversibility(source, "sql", reg))
        out = reconstruct_source(compile_source(source, "sql", reg), reg)
        self.assertEqual(out, source)

    def test_guard_a_select_upper(self):
        self._assert_sql_roundtrip("SELECT * FROM t;\n")

    def test_guard_a_select_lower(self):
        self._assert_sql_roundtrip("select * from t;\n")

    def test_guard_a_select_mixed(self):
        self._assert_sql_roundtrip("SeLeCt * FrOm t;\n")

    def test_guard_b_multiline_block_comment(self):
        source = "SELECT 1;\n/*\n  line2\n  line3\n*/\nINSERT INTO t;\n"
        reg = DocumentRegistry(profile=AlphabetProfile.OG)
        orig = tokenize_source(source, "sql")
        self._assert_sql_roundtrip(source)
        decompiled = reconstruct_source(compile_source(source, "sql", reg), reg)
        after = tokenize_source(decompiled, "sql")
        self.assertTrue(tokenize_results_equal(after, orig))
        insert_toks = [t for t in after.tokens if t.value == "INSERT"]
        self.assertTrue(insert_toks)
        self.assertEqual(insert_toks[0].nl, 1)

    def test_guard_b_js_multiline(self):
        source = "const x = 1;\n/*\na\n*/\nconst y = 2;\n"
        reg = DocumentRegistry(profile=AlphabetProfile.OG)
        orig = tokenize_source(source, "js")
        self.assertTrue(verify_reversibility(source, "js", reg))
        after = tokenize_source(reconstruct_source(compile_source(source, "js", reg), reg), "js")
        self.assertTrue(tokenize_results_equal(after, orig))


if __name__ == "__main__":
    unittest.main()
