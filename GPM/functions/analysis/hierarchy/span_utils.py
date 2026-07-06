"""Token-Span-Hilfen — Char-Map, Interval-Queries."""

from __future__ import annotations

from analysis.blocks.node import TokenSpan
from analysis.case.apply import apply_case
from analysis.compile.reconstruct import reconstruct_text
from analysis.document.model import GpmDocument
from analysis.hierarchy.access import get_hierarchy, get_interval_index
from analysis.hierarchy.geom import DocumentHierarchy
from analysis.index.interval_index import nodes_intersecting_indexed


def token_char_map(document: GpmDocument) -> list[tuple[int, int, int]]:
    """Pro Token: (token_index, char_start, char_end) im rekonstruierten Text."""
    text = reconstruct_text(document)
    mapping: list[tuple[int, int, int]] = []
    pos = 0
    explicit_map = dict(document.explicit)
    for i, token in enumerate(document.tokens):
        gap = document.gaps[i] if i < len(document.gaps) else ""
        pos += len(gap)
        start = pos
        if i in explicit_map:
            word = explicit_map[i]
        else:
            word = apply_case(document.header[token.word_id].word_canonical, token.case_code)
        pos += len(word)
        mapping.append((i, start, pos))
    if len(text) and pos > len(text):
        pass
    return mapping


def char_range_for_tokens(document: GpmDocument, token_start: int, token_count: int) -> tuple[int, int]:
    mapping = token_char_map(document)
    if token_count <= 0 or token_start >= len(mapping):
        return 0, 0
    end_idx = min(len(mapping), token_start + token_count) - 1
    return mapping[token_start][1], mapping[end_idx][2]


def nodes_for_token_span(
    hierarchy: DocumentHierarchy,
    token_start: int,
    token_count: int,
    *,
    interval_index=None,
) -> dict:
    span = TokenSpan(token_start, token_count)
    return {
        "sentences": nodes_intersecting_indexed(
            interval_index, "sentence", hierarchy.semantic.sentences, span
        ),
        "lines": nodes_intersecting_indexed(
            interval_index, "line", hierarchy.structural.lines, span
        ),
        "phrases": nodes_intersecting_indexed(
            interval_index, "phrase", hierarchy.semantic.phrases, span
        ),
    }


def nodes_for_document_span(document: GpmDocument, token_start: int, token_count: int) -> dict:
    hierarchy = get_hierarchy(document)
    idx = get_interval_index(document)
    return nodes_for_token_span(hierarchy, token_start, token_count, interval_index=idx)
