"""kgV über Token-Spans — arithmetischer Türsteher vor teuren Alignment-Loops."""

from __future__ import annotations

import math

from gpm.model import GpmDocument


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
    result = substances[0]
    for s in substances[1:]:
        result = math.lcm(result, s)
    return result


def passes_kgv_gate(local_kgv: int, s_target: int) -> bool:
    """Schlanker nativer Modulo-Zweig — kein DTW, kein Speicher."""
    if s_target <= 1:
        return True
    if local_kgv <= 1:
        return False
    return local_kgv % s_target == 0
