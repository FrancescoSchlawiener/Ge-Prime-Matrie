"""HTML embedded script/style — CHILD mit Sprachregeln (js/css Re-Lex)."""

from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from alphabets import AlphabetProfile  # noqa: E402
from analysis.blocks.kinds import PointerKind  # noqa: E402
from analysis.blocks.registry import DocumentRegistry  # noqa: E402
from analysis.code.compile import compile_source  # noqa: E402
from analysis.code.tokenizer import tokenize_html  # noqa: E402

_FIXTURE = ROOT.parent.parent / "Toy" / "gpm_c_i_fraktaler_tensorraum_v35.html"


def _script_child(mod):
    for child in mod.children:
        if child.meta.get("embedded_language") == "js" or child.meta.get("open_syntax", "").lower() == "script":
            return child
        found = _script_child(child)
        if found is not None:
            return found
    return None


class TestCodeHtmlEmbedded(unittest.TestCase):
    def test_script_body_relexed_to_tokens(self):
        src = "<script>let a=1;</script>\n"
        tok = tokenize_html(src)
        n_tokens = [t for t in tok.tokens if t.type == "N"]
        self.assertGreater(len(n_tokens), 0)
        self.assertTrue(any(t.value == "1" for t in n_tokens))

    def test_script_child_has_n_and_c(self):
        src = "<script>let a=1;</script>\n"
        mod = compile_source(src, "html", DocumentRegistry(profile=AlphabetProfile.OG))
        child = _script_child(mod)
        self.assertIsNotNone(child)
        kinds = {r.kind for r in child.sequence}
        self.assertIn(PointerKind.N, kinds)
        self.assertIn(PointerKind.C, kinds)

    def test_script_template_literal(self):
        src = "<script>const x=`</div>`;</script>\n"
        reg = DocumentRegistry(profile=AlphabetProfile.OG)
        compile_source(src, "html", reg)
        self.assertGreater(len(reg.c_entries), 0)

    def test_style_block_no_hex_fragment_s(self):
        src = "<style>.a{color:#8b8b98}</style>\n"
        reg = DocumentRegistry(profile=AlphabetProfile.OG)
        compile_source(src, "html", reg)
        s_vals = {e.word_canonical for e in reg.s_entries}
        isolated_hex = {v for v in s_vals if re.fullmatch(r"[0-9A-Fa-f]{3,8}", v)}
        self.assertNotIn("8B8B98", isolated_hex)
        self.assertNotIn("8b8b98", isolated_hex)
        self.assertTrue(any("8B8B98" in v or "8b8b98" in v.lower() for v in s_vals))

    def test_style_child_has_content(self):
        src = "<style>.a{color:red}</style>\n"
        mod = compile_source(src, "html", DocumentRegistry(profile=AlphabetProfile.OG))
        child = mod.children[0]
        self.assertEqual(child.meta.get("embedded_language"), "css")
        self.assertGreater(len(child.sequence), 0)

    def test_doctype_with_script_relexed(self):
        src = "<!doctype html>\n<html><script>const n=1;</script></html>\n"
        reg = DocumentRegistry(profile=AlphabetProfile.OG)
        compile_source(src, "html", reg)
        self.assertGreater(len(reg.n_entries), 0)

    @unittest.skipUnless(_FIXTURE.is_file(), "Toy fixture missing")
    def test_fraktaler_tensorraum_fixture(self):
        html = _FIXTURE.read_text(encoding="utf-8")
        reg = DocumentRegistry(profile=AlphabetProfile.OG)
        compile_source(html, "html", reg)
        self.assertGreater(len(reg.s_entries), 10)
        self.assertGreater(len(reg.c_entries), 10)
        self.assertGreater(len(reg.n_entries), 0)
        s_vals = {e.word_canonical for e in reg.s_entries}
        isolated_hex = {v for v in s_vals if re.fullmatch(r"[0-9A-F]{3,8}", v)}
        self.assertNotIn("8B8B98", isolated_hex)
        self.assertNotIn("8b8b98", isolated_hex)


if __name__ == "__main__":
    unittest.main()
