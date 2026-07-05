import sys
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from ge_prime.multiset_geom import perm_decode, perm_index, perm_space
from gpm.cell_geom import (
    build_cell_geometry,
    build_document_cells,
    cells_cover_document,
    expand_cells_to_tokens,
    split_into_slices,
)
from gpm.compiler import compile_text
from gpm.format import FLAG_BODY_CELL, VERSION, VERSION_V4, read_gpm, write_gpm
from gpm.model import GpmDocument, GpmHeaderEntry, GpmToken
from gpm.reader import reconstruct_text
from pipeline.normalize import CASE_EXPLICIT, CASE_LOWER
from pipeline.process import process_token


class TestMultisetGeom(unittest.TestCase):
    def test_papa_isst_papa_spec(self):
        counts = Counter({0: 2, 1: 1})
        seq = [0, 1, 0]
        self.assertEqual(perm_space(counts), 3)
        self.assertEqual(perm_index(seq, counts), 2)
        self.assertEqual(perm_decode(counts, 2), seq)

    def test_aba_ca_spec(self):
        counts = Counter({0: 3, 1: 1, 2: 1})
        seq = [0, 1, 0, 2, 0]
        self.assertEqual(perm_space(counts), 20)
        self.assertEqual(perm_index(seq, counts), 8)
        self.assertEqual(perm_decode(counts, 8), seq)

    def test_roundtrip_random(self):
        counts = Counter({0: 2, 1: 2, 2: 1})
        for i in range(1, perm_space(counts) + 1):
            seq = perm_decode(counts, i)
            self.assertEqual(perm_index(seq, counts), i)


class TestCellGeom(unittest.TestCase):
    def _tokens_from_words(self, words: list[str]) -> tuple[list[GpmToken], list[GpmHeaderEntry]]:
        header: list[GpmHeaderEntry] = []
        dictionary: dict[str, int] = {}
        tokens: list[GpmToken] = []
        for word in words:
            processed = process_token(word)
            assert processed is not None
            canonical = word.lower()
            if canonical not in dictionary:
                wid = len(header)
                dictionary[canonical] = wid
                header.append(
                    GpmHeaderEntry(
                        wid,
                        canonical,
                        processed.word_normalized,
                        processed.substance,
                    )
                )
            tokens.append(
                GpmToken(
                    dictionary[canonical],
                    processed.perm_index,
                    CASE_LOWER,
                )
            )
        return tokens, header

    def test_papa_isst_papa_cell(self):
        tokens, header = self._tokens_from_words(["PAPA", "ISST", "PAPA"])
        cell = build_cell_geometry(tokens, token_start=0, explicit_map={})
        self.assertEqual(cell.perm_space, 3)
        self.assertEqual(cell.perm_index, 2)
        self.assertEqual(len(cell.categories), 2)
        expanded = expand_cells_to_tokens([cell])
        self.assertEqual(len(expanded), 3)
        self.assertEqual(expanded[0].word_id, expanded[2].word_id)

    def test_split_respects_max(self):
        slices = split_into_slices(55, [""] + [" "] * 54 + [""])
        for sl in slices:
            self.assertLessEqual(sl.token_end - sl.token_start, 50)

    def test_explicit_separate_categories(self):
        tokens = [
            GpmToken(0, 1, CASE_EXPLICIT),
            GpmToken(0, 1, CASE_EXPLICIT),
        ]
        header = [GpmHeaderEntry(0, "test", "TEST", 6)]
        explicit = {0: "TeSt", 1: "tEsT"}
        cell = build_cell_geometry(tokens, token_start=0, explicit_map=explicit)
        self.assertEqual(len(cell.categories), 2)


class TestGpmV5Roundtrip(unittest.TestCase):
    def test_compile_v5_lossless(self):
        text = "PAPA ISST PAPA. Hallo Welt!"
        doc, blob, stats = compile_text(text)
        self.assertTrue(stats.lossless)
        self.assertEqual(blob[3], VERSION)
        self.assertTrue(stats.zellen_anzahl >= 1)
        loaded = read_gpm(blob)
        self.assertEqual(reconstruct_text(loaded), text)

    def test_multi_cell_long_text(self):
        words = [f"wort{i}" for i in range(120)]
        text = " ".join(words) + "."
        doc, blob, stats = compile_text(text)
        self.assertTrue(stats.lossless)
        self.assertGreater(stats.zellen_anzahl, 1)
        self.assertEqual(reconstruct_text(read_gpm(blob)), text)

    def test_v4_write_still_works(self):
        doc = GpmDocument(
            header=[GpmHeaderEntry(0, "a", "A", 3)],
            tokens=[GpmToken(0, 1, 0)],
            gaps=["", ""],
            explicit=[],
        )
        blob = write_gpm(doc, version=VERSION_V4)
        self.assertEqual(blob[3], VERSION_V4)
        self.assertEqual(reconstruct_text(read_gpm(blob)), "a")

    def test_v5_cell_body_flag(self):
        _, blob, stats = compile_text("PAPA ISST PAPA")
        if stats.body_mode == "cell":
            self.assertTrue(blob[4] & FLAG_BODY_CELL)


if __name__ == "__main__":
    unittest.main()
