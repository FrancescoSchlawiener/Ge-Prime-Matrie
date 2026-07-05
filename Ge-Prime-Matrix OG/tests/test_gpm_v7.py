import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from gpm.compiler import compile_text
from gpm.format import (
    FLAG_BODY_HIER,
    FLAG_GAP_RLE,
    FLAG_STRUCT,
    GpmFormatError,
    VERSION,
    VERSION_V6,
    read_gpm,
    write_gpm,
)
from gpm.hierarchy_geom import validate_structural_partition
from gpm.model import GpmDocument, GpmHeaderEntry, GpmToken
from gpm.reader import reconstruct_text
from gpm.reconstruct_v7 import reconstruct_text_v7


class TestGpmV7(unittest.TestCase):
    def test_v7_roundtrip_with_hierarchy(self):
        text = "Hallo, Welt!\nNeue Zeile hier."
        doc, blob, _ = compile_text(text)
        self.assertEqual(blob[3], VERSION)
        flags = blob[4]
        self.assertEqual(flags & FLAG_BODY_HIER, FLAG_BODY_HIER)
        self.assertEqual(flags & FLAG_STRUCT, FLAG_STRUCT)
        self.assertEqual(flags & FLAG_GAP_RLE, FLAG_GAP_RLE)
        loaded = read_gpm(blob)
        self.assertIsNotNone(loaded.hierarchy)
        self.assertIsNotNone(loaded.interval_index)
        self.assertIsNotNone(loaded.substance_index)
        self.assertEqual(reconstruct_text(loaded), text)
        validate_structural_partition(
            len(loaded.tokens),
            loaded.hierarchy.structural.lines,
        )

    def test_v7_write_diff_assert(self):
        text = "Ok.\tTab here."
        doc, blob, _ = compile_text(text)
        loaded = read_gpm(blob)
        self.assertEqual(reconstruct_text_v7(loaded), text)

    def test_v7_gap_rle_fallback_tabs(self):
        text = "A\tB"
        doc, _, _ = compile_text(text)
        self.assertIn("\t", reconstruct_text(doc))

    def test_v6_write_still_supported(self):
        doc = GpmDocument(
            header=[GpmHeaderEntry(0, "a", "A", 3)],
            tokens=[GpmToken(0, 1, 0)],
            gaps=["", ""],
            explicit=[],
        )
        blob = write_gpm(doc, version=VERSION_V6)
        self.assertEqual(blob[3], VERSION_V6)
        loaded = read_gpm(blob)
        self.assertIsNone(getattr(loaded, "gap_rle", None) or loaded.gap_rle)

    def test_partition_mismatch_raises(self):
        text = "Ok."
        doc, _, _ = compile_text(text)
        h = doc.hierarchy
        if h and h.structural.lines:
            bad = h.structural.lines[0]
            bad.token_count += 1
        with self.assertRaises(GpmFormatError):
            write_gpm(doc, hierarchy=h)


if __name__ == "__main__":
    unittest.main()
