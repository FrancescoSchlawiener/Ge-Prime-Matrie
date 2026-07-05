"""Token-I-Kurve und Zell-Kurven."""

from __future__ import annotations

from collections import Counter

from analysis.blocks.build import materialize_geometry
from analysis.document.model import GpmDocument
from perm.multiset import perm_space


def extract_i_curve(document: GpmDocument) -> list[dict]:
    materialize_geometry(document)
    points: list[dict] = []
    prev_ratio: float | None = None
    for i, token in enumerate(document.tokens):
        entry = document.header[token.word_id]
        ps = perm_space(Counter(entry.word_normalized))
        if ps <= 0:
            ps = max(1, entry.perm_index)
        ratio = token.perm_index / ps if ps else 0.0
        delta = 0.0 if prev_ratio is None else abs(ratio - prev_ratio)
        prev_ratio = ratio
        points.append(
            {
                "index": i,
                "perm_index": token.perm_index,
                "perm_space": ps,
                "i_ratio": round(ratio, 6),
                "delta_ratio": round(delta, 6),
                "substance": entry.substance,
            }
        )
    return points


def extract_cell_curve(document: GpmDocument) -> list[dict]:
    materialize_geometry(document)
    points: list[dict] = []
    prev_i: float | None = None
    for cell in document.cells:
        ratio = cell.perm_index / cell.perm_space if cell.perm_space else 0.0
        delta = 0.0 if prev_i is None else abs(ratio - prev_i)
        prev_i = ratio
        sk_hash = hash(tuple(cell.frequencies))
        points.append(
            {
                "token_start": cell.token_start,
                "token_count": cell.token_count,
                "i_satz_ratio": round(ratio, 6),
                "delta_ratio": round(delta, 6),
                "skeleton_hash": sk_hash,
                "perm_space": cell.perm_space,
            }
        )
    return points
