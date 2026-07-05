"""Orthogonales Hierarchie-Gitter — semantischer und struktureller Layer."""

from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass, field

from analysis.cell.geom import (
    MAX_CELL_TOKENS,
    CellGeometry,
    _category_key,
    build_cell_geometry,
    split_for_perm_overflow,
)
from analysis.document.model import GpmDocument
from analysis.hierarchy.boundary import boundary_suffix_for_token
from analysis.blocks.node import TokenSpan
from perm.multiset import perm_index, perm_space

_PHRASE_END = frozenset(",;-")
_SENTENCE_END = frozenset(".!?")


@dataclass(frozen=True)
class PhraseCategoryKey:
    s_phrase: int
    token_count: int


@dataclass(frozen=True)
class SentenceCategoryKey:
    s_sentence: int
    phrase_count: int


@dataclass(frozen=True)
class LineCategoryKey:
    s_line: int
    token_count: int


@dataclass
class HierarchyNode:
    layer: str
    level: str
    token_start: int
    token_count: int
    perm_index: int = 0
    perm_space: int = 1
    frequencies: list[int] = field(default_factory=list)
    category_sequence: list[int] = field(default_factory=list)
    s_level: int = 1
    parent_index: int | None = None
    overflow_index: int | None = None
    skeleton: list[int] = field(default_factory=list)
    boundary_suffix: int = 0


@dataclass
class SemanticTree:
    phrases: list[HierarchyNode] = field(default_factory=list)
    sentences: list[HierarchyNode] = field(default_factory=list)
    paragraphs: list[HierarchyNode] = field(default_factory=list)
    encodable_segments: list[CellGeometry] = field(default_factory=list)


@dataclass
class StructuralTree:
    lines: list[HierarchyNode] = field(default_factory=list)
    pages: list[HierarchyNode] = field(default_factory=list)


@dataclass
class DocumentHierarchy:
    semantic: SemanticTree = field(default_factory=SemanticTree)
    structural: StructuralTree = field(default_factory=StructuralTree)


def intervals_overlap(a_start: int, a_count: int, b_start: int, b_count: int) -> bool:
    a_end = a_start + a_count
    b_end = b_start + b_count
    return not (a_end <= b_start or b_end <= a_start)


def gap_ends_phrase(gap: str) -> bool:
    stripped = gap.rstrip()
    return bool(stripped) and stripped[-1] in _PHRASE_END


def gap_ends_sentence(gap: str) -> bool:
    stripped = gap.rstrip()
    return bool(stripped) and stripped[-1] in _SENTENCE_END


def gap_starts_paragraph(gap: str) -> bool:
    gap = gap.replace("\r\n", "\n").replace("\r", "\n")
    return "\n\n" in gap or gap.startswith("\n\n")


def gap_has_line_break(gap: str) -> bool:
    if "\n\n" in gap:
        return False
    return "\n" in gap


def _split_spans(
    token_count: int,
    gaps: list[str],
    *,
    gap_predicate,
    include_tail: bool = True,
) -> list[TokenSpan]:
    if token_count == 0:
        return []
    spans: list[TokenSpan] = []
    start = 0
    for i in range(token_count):
        gap_after = gaps[i + 1] if i + 1 < len(gaps) else ""
        if gap_predicate(gap_after):
            spans.append(TokenSpan(start, i - start + 1))
            start = i + 1
    if include_tail and start < token_count:
        spans.append(TokenSpan(start, token_count - start))
    return spans


def split_phrase_spans(token_count: int, gaps: list[str]) -> list[TokenSpan]:
    return _split_spans(token_count, gaps, gap_predicate=gap_ends_phrase)


def split_sentence_spans(token_count: int, gaps: list[str]) -> list[TokenSpan]:
    return _split_spans(token_count, gaps, gap_predicate=gap_ends_sentence)


def split_paragraph_spans(token_count: int, gaps: list[str]) -> list[TokenSpan]:
    if token_count == 0:
        return []
    spans: list[TokenSpan] = []
    start = 0
    for i in range(token_count):
        gap_before = gaps[i] if i < len(gaps) else ""
        if i > start and gap_starts_paragraph(gap_before):
            spans.append(TokenSpan(start, i - start))
            start = i
    if start < token_count:
        spans.append(TokenSpan(start, token_count - start))
    if not spans:
        spans.append(TokenSpan(0, token_count))
    return spans


def split_line_spans(token_count: int, gaps: list[str]) -> list[TokenSpan]:
    if token_count == 0:
        return []
    spans: list[TokenSpan] = []
    start = 0
    for i in range(token_count):
        gap_after = gaps[i + 1] if i + 1 < len(gaps) else ""
        if gap_has_line_break(gap_after):
            spans.append(TokenSpan(start, i - start + 1))
            start = i + 1
    if start < token_count:
        spans.append(TokenSpan(start, token_count - start))
    if not spans:
        spans.append(TokenSpan(0, token_count))
    return spans


def _phrase_substance(document: GpmDocument, span: TokenSpan) -> int:
    substances = [
        document.header[document.tokens[span.token_start + i].word_id].substance
        for i in range(span.token_count)
    ]
    result = substances[0] if substances else 1
    for s in substances[1:]:
        result = math.lcm(result, s)
    return result


def _category_keys_for_span(
    document: GpmDocument,
    span: TokenSpan,
    explicit_map: dict[int, str],
) -> list:
    return [
        _category_key(document.tokens[span.token_start + i], span.token_start + i, explicit_map)
        for i in range(span.token_count)
    ]


def _build_word_geometry(
    document: GpmDocument,
    span: TokenSpan,
    explicit_map: dict[int, str],
) -> CellGeometry:
    if span.token_count <= MAX_CELL_TOKENS:
        tokens = document.tokens[span.token_start : span.token_end]
        return build_cell_geometry(tokens, token_start=span.token_start, explicit_map=explicit_map)
    mid = span.token_count // 2
    keys = _category_keys_for_span(document, TokenSpan(span.token_start, mid), explicit_map) + (
        _category_keys_for_span(
            document, TokenSpan(span.token_start + mid, span.token_count - mid), explicit_map
        )
    )
    freqs, cat_seq, n, i_val = _geometry_from_keys(keys, lambda k: k)
    return CellGeometry(
        token_start=span.token_start,
        token_count=span.token_count,
        categories=[],
        category_sequence=cat_seq,
        frequencies=freqs,
        perm_space=n,
        perm_index=i_val,
    )


def _geometry_from_keys(keys: list, key_fn) -> tuple[list[int], list[int], int, int]:
    key_to_id: dict = {}
    cat_ids: list[int] = []
    for key in keys:
        if key not in key_to_id:
            key_to_id[key] = len(key_to_id)
        cat_ids.append(key_to_id[key])
    counts = Counter(cat_ids)
    freqs = [counts[i] for i in range(len(key_to_id))]
    n = perm_space(counts) if freqs else 1
    i_val = perm_index(cat_ids, counts) if freqs else 1
    return freqs, cat_ids, n, i_val


def _phrase_nodes(document: GpmDocument, explicit_map: dict[int, str]) -> list[HierarchyNode]:
    nodes: list[HierarchyNode] = []
    for span in split_phrase_spans(len(document.tokens), document.gaps):
        geom = _build_word_geometry(document, span, explicit_map)
        nodes.append(
            HierarchyNode(
                layer="semantic",
                level="phrase",
                token_start=span.token_start,
                token_count=span.token_count,
                perm_index=geom.perm_index,
                perm_space=geom.perm_space,
                frequencies=list(geom.frequencies),
                category_sequence=list(geom.category_sequence),
                skeleton=list(geom.frequencies),
                s_level=_phrase_substance(document, span),
            )
        )
    return nodes


def _sentence_nodes(document: GpmDocument, phrases: list[HierarchyNode]) -> list[HierarchyNode]:
    nodes: list[HierarchyNode] = []
    for span in split_sentence_spans(len(document.tokens), document.gaps):
        phrase_keys = [
            PhraseCategoryKey(
                s_phrase=_phrase_substance(document, TokenSpan(p.token_start, p.token_count)),
                token_count=p.token_count,
            )
            for p in phrases
            if intervals_overlap(p.token_start, p.token_count, span.token_start, span.token_count)
        ]
        if not phrase_keys:
            phrase_keys = [
                PhraseCategoryKey(
                    s_phrase=_phrase_substance(document, span),
                    token_count=span.token_count,
                )
            ]
        freqs, _seq, n, i_val = _geometry_from_keys(phrase_keys, lambda k: k)
        s_sentence = _phrase_substance(document, span)
        last_tok = span.token_start + span.token_count - 1
        gap_after = document.gaps[last_tok + 1] if last_tok + 1 < len(document.gaps) else ""
        nodes.append(
            HierarchyNode(
                layer="semantic",
                level="sentence",
                token_start=span.token_start,
                token_count=span.token_count,
                perm_index=i_val,
                perm_space=n,
                frequencies=freqs,
                s_level=s_sentence,
                boundary_suffix=boundary_suffix_for_token(document, last_tok, gap_after),
            )
        )
    return nodes


def _paragraph_nodes(document: GpmDocument, sentences: list[HierarchyNode]) -> list[HierarchyNode]:
    nodes: list[HierarchyNode] = []
    for span in split_paragraph_spans(len(document.tokens), document.gaps):
        sent_keys = [
            SentenceCategoryKey(
                s_sentence=s.s_level,
                phrase_count=max(1, len(s.frequencies)),
            )
            for s in sentences
            if intervals_overlap(s.token_start, s.token_count, span.token_start, span.token_count)
        ]
        if not sent_keys:
            sent_keys = [
                SentenceCategoryKey(
                    s_sentence=_phrase_substance(document, span),
                    phrase_count=1,
                )
            ]
        freqs, _seq, n, i_val = _geometry_from_keys(sent_keys, lambda k: k)
        nodes.append(
            HierarchyNode(
                layer="semantic",
                level="paragraph",
                token_start=span.token_start,
                token_count=span.token_count,
                perm_index=i_val,
                perm_space=n,
                frequencies=freqs,
                s_level=_phrase_substance(document, span),
            )
        )
    return nodes


def _line_nodes(document: GpmDocument, explicit_map: dict[int, str]) -> list[HierarchyNode]:
    nodes: list[HierarchyNode] = []
    for span in split_line_spans(len(document.tokens), document.gaps):
        keys = _category_keys_for_span(document, span, explicit_map)
        key_to_id: dict = {}
        cat_ids: list[int] = []
        for key in keys:
            if key not in key_to_id:
                key_to_id[key] = len(key_to_id)
            cat_ids.append(key_to_id[key])
        counts = Counter(cat_ids)
        freqs = [counts[i] for i in range(len(key_to_id))]
        if span.token_count <= MAX_CELL_TOKENS and len(key_to_id) <= 12:
            geom = _build_word_geometry(document, span, explicit_map)
            perm_index_val = geom.perm_index
            perm_space_val = geom.perm_space
            freqs = list(geom.frequencies)
        else:
            perm_index_val = 1
            perm_space_val = 1
        nodes.append(
            HierarchyNode(
                layer="structural",
                level="line",
                token_start=span.token_start,
                token_count=span.token_count,
                perm_index=perm_index_val,
                perm_space=perm_space_val,
                frequencies=freqs,
                skeleton=list(freqs),
                s_level=_phrase_substance(document, span),
            )
        )
    return nodes


def build_semantic_encodable_segments(document: GpmDocument) -> list[CellGeometry]:
    explicit_map = dict(document.explicit)
    segments: list[CellGeometry] = []
    for span in split_sentence_spans(len(document.tokens), document.gaps):
        tokens = document.tokens[span.token_start : span.token_end]
        segments.extend(
            split_for_perm_overflow(
                tokens,
                token_start=span.token_start,
                explicit_map=explicit_map,
            )
        )
    return segments


def build_document_hierarchy(document: GpmDocument) -> DocumentHierarchy:
    explicit_map = dict(document.explicit)
    phrases = _phrase_nodes(document, explicit_map)
    sentences = _sentence_nodes(document, phrases)
    paragraphs = _paragraph_nodes(document, sentences)
    lines = _line_nodes(document, explicit_map)
    encodable = build_semantic_encodable_segments(document)
    return DocumentHierarchy(
        semantic=SemanticTree(
            phrases=phrases,
            sentences=sentences,
            paragraphs=paragraphs,
            encodable_segments=encodable,
        ),
        structural=StructuralTree(lines=lines, pages=[]),
    )


def validate_structural_partition(token_count: int, lines: list[HierarchyNode]) -> None:
    cursor = 0
    for line in lines:
        if line.token_start != cursor:
            raise ValueError(
                f"Structural line start mismatch: expected {cursor}, got {line.token_start}"
            )
        cursor += line.token_count
    if cursor != token_count:
        raise ValueError(f"Structural partition mismatch: {cursor} != {token_count}")
