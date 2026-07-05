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


if __name__ == "__main__":
    unittest.main()
