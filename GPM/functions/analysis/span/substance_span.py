"""kgV über Token-Spans — arithmetischer Türsteher vor teuren Alignment-Loops."""

from __future__ import annotations

from analysis.algebra.fold import fold_lcm_span, passes_kgv_gate
from analysis.document.model import GpmDocument


def local_kgv(document: GpmDocument, token_start: int, token_count: int) -> int:
    if token_count <= 0:
        return 0
    substances = [
        document.header[document.tokens[token_start + i].word_id].substance
        for i in range(token_count)
        if token_start + i < len(document.tokens)
    ]
    if not substances:
        return 1
    return fold_lcm_span(substances)


__all__ = ["local_kgv", "passes_kgv_gate"]
