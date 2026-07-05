"""Hierarchie-Kurven aus DocumentHierarchy."""

from __future__ import annotations

from analysis.document.model import GpmDocument
from analysis.hierarchy.geom import build_document_hierarchy


def extract_phrase_curve(document: GpmDocument) -> list[dict]:
    hier = document.hierarchy or build_document_hierarchy(document)
    return [
        {
            "token_start": p.token_start,
            "token_count": p.token_count,
            "perm_index": p.perm_index,
            "perm_space": p.perm_space,
        }
        for p in hier.semantic.phrases
    ]


def extract_sentence_curve(document: GpmDocument) -> list[dict]:
    hier = document.hierarchy or build_document_hierarchy(document)
    return [
        {
            "token_start": s.token_start,
            "token_count": s.token_count,
            "perm_index": s.perm_index,
            "perm_space": s.perm_space,
            "boundary_suffix": s.boundary_suffix,
        }
        for s in hier.semantic.sentences
    ]
