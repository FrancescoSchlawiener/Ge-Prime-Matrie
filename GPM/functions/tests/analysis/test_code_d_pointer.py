"""D(I) Code-Pfad — Pointer-Triple-Dedup + pointer-first Rekonstruktion."""

import unittest

from alphabets import AlphabetProfile
from analysis.blocks.context import ParseContext, ParseDomain
from analysis.blocks.registry import DCodeEntry, DocumentRegistry
from analysis.code.intern import intern_d_decimal

CTX = ParseContext(domain=ParseDomain.CODE, language_id="js")


class TestCodeDPointer(unittest.TestCase):
    def test_equivalent_decimals_share_ptr_via_triple(self):
        reg = DocumentRegistry(profile=AlphabetProfile.OG)
        r1 = intern_d_decimal("4.16", 0, "", reg, CTX)
        r2 = intern_d_decimal("4.16", 0, "", reg, CTX)
        r3 = intern_d_decimal("3.5", 0, "", reg, CTX)
        # Gleiche Dezimale teilen ptr_id über das Pointer-Triple.
        self.assertEqual(r1.ptr_id, r2.ptr_id)
        # Verschiedene Dezimale bekommen eigene ptr_ids.
        self.assertNotEqual(r1.ptr_id, r3.ptr_id)
        self.assertEqual(len(reg.d_entries), 2)

    def test_dedup_key_is_pointer_triple_not_string(self):
        reg = DocumentRegistry(profile=AlphabetProfile.OG)
        intern_d_decimal("4.16", 0, "", reg, CTX)
        entry = reg.d_entries[0]
        self.assertIsInstance(entry, DCodeEntry)
        triple = (entry.whole_ptr, entry.den_reduced_ptr, entry.ggt_ptr)
        # Der Pointer-Triple-Index ist die Identitätsquelle.
        self.assertIn(triple, reg._d_by_triple)
        self.assertEqual(reg._d_by_triple[triple], 0)

    def test_d_relation_reconstructed_from_n_pointers(self):
        reg = DocumentRegistry(profile=AlphabetProfile.OG)
        r = intern_d_decimal("4.16", 0, "", reg, CTX)
        rel = reg.d_relation(r.ptr_id)
        self.assertIsNotNone(rel)
        self.assertEqual((rel.whole, rel.den_reduced, rel.ggt), (4, 25, 4))
        # Werte kommen aus den N-Pointern der Registry.
        entry = reg.d_entries[r.ptr_id]
        self.assertEqual(reg.n_val(entry.whole_ptr), 4)
        self.assertEqual(reg.n_val(entry.den_reduced_ptr), 25)

    def test_d_display_pointer_first_preserves_separator(self):
        reg = DocumentRegistry(profile=AlphabetProfile.OG)
        r_dot = intern_d_decimal("4.16", 0, "", reg, CTX)
        # Rekonstruktion aus N-Pointern, aber originales Trennzeichen erhalten.
        self.assertEqual(reg.d_display(r_dot.ptr_id), "4.16")
        reg2 = DocumentRegistry(profile=AlphabetProfile.OG)
        r_comma = intern_d_decimal("4,16", 0, "", reg2, CTX)
        self.assertEqual(reg2.d_display(r_comma.ptr_id), "4,16")

    def test_d_display_tamper_proof(self):
        reg = DocumentRegistry(profile=AlphabetProfile.OG)
        r = intern_d_decimal("3.5", 0, "", reg, CTX)
        # display-String verfälschen: Rekonstruktion muss trotzdem aus Pointern stimmen.
        reg.d_entries[r.ptr_id].display = "9.9"
        self.assertEqual(reg.d_display(r.ptr_id), "3.5")


if __name__ == "__main__":
    unittest.main()
