"""Hierarchie-Zugriff — lazy build + Interval-Index-Cache."""

from __future__ import annotations

from analysis.document.model import GpmDocument
from analysis.hierarchy.geom import DocumentHierarchy, build_document_hierarchy
from analysis.index.interval_index import IntervalIndex, build_interval_index


def get_hierarchy(document: GpmDocument) -> DocumentHierarchy:
    hierarchy = document.hierarchy
    if hierarchy is not None:
        return hierarchy
    hierarchy = build_document_hierarchy(document)
    document.hierarchy = hierarchy
    return hierarchy


def get_interval_index(document: GpmDocument) -> IntervalIndex:
    idx = getattr(document, "interval_index", None)
    if idx is not None:
        return idx
    h = get_hierarchy(document)
    idx = build_interval_index(h, len(document.tokens))
    document.interval_index = idx
    return idx
