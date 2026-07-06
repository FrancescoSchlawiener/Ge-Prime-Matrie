"""Tests für .gpm Binary-Writer und Reader."""

import unittest

from alphabets import AlphabetProfile
from analysis.binary.format import MAGIC_PREFIX, VERSION, read_gpm, write_gpm
from analysis.binary.reader import analyze_gpm, load_gpm
from analysis.compile.compiler import compile_text, compile_text_to_gpm
from analysis.compile.reconstruct import reconstruct_text
from analysis.document.invariants import assert_gap_symmetry


class TestBinaryGpm(unittest.TestCase):
    def setUp(self):
        self.profile = AlphabetProfile.OG

    def _roundtrip(self, source: str, *, use_gap_rle: bool = False) -> None:
        doc, blob, stats = compile_text_to_gpm(
            source, self.profile, use_gap_rle=use_gap_rle
        )
        self.assertTrue(blob.startswith(MAGIC_PREFIX))
        self.assertGreater(stats.file_bytes, 0)
        self.assertEqual(reconstruct_text(doc), source)

        loaded = read_gpm(blob)
        assert_gap_symmetry(loaded)
        self.assertEqual(loaded.profile, self.profile)
        self.assertEqual(reconstruct_text(loaded), source)

    def test_hallo_welt_roundtrip(self):
        self._roundtrip("Hallo Welt")

    def test_gap_matrix_roundtrip(self):
        for source in (" Hallo", "Hallo ", ",Hallo", "Hallo,Welt", "Hallo, Welt."):
            self._roundtrip(source)

    def test_explicit_case_roundtrip(self):
        self._roundtrip("HaLlo Welt")

    def test_gap_rle_mode(self):
        self._roundtrip("Hallo … Welt!", use_gap_rle=True)

    def test_write_read_direct(self):
        doc, _ = compile_text("Straße", self.profile)
        blob = write_gpm(doc)
        loaded = load_gpm(blob)
        self.assertEqual(reconstruct_text(loaded), "Straße")

    def test_analyze_gpm(self):
        _, blob, _ = compile_text_to_gpm("Test", self.profile)
        analysis = analyze_gpm(blob)
        self.assertEqual(analysis.version, VERSION)
        self.assertEqual(analysis.body_count, 1)
        self.assertEqual(analysis.reconstructed, "Test")

    def test_v4_write_read(self):
        doc, _ = compile_text("HALLO", self.profile)
        blob = write_gpm(doc, version=4)
        loaded = read_gpm(blob)
        self.assertEqual(loaded.profile, AlphabetProfile.OG)
        self.assertEqual(reconstruct_text(loaded), "HALLO")

    def test_crc_corruption_detected(self):
        _, blob, _ = compile_text_to_gpm("Test", self.profile)
        bad = bytearray(blob)
        bad[-2] ^= 0xFF
        with self.assertRaises(Exception):
            read_gpm(bytes(bad))

    def test_v9_long_prose_roundtrip(self):
        """Regression: Zell-Perm-Indizes > 65535 dürfen write_gpm nicht brechen."""
        words = [
            "Morgenröte", "Gedanken", "Moral", "Vorurteil", "Pulvergeruch",
            "Feinheit", "Nüstern", "Geschütz", "Schluß", "Kanonschuß",
            "Vorsicht", "Anbetung", "Bosheit", "Seegetier", "Felsen",
            "Genua", "Heimlichkeiten", "Erinnerung", "Eidechsen", "Grausamkeit",
            "Griechengott", "Eidechslein", "Morgenröten", "Inschrift",
            "Umwertung", "Moralwerte", "Verachtet", "Verflucht", "Zärtlichkeit",
            "Gewissen", "Dasein", "Selbstbesinnung", "Menschheit", "Zufall",
            "Priester", "Verneinung", "Verderbnis", "décadence", "Instinkt",
            "Herkunft", "Bibel", "Weisheit", "Schlechtweggekommenen",
            "Arglistig", "Rachsüchtigen", "Heiligen", "Verleumdern",
            "Physiologe", "Selbsterhaltung", "Solidarität", "Entarteten",
            "Seele", "Geist", "freier", "Willen", "Bleichsucht", "décadence",
        ]
        source = (
            "Morgenröte\nGedanken über die Moral als Vorurteil\n1\n"
            "[1124] Mit diesem Buche beginnt mein Feldzug gegen die Moral. "
            + " ".join(words * 3)
            + " Nicht daß es den geringsten Pulvergeruch an sich hätte."
        )
        self._roundtrip(source)

    def test_registry_c_large_perm_index(self):
        """Direkt: C-Registry mit perm_index > 65535 serialisierbar."""
        from analysis.binary.format import _build_registry_c
        from analysis.blocks.context import COrigin
        from analysis.blocks.registry import DocumentRegistry, StructureEntry

        reg = DocumentRegistry(profile=self.profile)
        reg.c_entries.append(
            StructureEntry(
                entry_id=0,
                key_bytes=b"\x01\x02",
                substance=1,
                perm_index=28_034_225,
                perm_space=28_034_225,
                origin=COrigin.GEOM,
            )
        )
        doc, _ = compile_text("Test", self.profile)
        doc.registry = reg
        block = _build_registry_c(doc)
        self.assertGreater(len(block), 2)

if __name__ == "__main__":
    unittest.main()
