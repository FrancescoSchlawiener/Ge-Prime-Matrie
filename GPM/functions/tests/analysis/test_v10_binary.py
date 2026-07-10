"""Tests für .gpm v10 mit SI-only Genom."""

import unittest

from alphabets import AlphabetProfile
from analysis.binary.format import FLAG_GENOME_SI, VERSION, VERSION_V9, read_gpm, write_gpm
from analysis.compile.compiler import compile_text, compile_text_to_gpm
from analysis.compile.reconstruct import reconstruct_text


class TestV10Binary(unittest.TestCase):
    def test_v10_default_version(self):
        _, blob, _ = compile_text_to_gpm("Hallo Welt.", AlphabetProfile.OG)
        self.assertEqual(blob[3], VERSION)
        self.assertTrue(blob[4] & FLAG_GENOME_SI)

    def test_v10_roundtrip(self):
        for source in (
            "Hallo Welt.",
            "Straße",
            "HaLlo Welt",
            "listen silent",
        ):
            with self.subTest(source=source):
                _, blob, _ = compile_text_to_gpm(source, AlphabetProfile.OG)
                loaded = read_gpm(blob)
                self.assertEqual(reconstruct_text(loaded), source)

    def test_v10_smaller_than_v9_genome(self):
        source = "Morgenröte Gedanken Moral Vorurteil " * 5
        _, blob_v10, _ = compile_text_to_gpm(source, AlphabetProfile.OG, version=VERSION)
        _, blob_v9, _ = compile_text_to_gpm(source, AlphabetProfile.OG, version=VERSION_V9)
        self.assertLess(len(blob_v10), len(blob_v9))

    def test_v10_genome_has_no_utf8_strings(self):
        doc, _ = compile_text("Francesco Schauer", AlphabetProfile.OG)
        blob = write_gpm(doc)
        payload_start = 29
        # Profile block + empty registry (2 bytes) + genome only before body
        profile_len = 1 + len(b"og")
        genome_start = payload_start + profile_len + 2
        genome_end = genome_start
        for entry in doc.header:
            s_bytes = 2 + 4  # class byte + substance for short words
            i_bytes = 2
            genome_end += 1 + s_bytes + i_bytes
        genome_slice = blob[genome_start:genome_end]
        self.assertNotIn(b"Francesco", genome_slice)
        self.assertNotIn(b"FRANCESCO", genome_slice)


if __name__ == "__main__":
    unittest.main()
