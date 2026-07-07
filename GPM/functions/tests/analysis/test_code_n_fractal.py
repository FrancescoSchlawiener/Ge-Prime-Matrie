"""Fraktale N(I) — Ziffern-Pointer mit Substanz/Checksum-Identität."""

import unittest

from alphabets import AlphabetProfile
from analysis.blocks.registry import DocumentRegistry, NComposite
from analysis.code.compile import compile_source, verify_reversibility
from analysis.code.decompile import reconstruct_source
from gpm_types.ni.registry import checksum_n
from gpm_types.ni.substance import substance_n


class TestCodeNFractal(unittest.TestCase):
    def _all_refs(self, node):
        for r in node.sequence:
            yield r
        for c in node.children:
            yield from self._all_refs(c)

    def test_eleven_single_composite_ptr(self):
        reg = DocumentRegistry(profile=AlphabetProfile.OG)
        mod = compile_source("let x = 11;\n", "js", reg)
        n_refs = [r for r in self._all_refs(mod) if r.kind.value == "N"]
        # Ganzes bleibt EIN adressierbarer Pointer.
        self.assertEqual(len(n_refs), 1)
        entry = reg.n_entries[n_refs[0].ptr_id]
        # Komposit trägt echte GPM-Identität (Substanz/Checksum), Literal roh.
        self.assertIsInstance(entry, NComposite)
        self.assertEqual(entry.literal, "11")
        self.assertEqual(len(entry.digit_ptrs), 2)
        self.assertEqual(entry.digit_ptrs[0], entry.digit_ptrs[1])
        self.assertEqual(entry.substance, substance_n("11"))
        self.assertEqual(entry.checksum, checksum_n("11"))
        self.assertEqual(reg.n_display(n_refs[0].ptr_id), "11")
        self.assertEqual(reg.n_substance(n_refs[0].ptr_id), substance_n("11"))

    def test_atoms_reused_composites_grow_linearly(self):
        reg = DocumentRegistry(profile=AlphabetProfile.OG)
        # Viele mehrstellige Literale mit denselben Ziffern.
        compile_source("a=11; b=12; c=21; d=112; e=121;\n", "js", reg)
        atom_entries = [e for e in reg.n_entries if isinstance(e, int)]
        composite_entries = [e for e in reg.n_entries if isinstance(e, NComposite)]
        # Atome werden wiederverwendet: nur die tatsächlich genutzten Ziffern.
        self.assertLessEqual(len(atom_entries), 10)
        self.assertEqual(set(atom_entries), {1, 2})
        # Komposite wachsen linear mit eindeutigen Zahlenräumen.
        literals = {c.literal for c in composite_entries}
        self.assertEqual(literals, {"11", "12", "21", "112", "121"})

    def test_registry_has_atoms_and_composites(self):
        reg = DocumentRegistry(profile=AlphabetProfile.OG)
        compile_source("a=11; b=112;\n", "js", reg)
        displays = {reg.n_display(i) for i in range(len(reg.n_entries))}
        self.assertIn("11", displays)
        self.assertIn("112", displays)
        self.assertTrue(any(isinstance(e, NComposite) for e in reg.n_entries))

    def test_same_literal_shares_ptr_distinct_literals_differ(self):
        reg = DocumentRegistry(profile=AlphabetProfile.OG)
        mod = compile_source("a=11; b=11; c=112;\n", "js", reg)
        n_refs = [r for r in self._all_refs(mod) if r.kind.value == "N"]
        by_literal: dict[str, set[int]] = {}
        for ref in n_refs:
            by_literal.setdefault(reg.n_display(ref.ptr_id), set()).add(ref.ptr_id)
        # "11" zweimal → derselbe ptr_id (Dedup über Fraktal-Struktur).
        self.assertEqual(len(by_literal["11"]), 1)
        # "11" ≠ "112".
        self.assertNotEqual(by_literal["11"], by_literal["112"])

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
