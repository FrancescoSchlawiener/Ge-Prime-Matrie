"""Eager Warm-up für gecachte GpmDocument-Instanzen."""

from __future__ import annotations

from analysis.basis.signature import get_basis_signature
from analysis.blocks.build import materialize_geometry
from analysis.document.model import GpmDocument
from analysis.index.substance_index import get_substance_index


def warmup_document(document: GpmDocument) -> None:
    """Materialisiert Lazy-Caches einmalig nach Compile."""
    if document.tokens:
        materialize_geometry(document)
    get_basis_signature(document)
    if document.tokens:
        get_substance_index(document)
