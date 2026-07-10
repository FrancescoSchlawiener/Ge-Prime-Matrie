"""Hybrid → v10 Binary Export und Roundtrip."""

import unittest

from alphabets import AlphabetProfile
from analysis.binary.format import FLAG_BLOCK_TREE, VERSION, read_gpm
from analysis.code.compile import compile_hybrid, compile_hybrid_to_gpm, verify_hybrid_reversibility
from analysis.code.decompile import reconstruct_hybrid, reconstruct_source
from analysis.compile.reconstruct import reconstruct_text


class TestV10Hybrid(unittest.TestCase):
    TEXT = "# Title\n\n```javascript\nconst x = 1;\n```\n"

    def test_hybrid_export_block_tree(self):
        doc, blob = compile_hybrid_to_gpm(self.TEXT, AlphabetProfile.OG)
        self.assertEqual(blob[3], VERSION)
        self.assertIsNotNone(doc.root_block)
        self.assertIsNotNone(doc.registry)
        flags = blob[4]
        self.assertTrue(flags & FLAG_BLOCK_TREE)
        loaded = read_gpm(blob)
        self.assertIsNotNone(loaded.root_block)
        self.assertIsNotNone(loaded.registry)

    def test_hybrid_in_memory_roundtrip(self):
        self.assertTrue(verify_hybrid_reversibility(self.TEXT, AlphabetProfile.OG))
        hybrid = compile_hybrid(self.TEXT, AlphabetProfile.OG)
        self.assertEqual(reconstruct_hybrid(hybrid), self.TEXT)

    def test_hybrid_gpm_read_roundtrip(self):
        doc, blob = compile_hybrid_to_gpm(self.TEXT, AlphabetProfile.OG)
        loaded = read_gpm(blob)
        self.assertIsNotNone(loaded.registry)
        self.assertEqual(reconstruct_text(loaded), reconstruct_text(doc))
        code_text = reconstruct_source(loaded.root_block, loaded.registry)
        self.assertIn("const x = 1", code_text)

    def test_hybrid_gpm_preserves_code_source(self):
        doc, blob = compile_hybrid_to_gpm(self.TEXT, AlphabetProfile.OG)
        loaded = read_gpm(blob)
        pre = reconstruct_source(doc.root_block, doc.registry)
        post = reconstruct_source(loaded.root_block, loaded.registry)
        self.assertEqual(post, pre)
        self.assertIn("const x = 1", post)


if __name__ == "__main__":
    unittest.main()
