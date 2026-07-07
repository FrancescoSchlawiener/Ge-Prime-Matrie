"""Fremde Nicht-Whitespace-Zeichen (Em-Dash, typografische Quotes, Symbole)
duerfen nicht in den Gap leaken — sprachunabhaengiger, verlustfreier Roundtrip.
"""

import unittest

from alphabets import AlphabetProfile
from analysis.blocks.registry import DocumentRegistry
from analysis.code.compile import compile_source, verify_reversibility
from analysis.code.decompile import reconstruct_source
from analysis.code.tokenizer import tokenize_source
from analysis.code.tokens import tokenize_results_equal

EM_DASH = "\u2014"
LDQUO = "\u201c"
RDQUO = "\u201d"
SECTION = "\u00a7"
DEGREE = "\u00b0"
EURO = "\u20ac"


class TestCodeSymbolGap(unittest.TestCase):
    def _roundtrip(self, source: str, language_id: str) -> None:
        reg = DocumentRegistry(profile=AlphabetProfile.OG)
        # Kein Crash mehr, exakter Byte-Roundtrip.
        mod = compile_source(source, language_id, reg)
        out = reconstruct_source(mod, reg)
        self.assertEqual(out, source, f"{language_id}: {source!r} -> {out!r}")
        self.assertTrue(
            verify_reversibility(source, language_id, DocumentRegistry(profile=AlphabetProfile.OG)),
            f"verify_reversibility fehlgeschlagen fuer {language_id}: {source!r}",
        )
        # Tokenisierung ist idempotent ueber den Roundtrip.
        before = tokenize_source(source, language_id)
        after = tokenize_source(out, language_id)
        self.assertTrue(tokenize_results_equal(after, before))

    def test_em_dash_bare_python(self):
        self._roundtrip(f"a = 1 {EM_DASH} 2\n", "py")

    def test_em_dash_in_hash_comment_python(self):
        self._roundtrip(f"x = 1  # value {EM_DASH} one\nname = 1\n", "py")

    def test_curly_quotes_js(self):
        self._roundtrip(f"const s = {LDQUO}x{RDQUO};\n", "js")

    def test_em_dash_bare_js(self):
        self._roundtrip(f"let a = 1 {EM_DASH} 2;\n", "js")

    def test_section_sign_python(self):
        self._roundtrip(f"x = {SECTION} + 1\n", "py")

    def test_degree_sql(self):
        self._roundtrip(f"SELECT {DEGREE} FROM t;\n", "sql")

    def test_euro_and_symbols_js(self):
        self._roundtrip(f"const e = 5{EURO}; ~x; a\\b;\n", "js")

    def test_em_dash_ruby(self):
        self._roundtrip(f"x = 1 {EM_DASH} 2\n", "rb")

    def test_multiple_symbols_in_a_row(self):
        self._roundtrip(f"y = 1 {EM_DASH}{EM_DASH} {SECTION}{SECTION} 2\n", "js")

    def test_symbol_in_typescript_via_js(self):
        # .ts wird als js-Sprache behandelt (siehe language_for_extension).
        self._roundtrip(f"const label = 1; // {EM_DASH} dash\n", "js")

    def test_plain_code_unaffected(self):
        # Regression: normaler Code bleibt exakt reversibel.
        self._roundtrip("function add(a, b) { return a + b; }\n", "js")


if __name__ == "__main__":
    unittest.main()
