"""Denormalisierte Dokument-Previews und Referenz-Integrität."""

from __future__ import annotations

from analysis.binary.int_codec import perm_space_size
from analysis.document.invariants import assert_gap_symmetry
from analysis.document.model import GpmDocument

DEFAULT_PREVIEW_LIMIT = 500


def assert_referential_integrity(document: GpmDocument) -> None:
    """Gatekeeper: word_id-Grenzen, I im Permutationsraum, Gap-Symmetrie."""
    header = document.header
    if not header and document.tokens:
        raise ValueError("Token-Stream ohne Genom-Header.")

    assert_gap_symmetry(document)

    for idx, token in enumerate(document.tokens):
        word_id = token.word_id
        if word_id < 0 or word_id >= len(header):
            raise ValueError(
                f"Ungültige word_id {word_id} an Position {idx} "
                f"(Header-Länge {len(header)})."
            )
        entry = header[word_id]
        n = perm_space_size(entry.word_normalized)
        if not 1 <= token.perm_index <= n:
            raise ValueError(
                f"Index I={token.perm_index} außerhalb N={n} "
                f"für Wort {entry.word_canonical!r} an Position {idx}."
            )


def build_genome_preview(
    document: GpmDocument,
    *,
    limit: int = DEFAULT_PREVIEW_LIMIT,
) -> list[dict]:
    assert_referential_integrity(document)
    return [
        {
            "word_id": entry.word_id,
            "word": entry.word_canonical,
            "word_normalized": entry.word_normalized,
            "substance": entry.substance,
        }
        for entry in document.header[:limit]
    ]


def build_geometry_preview(
    document: GpmDocument,
    *,
    limit: int = DEFAULT_PREVIEW_LIMIT,
) -> list[dict]:
    assert_referential_integrity(document)
    rows: list[dict] = []
    for idx, token in enumerate(document.tokens[:limit]):
        entry = document.header[token.word_id]
        rows.append(
            {
                "position": idx,
                "word": entry.word_canonical,
                "word_normalized": entry.word_normalized,
                "substance": entry.substance,
                "perm_index": token.perm_index,
                "case_code": token.case_code,
            }
        )
    return rows
