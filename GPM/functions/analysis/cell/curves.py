"""Zell-Kurven — I_Satz und Skeleton-Übergänge."""

from __future__ import annotations

from analysis.cell.geom import build_document_cells
from analysis.document.model import GpmDocument


def extract_cell_transitions(document: GpmDocument) -> list[dict]:
    cells = document.cells or build_document_cells(document)
    points: list[dict] = []
    prev_ratio: float | None = None
    for cell in cells:
        ratio = cell.perm_index / cell.perm_space if cell.perm_space else 0.0
        delta = 0.0 if prev_ratio is None else abs(ratio - prev_ratio)
        prev_ratio = ratio
        points.append(
            {
                "token_start": cell.token_start,
                "token_count": cell.token_count,
                "i_satz_ratio": round(ratio, 6),
                "delta_ratio": round(delta, 6),
                "skeleton": list(cell.frequencies),
            }
        )
    return points
