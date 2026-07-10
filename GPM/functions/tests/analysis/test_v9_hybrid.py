"""Hybrid → v9 Binary Export."""

import unittest

from alphabets import AlphabetProfile
from analysis.binary.format import FLAG_BLOCK_TREE, VERSION, VERSION_V9, read_gpm
from analysis.code.compile import compile_hybrid_to_gpm, verify_hybrid_reversibility


class TestV9Hybrid(unittest.TestCase):
    def test_hybrid_export_block_tree(self):
        text = "# Title\n\n```javascript\nconst x = 1;\n```\n"
        self.assertTrue(verify_hybrid_reversibility(text))
        doc, blob = compile_hybrid_to_gpm(text, AlphabetProfile.OG)
        self.assertEqual(blob[3], VERSION)
        self.assertIsNotNone(doc.root_block)
        self.assertIsNotNone(doc.registry)
        flags = blob[4]
        self.assertTrue(flags & FLAG_BLOCK_TREE)
        loaded = read_gpm(blob)
        self.assertIsNotNone(loaded.root_block)


if __name__ == "__main__":
    unittest.main()
