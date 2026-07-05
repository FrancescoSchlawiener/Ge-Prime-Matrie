"""Substanz-Kurve entlang Token-Folge."""

from __future__ import annotations

from analysis.blocks.build import materialize_geometry
from analysis.document.model import GpmDocument
from analysis.substance.transition import transition_fields


def extract_substance_curve(document: GpmDocument) -> list[dict]:
    materialize_geometry(document)
    points: list[dict] = []
    prev_s: int | None = None
    for i, token in enumerate(document.tokens):
        s = document.header[token.word_id].substance
        row: dict = {"index": i, "substance": s}
        if prev_s is not None:
            row.update(transition_fields(prev_s, s))
        points.append(row)
        prev_s = s
    return points
