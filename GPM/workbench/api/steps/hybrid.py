"""Hybrid-Compile-Hilfen — Invariante A: keine Fence-Leaks in registry_entries."""

from __future__ import annotations

from typing import Any

from analysis.blocks.context import ParseDomain
from analysis.code.hybrid import HybridDocument, render_fence_boundary
from analysis.document.model import GpmDocument
from analysis.curves.i_curve import extract_cell_geometry
from analysis.document.preview import (
    assert_referential_integrity,
    build_genome_preview,
    build_geometry_preview,
)
from api.session import document_to_dict


def _fence_to_dict(boundary) -> dict[str, str]:
    if boundary is None:
        return {}
    return {
        "prefix_gap": boundary.prefix_gap,
        "fence_line": boundary.fence_line,
        "suffix_gap": boundary.suffix_gap,
    }


def build_hybrid_payload(hybrid: HybridDocument, *, document_ref: str, roundtrip_ok: bool) -> dict[str, Any]:
    nl_segments: list[dict] = []
    code_segments: list[dict] = []
    fence_boundaries: list[dict] = []
    gaps: list[str] = []

    for seg in hybrid.segments:
        if seg.domain is ParseDomain.NL and seg.nl_document is not None:
            nl_segments.append(
                {
                    "source_start": seg.source_start,
                    "source_end": seg.source_end,
                    "document": document_to_dict(seg.nl_document),
                }
            )
            gaps.extend(seg.nl_document.gaps)
        elif seg.domain is ParseDomain.CODE:
            code_segments.append(
                {
                    "source_start": seg.source_start,
                    "source_end": seg.source_end,
                    "language_id": seg.language_id,
                    "has_module": seg.code_module is not None,
                }
            )
            if seg.fence_open is not None:
                fence_boundaries.append({"kind": "open", **_fence_to_dict(seg.fence_open)})
            if seg.fence_close is not None:
                fence_boundaries.append({"kind": "close", **_fence_to_dict(seg.fence_close)})

    registry_entries: list[dict] = []
    if hybrid.registry is not None:
        for entry in hybrid.registry.s_entries:
            registry_entries.append(
                {
                    "word_id": entry.word_id,
                    "word_canonical": entry.word_canonical,
                    "word_normalized": entry.word_normalized,
                    "substance": entry.substance,
                    "perm_index": entry.perm_index,
                }
            )

    return {
        "document_ref": document_ref,
        "mode": "hybrid",
        "profile": hybrid.profile.value,
        "nl_segments": nl_segments,
        "code_segments": code_segments,
        "fence_boundaries": fence_boundaries,
        "gaps": gaps,
        "registry_entries": registry_entries,
        "roundtrip_ok": roundtrip_ok,
        "segment_count": len(hybrid.segments),
    }


def build_nl_payload(doc: GpmDocument, *, document_ref: str, roundtrip_ok: bool) -> dict[str, Any]:
    assert_referential_integrity(doc)
    payload = document_to_dict(doc)
    cells = extract_cell_geometry(doc) if doc.tokens else []
    payload.update(
        {
            "document_ref": document_ref,
            "mode": "nl",
            "roundtrip_ok": roundtrip_ok,
            "cells": cells[:512],
            "cell_count": len(cells),
            "genome_preview": build_genome_preview(doc),
            "geometry_preview": build_geometry_preview(doc),
            "registry_entries": [
                {
                    "word_id": e.word_id,
                    "word_canonical": e.word_canonical,
                    "word_normalized": e.word_normalized,
                    "substance": e.substance,
                    "perm_index": e.perm_index,
                }
                for e in doc.header
            ],
        }
    )
    return payload


def build_code_payload(
    *,
    document_ref: str,
    profile: str,
    language_id: str,
    registry_entries: list[dict],
    roundtrip_ok: bool,
) -> dict[str, Any]:
    return {
        "document_ref": document_ref,
        "mode": "code",
        "profile": profile,
        "language_id": language_id,
        "registry_entries": registry_entries,
        "roundtrip_ok": roundtrip_ok,
    }
