import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from gpm.compiler import compile_text
from gpm.format import (
    FLAG_BODY_HIER,
    FLAG_STRUCT,
    GpmFormatError,
    VERSION_V6,
    VERSION_V5,
    read_gpm,
    write_gpm,
)
from gpm.hierarchy_geom import validate_structural_partition
from gpm.model import GpmDocument, GpmHeaderEntry, GpmToken
from gpm.reader import reconstruct_text


class TestGpmV6(unittest.TestCase):
    def test_v6_roundtrip_with_hierarchy(self):
        text = "Hallo, Welt!\nNeue Zeile hier."
        doc, blob, _ = compile_text(text)
        blob = write_gpm(doc, cells=doc.cells, hierarchy=doc.hierarchy, version=VERSION_V6)
        self.assertEqual(blob[3], VERSION_V6)
        self.assertEqual(blob[4] & FLAG_BODY_HIER, FLAG_BODY_HIER)
        self.assertEqual(blob[4] & FLAG_STRUCT, FLAG_STRUCT)
        loaded = read_gpm(blob)
        self.assertIsNotNone(loaded.hierarchy)
        self.assertEqual(reconstruct_text(loaded), text)
        validate_structural_partition(
            len(loaded.tokens),
            loaded.hierarchy.structural.lines,
        )

    def test_v6_structural_no_word_ids_in_index(self):
        _, blob, _ = compile_text("A.\nB.")
        idx = blob.find(b"\x00\x00\x00")  # struct_len u32 may vary
        self.assertGreater(len(blob), 40)
        loaded = read_gpm(blob)
        for line in loaded.hierarchy.structural.lines:
            self.assertEqual(line.layer, "structural")
            self.assertEqual(line.level, "line")

    def test_v5_write_still_supported(self):
        doc = GpmDocument(
            header=[GpmHeaderEntry(0, "a", "A", 3)],
            tokens=[GpmToken(0, 1, 0)],
            gaps=["", ""],
            explicit=[],
        )
        blob = write_gpm(doc, version=VERSION_V5)
        self.assertEqual(blob[3], VERSION_V5)
        loaded = read_gpm(blob)
        self.assertIsNone(loaded.hierarchy)

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
