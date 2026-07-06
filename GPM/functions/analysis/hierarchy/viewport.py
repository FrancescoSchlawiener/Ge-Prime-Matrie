"""Viewport-Serialisierung für I-Kurve GeometricMatrix."""

from __future__ import annotations

from analysis.blocks.build import materialize_geometry
from analysis.compile.reconstruct import reconstruct_text
from analysis.document.model import GpmDocument
from analysis.hierarchy.access import get_hierarchy
from analysis.hierarchy.span_utils import token_char_map


def serialize_viewport(document: GpmDocument) -> dict:
    materialize_geometry(document)
    text = reconstruct_text(document)
    hierarchy = get_hierarchy(document)
    structural_lines = [
        {
            "line_index": idx,
            "token_start": line.token_start,
            "token_count": line.token_count,
        }
        for idx, line in enumerate(hierarchy.structural.lines)
    ]
    token_map = [
        {
            "token_index": token_index,
            "char_start": char_start,
            "char_end": char_end,
        }
        for token_index, char_start, char_end in token_char_map(document)
    ]
    return {
        "reconstructed_text": text,
        "structural_lines": structural_lines,
        "token_char_map": token_map,
    }
