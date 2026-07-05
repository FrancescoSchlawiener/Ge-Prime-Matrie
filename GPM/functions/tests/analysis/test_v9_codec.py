"""Tests für v9 Block-Tree codec."""

import unittest

from alphabets import AlphabetProfile
from analysis.binary.v9_body import decode_block_tree, encode_block_tree
from analysis.blocks.registry import DocumentRegistry
from analysis.code.compile import compile_source
from analysis.code.decompile import reconstruct_source


class TestV9Codec(unittest.TestCase):
    def test_block_tree_roundtrip(self):
        reg = DocumentRegistry(profile=AlphabetProfile.OG)
        mod = compile_source("function f() {}\n", "js", reg)
        wire = encode_block_tree(mod)
        loaded = decode_block_tree(wire)
        self.assertEqual(loaded.level.value, "module")
        self.assertEqual(loaded.meta.get("trailing_whitespace"), "\n")

    def test_block_tree_col_prefix_roundtrip(self):
        reg = DocumentRegistry(profile=AlphabetProfile.OG)
        src = "  a + b"
        mod = compile_source(src, "js", reg)
        wire = encode_block_tree(mod)
        loaded = decode_block_tree(wire)
        self.assertEqual(len(loaded.sequence), len(mod.sequence))
        for orig, decoded in zip(mod.sequence, loaded.sequence):
            self.assertEqual(orig.nl, decoded.nl)
            self.assertEqual(orig.col_prefix, decoded.col_prefix)
        out = reconstruct_source(loaded, reg)
        self.assertEqual(out, src)


if __name__ == "__main__":
    unittest.main()
