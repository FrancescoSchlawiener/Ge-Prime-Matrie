"""v35 Tensorraum HTML — normalize + compile, keine S-Hex-Fragmente."""

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
from analysis.code.canonicalize import normalize_for_tensorraum  # noqa: E402
from analysis.code.compile import compile_source  # noqa: E402
from analysis.code.decompile import reconstruct_source  # noqa: E402

_FIXTURE = ROOT.parent.parent / "Toy" / "gpm_c_i_fraktaler_tensorraum_v35.html"


def _find_child_with_s(module, min_body_len: int = 10):
    for child in module.children:
        s_refs = [r for r in child.sequence if r.kind is PointerKind.S]
        if s_refs:
            return child
        found = _find_child_with_s(child, min_body_len)
        if found is not None:
            return found
    return None


class TestCodeHtmlV35Tensorraum(unittest.TestCase):
    @unittest.skipUnless(_FIXTURE.is_file(), "Toy fixture missing")
    def test_fraktaler_no_isolated_hex_s(self):
        raw = _FIXTURE.read_text(encoding="utf-8")
        normalized = normalize_for_tensorraum(raw, "html")
        reg = DocumentRegistry(profile=AlphabetProfile.OG)
        compile_source(normalized, "html", reg)
        s_vals = {e.word_canonical for e in reg.s_entries}
        isolated_hex = {v for v in s_vals if re.fullmatch(r"[0-9A-F]{3,8}", v)}
        self.assertNotIn("8B8B98", isolated_hex)
        self.assertNotIn("8b8b98", isolated_hex)

    @unittest.skipUnless(_FIXTURE.is_file(), "Toy fixture missing")
    def test_fraktaler_normalized_roundtrip(self):
        raw = _FIXTURE.read_text(encoding="utf-8")
        normalized = normalize_for_tensorraum(raw, "html")
        reg = DocumentRegistry(profile=AlphabetProfile.OG)
        mod = compile_source(normalized, "html", reg)
        out = reconstruct_source(mod, reg)
        # Eingebettete Re-Lex: Zeilenanzahl kann um wenige Gaps abweichen
        self.assertLessEqual(abs(len(out.splitlines()) - len(normalized.splitlines())), 8)
        self.assertTrue("</HTML>" in out or out.rstrip().endswith("</BODY>"))
        self.assertIn("</BODY>", out)

    @unittest.skipUnless(_FIXTURE.is_file(), "Toy fixture missing")
    def test_fraktaler_child_block_has_s_content(self):
        raw = _FIXTURE.read_text(encoding="utf-8")
        normalized = normalize_for_tensorraum(raw, "html")
        mod = compile_source(normalized, "html", DocumentRegistry(profile=AlphabetProfile.OG))
        child = _find_child_with_s(mod)
        self.assertIsNotNone(child, "Kein CHILD-Block mit S-Inhalt gefunden")
        s_refs = [r for r in child.sequence if r.kind is PointerKind.S]  # type: ignore[union-attr]
        self.assertGreater(len(s_refs), 0)

    @unittest.skipUnless(_FIXTURE.is_file(), "Toy fixture missing")
    def test_fraktaler_s_count_sane(self):
        raw = _FIXTURE.read_text(encoding="utf-8")
        normalized = normalize_for_tensorraum(raw, "html")
        reg = DocumentRegistry(profile=AlphabetProfile.OG)
        compile_source(normalized, "html", reg)
        # Re-Lex in script/style: mehr S als tag-only, aber kein Micro-Hex-Chaos
        self.assertLess(len(reg.s_entries), 8000)

    @unittest.skipUnless(_FIXTURE.is_file(), "Toy fixture missing")
    def test_fraktaler_script_child_has_n(self):
        raw = _FIXTURE.read_text(encoding="utf-8")
        normalized = normalize_for_tensorraum(raw, "html")
        mod = compile_source(normalized, "html", DocumentRegistry(profile=AlphabetProfile.OG))

        def find_script(node):
            if node.meta.get("embedded_language") == "js":
                return node
            for c in node.children:
                found = find_script(c)
                if found is not None:
                    return found
            return None

        script = find_script(mod)
        self.assertIsNotNone(script, "Kein script-CHILD mit embedded_language=js")

        def count_n(node):
            n = sum(1 for r in node.sequence if r.kind is PointerKind.N)
            for c in node.children:
                n += count_n(c)
            return n

        self.assertGreater(count_n(script), 0)


if __name__ == "__main__":
    unittest.main()
