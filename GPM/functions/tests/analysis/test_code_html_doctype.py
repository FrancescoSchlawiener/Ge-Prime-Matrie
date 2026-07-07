"""HTML DOCTYPE / processing-instruction tokenization."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from alphabets import AlphabetProfile  # noqa: E402
from analysis.blocks.registry import DocumentRegistry  # noqa: E402
from analysis.code.compile import compile_source, verify_reversibility  # noqa: E402
from analysis.code.tokenizer import tokenize_html  # noqa: E402


class TestCodeHtmlDoctype(unittest.TestCase):
    def test_doctype_html_roundtrip_minimal(self):
        src = "<!doctype html>\n<html></html>\n"
        reg = DocumentRegistry(profile=AlphabetProfile.OG)
        self.assertTrue(verify_reversibility(src, "html", reg))
        c_vals = {e.key_bytes.decode("utf-8", errors="replace") for e in reg.c_entries}
        self.assertTrue(any("doctype" in v.lower() for v in c_vals))

    def test_doctype_html_workbench_snippet_compiles(self):
        src = (
            "<!doctype html>\n"
            '<html lang="de">\n'
            "  <head><meta charset=\"UTF-8\" /></head>\n"
            "  <body><div id=\"root\"></div></body>\n"
            "</html>\n"
        )
        tok = tokenize_html(src)
        self.assertGreater(len(tok.tokens), 0)
        reg = DocumentRegistry(profile=AlphabetProfile.OG)
        compile_source(src, "html", reg)
        c_vals = {e.key_bytes.decode("utf-8", errors="replace") for e in reg.c_entries}
        self.assertTrue(any("doctype" in v.lower() for v in c_vals))

    def test_xml_processing_instruction(self):
        src = '<?xml version="1.0" encoding="UTF-8"?>\n<root/>\n'
        reg = DocumentRegistry(profile=AlphabetProfile.OG)
        self.assertTrue(verify_reversibility(src, "html", reg))


if __name__ == "__main__":
    unittest.main()
