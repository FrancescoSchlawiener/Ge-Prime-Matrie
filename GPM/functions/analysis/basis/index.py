"""Invertierter Prim-Index — profilweise partitioniert (Basis-Invariante A)."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field

from alphabets import AlphabetProfile
from analysis.algebra.gates import profile_symmetry_guard
from analysis.algebra.minhash import minhash_band_distance
from analysis.basis.compare_tiered import compare_basis_signatures_only
from analysis.basis.signature import BasisSignature, get_basis_signature
from analysis.document.model import GpmDocument


@dataclass(frozen=True)
class CandidateQueryResult:
    candidates: list[tuple[str, float]]
    zero_reason: str | None = None


@dataclass
class BasisIndex:
    profile: AlphabetProfile
    by_prime: dict[int, set[str]] = field(default_factory=dict)
    by_substance_bucket: dict[int, set[str]] = field(default_factory=dict)
    by_twin_bucket: dict[tuple, set[str]] = field(default_factory=dict)
    signatures: dict[str, BasisSignature] = field(default_factory=dict)

    def add(self, doc_id: str, signature: BasisSignature) -> None:
        if signature.profile != self.profile:
            raise ValueError(
                f"BasisIndex profile {self.profile.value} != signature {signature.profile.value}"
            )
        self.signatures[doc_id] = signature
        for prime in signature.prime_set:
            self.by_prime.setdefault(prime, set()).add(doc_id)
        for substance in signature.header_substance_set:
            bucket = substance % (1 << 20)
            self.by_substance_bucket.setdefault(bucket, set()).add(doc_id)
        if signature.twin_keys:
            for twin_key in signature.twin_keys:
                self.by_twin_bucket.setdefault(twin_key, set()).add(doc_id)


def build_basis_index(
    documents: Iterable[tuple[str, GpmDocument]],
    *,
    include_relation_sketch: bool = False,
    use_minhash: bool = False,
    include_typed_sketch: bool = False,
    include_twin_keys: bool = False,
) -> dict[AlphabetProfile, BasisIndex]:
    partitions: dict[AlphabetProfile, BasisIndex] = {}
    for doc_id, document in documents:
        profile = document.profile
        if profile not in partitions:
            partitions[profile] = BasisIndex(profile=profile)
        sig = get_basis_signature(
            document,
            doc_id=doc_id,
            include_relation_sketch=include_relation_sketch,
            use_minhash=use_minhash,
            include_typed_sketch=include_typed_sketch,
            include_twin_keys=include_twin_keys,
        )
        partitions[profile].add(doc_id, sig)
    return partitions


def extend_basis_index(
    partitions: dict[AlphabetProfile, BasisIndex],
    documents: Iterable[tuple[str, GpmDocument]],
    *,
    include_relation_sketch: bool = False,
    use_minhash: bool = False,
    include_typed_sketch: bool = False,
    include_twin_keys: bool = False,
) -> None:
    for doc_id, document in documents:
        profile = document.profile
        if profile not in partitions:
            partitions[profile] = BasisIndex(profile=profile)
        sig = get_basis_signature(
            document,
            doc_id=doc_id,
            include_relation_sketch=include_relation_sketch,
            use_minhash=use_minhash,
            include_typed_sketch=include_typed_sketch,
            include_twin_keys=include_twin_keys,
        )
        partitions[profile].add(doc_id, sig)


def _candidate_ids(
    index: BasisIndex,
    query_sig: BasisSignature,
    min_shared_primes: int,
    *,
    substance_hint: int | None = None,
    twin_hint: tuple | None = None,
) -> dict[str, int]:
    counts: dict[str, int] = {}
    for prime in query_sig.prime_set:
        for doc_id in index.by_prime.get(prime, ()):
            counts[doc_id] = counts.get(doc_id, 0) + 1
    filtered = {doc_id: c for doc_id, c in counts.items() if c >= min_shared_primes}
    if substance_hint is not None:
        bucket = substance_hint % (1 << 20)
        allowed = index.by_substance_bucket.get(bucket, set())
        filtered = {doc_id: c for doc_id, c in filtered.items() if doc_id in allowed}
    if twin_hint is not None:
        allowed = index.by_twin_bucket.get(twin_hint, set())
        filtered = {doc_id: c for doc_id, c in filtered.items() if doc_id in allowed}
    return filtered


def query_candidates(
    index: BasisIndex,
    query_sig: BasisSignature,
    *,
    min_shared_primes: int = 1,
    top_k: int = 50,
    substance_hint: int | None = None,
    minhash_min_band: float = 0.0,
    twin_hint: tuple | None = None,
) -> CandidateQueryResult:
    ok, reason = profile_symmetry_guard(query_sig.profile, index.profile)
    if not ok:
        return CandidateQueryResult([], zero_reason=reason)

    raw = _candidate_ids(
        index,
        query_sig,
        min_shared_primes,
        substance_hint=substance_hint,
        twin_hint=twin_hint,
    )
    if not raw:
        return CandidateQueryResult([], zero_reason="no_candidates")

    use_minhash = query_sig.minhash is not None and minhash_min_band > 0.0
    scored: list[tuple[str, float, int]] = []
    for doc_id, shared_count in raw.items():
        if doc_id == query_sig.doc_id:
            continue
        sig = index.signatures[doc_id]
        if use_minhash and sig.minhash is not None:
            band_sim = minhash_band_distance(query_sig.minhash, sig.minhash)
            if band_sim < minhash_min_band:
                continue
        tiered = compare_basis_signatures_only(query_sig, sig)
        if tiered.zero_reason:
            continue
        scored.append((doc_id, tiered.basis_score, shared_count))

    scored.sort(key=lambda row: (row[2], row[1]), reverse=True)
    return CandidateQueryResult([(doc_id, score) for doc_id, score, _ in scored[:top_k]])
