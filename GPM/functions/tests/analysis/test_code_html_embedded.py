"""HTML embedded script/style re-tokenization."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from alphabets import AlphabetProfile  # noqa: E402
from analysis.blocks.registry import DocumentRegistry  # noqa: E402
from analysis.code.compile import compile_source  # noqa: E402
from analysis.code.tokenizer import tokenize_html  # noqa: E402

_FIXTURE = ROOT.parent.parent / "Toy" / "gpm_c_i_fraktaler_tensorraum_v35.html"


class TestCodeHtmlEmbedded(unittest.TestCase):
    def test_script_comparison_operators(self):
        src = "<script>if(a<b){}</script>\n"
        reg = DocumentRegistry(profile=AlphabetProfile.OG)
        compile_source(src, "html", reg)
        self.assertGreater(len(reg.s_entries), 0)

    def test_script_template_literal(self):
        src = "<script>const x=`</div>`;</script>\n"
        reg = DocumentRegistry(profile=AlphabetProfile.OG)
        compile_source(src, "html", reg)
        self.assertGreater(len(reg.c_entries), 0)

    def test_style_block(self):
        src = "<style>.a{color:red}</style>\n"
        reg = DocumentRegistry(profile=AlphabetProfile.OG)
        compile_source(src, "html", reg)
        self.assertGreater(len(reg.c_entries), 0)

    def test_doctype_with_script(self):
        src = "<!doctype html>\n<html><script>const n=1;</script></html>\n"
        reg = DocumentRegistry(profile=AlphabetProfile.OG)
        compile_source(src, "html", reg)
        self.assertGreater(len(reg.n_entries), 0)

    def test_tokenize_html_script_body_is_js(self):
        src = "<script>let a=1;</script>\n"
        tok = tokenize_html(src)
        types = [t.type or t.block for t in tok.tokens]
        self.assertIn("open", types)
        self.assertIn("C", types)

    @unittest.skipUnless(_FIXTURE.is_file(), "Toy fixture missing")
    def test_fraktaler_tensorraum_fixture(self):
        html = _FIXTURE.read_text(encoding="utf-8")
        reg = DocumentRegistry(profile=AlphabetProfile.OG)
        compile_source(html, "html", reg)
        self.assertGreater(len(reg.s_entries), 10)
        self.assertGreater(len(reg.c_entries), 10)


if __name__ == "__main__":
    unittest.main()
