"""Hierarchie-Kurven aus DocumentHierarchy — vollständige OG-Punkte."""

from __future__ import annotations

from analysis.compile.reconstruct import reconstruct_text
from analysis.document.model import GpmDocument
from analysis.hierarchy.access import get_hierarchy
from analysis.hierarchy.geom import HierarchyNode, build_document_hierarchy
from analysis.hierarchy.span_utils import char_range_for_tokens
from analysis.algebra.substance_kernel import (
    empty_transition_fields,
    substance_ggt_kgv_similarity,
    substance_transition_fields,
)


def _curve_from_nodes(
    document: GpmDocument,
    nodes: list[HierarchyNode],
    *,
    ratio_key: str,
    index_key: str,
) -> list[dict]:
    points: list[dict] = []
    prev_s: int | None = None
    text = reconstruct_text(document)
    for node in nodes:
        ratio = node.perm_index / node.perm_space if node.perm_space > 1 else 1.0
        trans = (
            substance_transition_fields(prev_s, node.s_level)
            if prev_s is not None
            else empty_transition_fields()
        )
        cs, ce = char_range_for_tokens(document, node.token_start, node.token_count)
        snippet = text[cs:ce] if text else ""
        points.append(
            {
                index_key: len(points),
                "text": snippet.strip(),
                "token_start": node.token_start,
                "token_count": node.token_count,
                "s_level": node.s_level,
                ratio_key: round(ratio, 6),
                "perm_index": node.perm_index,
                "perm_space": node.perm_space,
                "skeleton": list(node.skeleton or node.frequencies),
                **trans,
            }
        )
        prev_s = node.s_level
    return points


def extract_phrase_curve(document: GpmDocument) -> list[dict]:
    h = document.hierarchy or build_document_hierarchy(document)
    return _curve_from_nodes(document, h.semantic.phrases, ratio_key="i_phrase_ratio", index_key="phrase_index")


def extract_sentence_curve(document: GpmDocument) -> list[dict]:
    h = document.hierarchy or build_document_hierarchy(document)
    return _curve_from_nodes(document, h.semantic.sentences, ratio_key="i_satz_ratio", index_key="sentence_index")


def extract_paragraph_curve(document: GpmDocument) -> list[dict]:
    h = document.hierarchy or build_document_hierarchy(document)
    return _curve_from_nodes(document, h.semantic.paragraphs, ratio_key="i_absatz_ratio", index_key="paragraph_index")


def extract_line_curve(document: GpmDocument) -> list[dict]:
    h = document.hierarchy or build_document_hierarchy(document)
    return _curve_from_nodes(document, h.structural.lines, ratio_key="i_zeile_ratio", index_key="line_index")


def extract_page_curve(document: GpmDocument) -> list[dict]:
    h = get_hierarchy(document)
    return _curve_from_nodes(document, h.structural.pages, ratio_key="i_page_ratio", index_key="page_index")
