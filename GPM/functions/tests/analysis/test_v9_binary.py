"""Tests für .gpm v9 mit Fraktal-Geometrie."""

import unittest

from alphabets import AlphabetProfile
from analysis.binary.format import VERSION, read_gpm
from analysis.compile.compiler import compile_text_to_gpm
from analysis.compile.reconstruct import reconstruct_text
from analysis.document.invariants import assert_gap_symmetry
from analysis.blocks.build import materialize_geometry


class TestV9Binary(unittest.TestCase):
    def test_v9_default_version(self):
        _, blob, _ = compile_text_to_gpm("Hallo Welt.", AlphabetProfile.OG)
        self.assertEqual(blob[3], VERSION)

    def test_v9_roundtrip_geometry(self):
        doc, blob, _ = compile_text_to_gpm("Hallo Welt.", AlphabetProfile.OG, version=VERSION)
        materialize_geometry(doc)
        self.assertIsNotNone(doc.root_block)
        self.assertIsNotNone(doc.cells)

        loaded = read_gpm(blob)
        assert_gap_symmetry(loaded)
        self.assertEqual(reconstruct_text(loaded), "Hallo Welt.")

    def test_v9_multiline_roundtrip(self):
        source = "Erster Satz.\nZweiter Satz."
        _, blob, _ = compile_text_to_gpm(source, AlphabetProfile.OG, version=VERSION)
        loaded = read_gpm(blob)
        self.assertEqual(reconstruct_text(loaded), source)


if __name__ == "__main__":
    unittest.main()
