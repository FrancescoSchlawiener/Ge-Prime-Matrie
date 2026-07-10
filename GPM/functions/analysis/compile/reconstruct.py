"""Verlustfreie Text-Rekonstruktion aus GpmDocument."""

from __future__ import annotations

from analysis.case.apply import apply_case
from analysis.case.codes import CASE_EXPLICIT, CASE_LOWER
from analysis.document.invariants import assert_gap_symmetry
from analysis.document.model import GpmDocument
from gpm_types.si.codec import decode_si


def _token_base_text(token_index: int, token, document: GpmDocument) -> str:
    entry = document.header[token.word_id]
    if entry.word_normalized:
        return entry.word_normalized
    return decode_si(entry.substance, token.perm_index, document.profile)


def render_token(
    token_index: int,
    token,
    document: GpmDocument,
    explicit_map: dict[int, str],
) -> str:
    if not document.case_policy.store_case:
        entry = document.header[token.word_id]
        if entry.word_canonical:
            return apply_case(entry.word_canonical, CASE_LOWER)
        return apply_case(_token_base_text(token_index, token, document), CASE_LOWER)
    if token_index in explicit_map:
        return explicit_map[token_index]
    entry = document.header[token.word_id]
    if entry.word_canonical:
        return apply_case(entry.word_canonical, token.case_code)
    return apply_case(_token_base_text(token_index, token, document), token.case_code)


def reconstruct_text(document: GpmDocument) -> str:
    assert_gap_symmetry(document)
    explicit_map = dict(document.explicit)
    parts: list[str] = [document.gaps[0]]
    for i, token in enumerate(document.tokens):
        parts.append(render_token(i, token, document, explicit_map))
        parts.append(document.gaps[i + 1])
    return "".join(parts)
