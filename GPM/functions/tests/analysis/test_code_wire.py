"""Tests für Code-Wire (Blockbaum v2 + Registry)."""

import unittest

from alphabets import AlphabetProfile
from analysis.blocks.registry import DocumentRegistry
from analysis.code.compile import compile_source
from analysis.code.decompile import reconstruct_source
from analysis.code.wire import decode_code_module, encode_code_module


class TestCodeWire(unittest.TestCase):
    def test_js_roundtrip(self):
        reg = DocumentRegistry(profile=AlphabetProfile.OG)
        src = "function add(a,b){return a+b;}\n"
        mod = compile_source(src, "js", reg)
        wire = encode_code_module(mod, reg)
        loaded_mod, loaded_reg = decode_code_module(wire)
        out = reconstruct_source(loaded_mod, loaded_reg)
        self.assertEqual(out, src)

    def test_html_child_meta_roundtrip(self):
        reg = DocumentRegistry(profile=AlphabetProfile.OG)
        src = "<script>\nif (true) {\n  x = 1;\n}\n</script>\n"
        mod = compile_source(src, "html", reg)
        wire = encode_code_module(mod, reg)
        loaded_mod, loaded_reg = decode_code_module(wire)
        out = reconstruct_source(loaded_mod, loaded_reg)
        self.assertEqual(out, src)

    def test_col_prefix_and_bigint_meta(self):
        reg = DocumentRegistry(profile=AlphabetProfile.OG)
        src = "  a + 42n\n"
        mod = compile_source(src, "js", reg)
        wire = encode_code_module(mod, reg)
        loaded_mod, loaded_reg = decode_code_module(wire)
        for orig, decoded in zip(mod.sequence, loaded_mod.sequence):
            self.assertEqual(orig.nl, decoded.nl)
            self.assertEqual(orig.col_prefix, decoded.col_prefix)
            self.assertEqual(orig.meta.get("bigint"), decoded.meta.get("bigint"))
        out = reconstruct_source(loaded_mod, loaded_reg)
        self.assertEqual(out, src)

    def test_block_tree_v2_meta_string_length_is_u32(self):
        """Regression: u16-Meta-Strings brachen TS-Decoder (Invalid typed array length)."""
        import struct

        from analysis.blocks.codec import decode_block_tree_v2, encode_block_tree_v2
        from analysis.blocks.node import BlockLevel, BlockNode
        from analysis.code.envelope import BlockEnvelope

        node = BlockNode(
            block_id=1,
            level=BlockLevel.CODE_BLOCK,
            parent_id=0,
            sequence=[],
            meta={"envelope": int(BlockEnvelope.TAG), "open_syntax": "<DIV>"},
        )
        wire = encode_block_tree_v2(node)
        self.assertIn(bytes([int(BlockEnvelope.TAG)]), wire)
        self.assertIn(struct.pack("<I", 5) + b"<DIV>", wire)
        decoded = decode_block_tree_v2(wire)
        self.assertEqual(decoded.meta.get("envelope"), int(BlockEnvelope.TAG))
        self.assertEqual(decoded.meta.get("open_syntax"), "<DIV>")

        from analysis.binary.format import read_gpm
        from analysis.code.compile import compile_source_to_gpm

        src = "function f() {}\n"
        doc, blob = compile_source_to_gpm(src, "js", AlphabetProfile.OG)
        loaded = read_gpm(blob)
        self.assertIsNotNone(doc.root_block)
        self.assertIsNotNone(loaded.root_block)


if __name__ == "__main__":
    unittest.main()
