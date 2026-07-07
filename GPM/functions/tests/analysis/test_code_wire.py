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

    def test_v4_preserves_c_and_h_geometry(self):
        reg = DocumentRegistry(profile=AlphabetProfile.OG)
        src = "function add(a, b) { return a + b; }\nlet y = abc123;\n"
        mod = compile_source(src, "js", reg)
        wire = encode_code_module(mod, reg)
        self.assertEqual(wire[0], 4)  # v4 Version-Byte
        _, loaded_reg = decode_code_module(wire)
        # C-Substanz/perm_index (auch sehr grosse Werte) exakt erhalten.
        for i in range(len(reg.c_entries)):
            self.assertEqual(loaded_reg.c_substance(i), reg.c_substance(i))
            self.assertEqual(loaded_reg.c_perm_index(i), reg.c_perm_index(i))
        # H-Substanz deterministisch identisch.
        for i in range(len(reg.h_entries)):
            self.assertEqual(loaded_reg.h_substance(i), reg.h_substance(i))

    def test_v3_blob_backward_compatible(self):
        """Alter v3-Blob (ohne C/H-Geometrie) wird gelesen; Geometrie rekonstruiert."""
        import struct

        from gpm_types.hi.codec import decode_hi
        from analysis.code import wire as W
        from analysis.code.wire import decode_code_module, encode_block_tree_v2

        reg = DocumentRegistry(profile=AlphabetProfile.OG)
        src = "function add(a, b) { return a + b; }\nlet y = abc123;\n"
        mod = compile_source(src, "js", reg)

        # v3-Registry-Layout manuell (ohne die v4-Zusatzfelder).
        parts = [W._pack_utf16(reg.profile.value)]
        parts.append(struct.pack("<I", len(reg.s_entries)))
        for e in reg.s_entries:
            parts.append(W._pack_utf16(e.word_canonical))
            parts.append(W._pack_utf16(e.word_normalized))
            parts.append(struct.pack("<QQ", e.substance & 0xFFFFFFFFFFFFFFFF, e.perm_index & 0xFFFFFFFFFFFFFFFF))
        parts.append(struct.pack("<I", len(reg.n_entries)))
        for i in range(len(reg.n_entries)):
            parts.append(W._pack_utf16(reg.n_display(i)))
        parts.append(struct.pack("<I", len(reg.d_entries)))
        parts.append(struct.pack("<I", len(reg.c_entries)))
        for e in reg.c_entries:
            ob = (e.origin.value if hasattr(e.origin, "value") else str(e.origin)).encode("ascii")
            parts.append(struct.pack("<B", len(ob)))
            parts.append(ob)
            parts.append(W._pack_utf16(e.key_bytes.decode("utf-8", "replace")))
        parts.append(struct.pack("<I", len(reg.h_entries)))
        for p in reg.h_entries:
            parts.append(W._pack_utf16(decode_hi(p)))
            parts.append(struct.pack("<H", len(p.segments)))
            for s in p.segments:
                tb = s.tag.encode("ascii")
                parts.append(struct.pack("<B", len(tb)))
                parts.append(tb)
                parts.append(W._pack_utf16(s.value))
        regbytes = b"".join(parts)
        block = encode_block_tree_v2(mod)
        v3blob = struct.pack("<BII", 3, len(block), len(regbytes)) + block + regbytes

        loaded_mod, loaded_reg = decode_code_module(v3blob)
        self.assertEqual(reconstruct_source(loaded_mod, loaded_reg), src)
        # C-Geometrie aus dem Klartext rekonstruiert (nicht verloren).
        for i in range(len(reg.c_entries)):
            self.assertEqual(loaded_reg.c_substance(i), reg.c_substance(i))

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
