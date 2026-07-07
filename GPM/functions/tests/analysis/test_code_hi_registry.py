import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from alphabets import AlphabetProfile
from analysis.blocks.kinds import PointerKind
from analysis.blocks.registry import DocumentRegistry
from analysis.code.compile import compile_source, verify_reversibility
from analysis.code.tokenizer import classify_code_token
from analysis.blocks.context import ParseContext, ParseDomain


class TestCodeHiRegistry(unittest.TestCase):
    def test_classify_abc123_as_h(self):
        ctx = ParseContext(domain=ParseDomain.CODE, language_id="js")
        kind = classify_code_token("abc123", context=ctx, language_id="js")
        self.assertEqual(kind, PointerKind.H)

    def test_classify_pure_alpha_as_s(self):
        ctx = ParseContext(domain=ParseDomain.CODE, language_id="js")
        kind = classify_code_token("hello", context=ctx, language_id="js")
        self.assertEqual(kind, PointerKind.S)

    def test_intern_h_segments_in_s_and_n(self):
        reg = DocumentRegistry(profile=AlphabetProfile.OG)
        ctx = ParseContext(domain=ParseDomain.CODE, language_id="js")
        reg.intern(PointerKind.H, "abc123", context=ctx)
        self.assertEqual(len(reg.h_entries), 1)
        self.assertEqual(len(reg.h_entries[0].segments), 2)
        self.assertGreater(len(reg.s_entries), 0)
        self.assertGreater(len(reg.n_entries), 0)
        n_seg = next(s for s in reg.h_entries[0].segments if s.tag == "N")
        self.assertEqual(n_seg.value, "123")
        self.assertIsNotNone(n_seg.ptr_id)
        self.assertEqual(reg.n_display(n_seg.ptr_id), "123")

    def test_verify_reversibility_with_h(self):
        reg = DocumentRegistry(profile=AlphabetProfile.OG)
        src = "var x = abc123 + 42;\n"
        self.assertTrue(verify_reversibility(src, "js", reg))


if __name__ == "__main__":
    unittest.main()
