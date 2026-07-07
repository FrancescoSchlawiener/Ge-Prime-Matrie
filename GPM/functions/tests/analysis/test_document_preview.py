"""Tests für Dokument-Previews und Referenz-Integrität."""

from __future__ import annotations

import unittest

from alphabets import AlphabetProfile
from analysis.compile.compiler import compile_text
from analysis.document.model import GpmHeaderEntry, GpmToken
from analysis.document.preview import (
    assert_referential_integrity,
    build_genome_preview,
    build_geometry_preview,
)
from gpm_types.classify import PayloadKind


class TestDocumentPreview(unittest.TestCase):
  def test_hallo_francesco_integrity_and_previews(self) -> None:
    doc, _ = compile_text("HALLO FRANCESCO", AlphabetProfile("og"))
    assert_referential_integrity(doc)

    genome = build_genome_preview(doc)
    geometry = build_geometry_preview(doc)

    self.assertEqual(len(genome), 2)
    self.assertEqual(len(geometry), 2)
    self.assertNotIn("perm_index", genome[0])

    genome_by_word = {row["word"]: row["substance"] for row in genome}
    for row in geometry:
      self.assertEqual(row["substance"], genome_by_word[row["word"]])
      self.assertGreaterEqual(row["perm_index"], 1)

  def test_invalid_word_id_raises(self) -> None:
    doc, _ = compile_text("A", AlphabetProfile("og"))
    doc.tokens[0] = GpmToken(
      word_id=99,
      perm_index=doc.tokens[0].perm_index,
      case_code=doc.tokens[0].case_code,
      payload_kind=PayloadKind.S,
    )
    with self.assertRaises(ValueError):
      assert_referential_integrity(doc)

  def test_invalid_perm_index_raises(self) -> None:
    doc, _ = compile_text("A", AlphabetProfile("og"))
    doc.tokens[0] = GpmToken(
      word_id=0,
      perm_index=999999999,
      case_code=doc.tokens[0].case_code,
      payload_kind=PayloadKind.S,
    )
    with self.assertRaises(ValueError):
      assert_referential_integrity(doc)


if __name__ == "__main__":
  unittest.main()
