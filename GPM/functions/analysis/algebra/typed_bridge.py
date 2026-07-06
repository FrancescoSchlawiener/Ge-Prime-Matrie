"""gpm_types-Brücke — NI/DI-Sketches auf Dokument-Ebene."""

from __future__ import annotations

import hashlib

from gpm_types.classify import PayloadKind
from gpm_types.di.relation import parse_decimal

from analysis.document.model import GpmDocument, GpmToken


def _hash_chain(values: list[str]) -> tuple[int, ...]:
    if not values:
        return tuple()
    out: list[int] = []
    for value in values:
        digest = hashlib.sha256(value.encode()).hexdigest()
        out.append(int(digest[:8], 16))
    return tuple(out)


def document_ni_sketch(tokens: list[GpmToken]) -> tuple[int, ...]:
    """Hash-Kette aus NI-Token (PayloadKind N) — Pointer-IDs als Platzhalter."""
    chain: list[str] = []
    for token in tokens:
        if token.payload_kind == PayloadKind.N:
            chain.append(f"N:{token.word_id}:{token.perm_index}")
    return _hash_chain(chain)


def document_di_sketch(document: GpmDocument) -> tuple[int, ...]:
    """Sketch aus expliziten Dezimal-Payloads."""
    chain: list[str] = []
    for _pos, raw in document.explicit:
        try:
            rel = parse_decimal(raw)
            chain.append(f"D:{rel.whole}:{rel.den_reduced}:{rel.ggt}")
        except ValueError:
            continue
    for token in document.tokens:
        if token.payload_kind == PayloadKind.D:
            chain.append(f"D:tok:{token.word_id}")
    return _hash_chain(chain)


def document_typed_sketch(document: GpmDocument) -> tuple[int, ...] | None:
    ni = document_ni_sketch(document.tokens)
    di = document_di_sketch(document)
    combined = ni + di
    return combined if combined else None


def typed_sketch_jaccard(
    a: tuple[int, ...] | None,
    b: tuple[int, ...] | None,
) -> float:
    """Jaccard auf NI/DI-Hash-Tuples — nur wenn beide gesetzt."""
    if not a or not b:
        return 0.0
    set_a = set(a)
    set_b = set(b)
    union = set_a | set_b
    if not union:
        return 0.0
    return len(set_a & set_b) / len(union)
