"""Basis-Signaturen — kompakte Dokument-Fingerprints."""

from __future__ import annotations

import hashlib
from collections import Counter
from dataclasses import dataclass

from alphabets import AlphabetProfile
from analysis.algebra.log_profile import profile_log_norm
from analysis.algebra.minhash import prime_minhash
from analysis.algebra.typed_bridge import document_typed_sketch
from analysis.document.model import GpmDocument
from analysis.profile.prime_profile import build_prime_profile
from analysis.profile.relation import build_relation_profile


def _relation_sketch(document: GpmDocument) -> tuple[int, ...] | None:
    if len(document.tokens) < 2:
        return None
    rel = build_relation_profile(document)
    bigrams = rel["substance_bigrams"]
    if not bigrams:
        return None
    top_keys = [k for k, _ in bigrams.most_common(32)]
    hashes: list[int] = []
    for key in top_keys:
        digest = hashlib.sha256(key.encode()).hexdigest()
        hashes.append(int(digest[:8], 16))
    return tuple(sorted(hashes))


def _document_twin_keys(document: GpmDocument) -> frozenset[tuple]:
    from analysis.curves.i_curve import extract_cell_geometry, skeleton_signature

    cells = extract_cell_geometry(document)
    keys = {skeleton_signature(cell) for cell in cells if cell.get("perm_space", 0) > 0}
    return frozenset(keys)


@dataclass(frozen=True)
class BasisSignature:
    doc_id: str
    profile: AlphabetProfile
    prime_profile: Counter[int]
    prime_set: frozenset[int]
    token_count: int
    header_substance_set: frozenset[int]
    relation_sketch: tuple[int, ...] | None
    log_norm: float
    has_relation_sketch: bool = True
    minhash: tuple[int, ...] | None = None
    typed_sketch: tuple[int, ...] | None = None
    twin_keys: frozenset[tuple] | None = None


def build_basis_signature(
    document: GpmDocument,
    *,
    doc_id: str = "",
    include_relation_sketch: bool = True,
    use_minhash: bool = False,
    include_typed_sketch: bool = False,
    include_twin_keys: bool = False,
) -> BasisSignature:
    prime_profile = build_prime_profile(document)
    substances = frozenset(entry.substance for entry in document.header if entry.substance > 1)
    rel_sketch = _relation_sketch(document) if include_relation_sketch else None
    minhash = (
        prime_minhash(prime_profile, alphabet_profile=document.profile)
        if use_minhash
        else None
    )
    typed = document_typed_sketch(document) if include_typed_sketch else None
    twin_keys = _document_twin_keys(document) if include_twin_keys else None
    return BasisSignature(
        doc_id=doc_id,
        profile=document.profile,
        prime_profile=prime_profile,
        prime_set=frozenset(prime_profile.keys()),
        token_count=len(document.tokens),
        header_substance_set=substances,
        relation_sketch=rel_sketch,
        log_norm=profile_log_norm(prime_profile),
        has_relation_sketch=include_relation_sketch and rel_sketch is not None,
        minhash=minhash,
        typed_sketch=typed,
        twin_keys=twin_keys,
    )


def get_basis_signature(
    document: GpmDocument,
    *,
    doc_id: str = "",
    include_relation_sketch: bool = True,
    use_minhash: bool = False,
    include_typed_sketch: bool = False,
    include_twin_keys: bool = False,
) -> BasisSignature:
    cached = getattr(document, "basis_signature", None)
    if (
        cached is not None
        and cached.doc_id == doc_id
        and cached.has_relation_sketch == (include_relation_sketch and cached.relation_sketch is not None)
        and (cached.typed_sketch is not None) == include_typed_sketch
        and (cached.minhash is not None) == use_minhash
        and (cached.twin_keys is not None) == include_twin_keys
    ):
        return cached
    sig = build_basis_signature(
        document,
        doc_id=doc_id,
        include_relation_sketch=include_relation_sketch,
        use_minhash=use_minhash,
        include_typed_sketch=include_typed_sketch,
        include_twin_keys=include_twin_keys,
    )
    document.basis_signature = sig
    return sig
