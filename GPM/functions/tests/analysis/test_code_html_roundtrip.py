"""HTML nested tag round-trip."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from alphabets import AlphabetProfile  # noqa: E402
from analysis.blocks.registry import DocumentRegistry  # noqa: E402
from analysis.code.canonicalize import normalize_for_tensorraum  # noqa: E402
from analysis.code.compile import compile_source, verify_reversibility  # noqa: E402
from analysis.code.decompile import reconstruct_source  # noqa: E402

_FIXTURE = ROOT.parent.parent / "Toy" / "gpm_c_i_fraktaler_tensorraum_v35.html"


class TestCodeHtmlRoundtrip(unittest.TestCase):
    def test_nested_head_body_roundtrip(self):
        src = "<html><head><title>x</title></head><body></body></html>\n"
        reg = DocumentRegistry(profile=AlphabetProfile.OG)
        self.assertTrue(verify_reversibility(src, "html", reg))

    def test_doctype_script_style_roundtrip(self):
        src = (
            "<!DOCTYPE html><html><head><style>.a{}</style></head>"
            "<body><script>const n=1;</script></body></html>\n"
        )
        reg = DocumentRegistry(profile=AlphabetProfile.OG)
        mod = compile_source(src, "html", reg)
        self.assertEqual(reconstruct_source(mod, reg), src)
        self.assertTrue(verify_reversibility(src, "html", reg))

    def test_workbench_index_html_roundtrip(self):
        index_path = ROOT.parent / "workbench" / "web" / "index.html"
        if not index_path.is_file():
            self.skipTest("workbench index.html missing")
        src = index_path.read_text(encoding="utf-8")
        reg = DocumentRegistry(profile=AlphabetProfile.OG)
        self.assertTrue(verify_reversibility(src, "html", reg))

    @unittest.skipUnless(_FIXTURE.is_file(), "Toy fixture missing")
    def test_fraktaler_tensorraum_fixture_roundtrip(self):
        raw = _FIXTURE.read_text(encoding="utf-8")
        src = normalize_for_tensorraum(raw, "html")
        reg = DocumentRegistry(profile=AlphabetProfile.OG)
        mod = compile_source(src, "html", reg)
        out = reconstruct_source(mod, reg)
        self.assertEqual(len(out.splitlines()), len(src.splitlines()))
        self.assertTrue(out.endswith("</HTML>"))
        self.assertIn("</BODY>", out)


if __name__ == "__main__":
    unittest.main()
