"""Verlustfreie Text-Rekonstruktion aus GpmDocument."""

from __future__ import annotations

from analysis.case.apply import apply_case
from analysis.case.codes import CASE_EXPLICIT, CASE_LOWER
from analysis.document.invariants import assert_gap_symmetry
from analysis.document.model import GpmDocument


def render_token(
    token_index: int,
    token,
    document: GpmDocument,
    explicit_map: dict[int, str],
) -> str:
    if not document.case_policy.store_case:
        entry = document.header[token.word_id]
        return apply_case(entry.word_canonical, CASE_LOWER)
    if token_index in explicit_map:
        return explicit_map[token_index]
    entry = document.header[token.word_id]
    return apply_case(entry.word_canonical, token.case_code)


def reconstruct_text(document: GpmDocument) -> str:
    assert_gap_symmetry(document)
    explicit_map = dict(document.explicit)
    parts: list[str] = [document.gaps[0]]
    for i, token in enumerate(document.tokens):
        parts.append(render_token(i, token, document, explicit_map))
        parts.append(document.gaps[i + 1])
    return "".join(parts)
