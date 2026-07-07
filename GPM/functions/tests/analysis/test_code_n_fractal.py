"""Fraktale N(I) — Ziffern-Pointer."""

import unittest

from alphabets import AlphabetProfile
from analysis.blocks.registry import DocumentRegistry
from analysis.code.compile import compile_source, verify_reversibility
from analysis.code.decompile import reconstruct_source


class TestCodeNFractal(unittest.TestCase):
    def _all_refs(self, node):
        for r in node.sequence:
            yield r
        for c in node.children:
            yield from self._all_refs(c)

    def test_eleven_single_tuple_ptr(self):
        reg = DocumentRegistry(profile=AlphabetProfile.OG)
        mod = compile_source("let x = 11;\n", "js", reg)
        n_refs = [r for r in self._all_refs(mod) if r.kind.value == "N"]
        self.assertEqual(len(n_refs), 1)
        entry = reg.n_entries[n_refs[0].ptr_id]
        self.assertIsInstance(entry, tuple)
        self.assertEqual(len(entry), 2)
        self.assertEqual(entry[0], entry[1])
        self.assertEqual(reg.n_display(n_refs[0].ptr_id), "11")
        digit_entries = [e for e in reg.n_entries if isinstance(e, int)]
        self.assertLessEqual(len(digit_entries), 10)

    def test_registry_has_atoms_and_composites(self):
        reg = DocumentRegistry(profile=AlphabetProfile.OG)
        compile_source("a=11; b=112;\n", "js", reg)
        displays = {reg.n_display(i) for i in range(len(reg.n_entries))}
        self.assertIn("11", displays)
        self.assertIn("112", displays)
        self.assertTrue(any(isinstance(e, tuple) for e in reg.n_entries))

    def test_eleven_vs_spaced_ones_roundtrip(self):
        reg = DocumentRegistry(profile=AlphabetProfile.OG)
        src_compact = "x=11;\n"
        src_spaced = "x=1 1;\n"
        mod_c = compile_source(src_compact, "js", reg)
        out_c = reconstruct_source(mod_c, reg)
        self.assertEqual(out_c, src_compact)
        reg2 = DocumentRegistry(profile=AlphabetProfile.OG)
        mod_s = compile_source(src_spaced, "js", reg2)
        out_s = reconstruct_source(mod_s, reg2)
        self.assertEqual(out_s, src_spaced)
        self.assertNotEqual(out_c, out_s)


if __name__ == "__main__":
    unittest.main()
