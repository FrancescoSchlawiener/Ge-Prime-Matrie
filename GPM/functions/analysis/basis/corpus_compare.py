"""Korpus-API — find_similar_documents über BasisIndex."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass, field

from alphabets import AlphabetProfile
from analysis.algebra.gates import passes_document_relevance
from analysis.basis.compare_tiered import CompareTier, compare_documents_tiered
from analysis.basis.index import BasisIndex, build_basis_index, query_candidates
from analysis.basis.signature import BasisSignature, get_basis_signature
from analysis.document.model import GpmDocument

MINHASH_AUTO_THRESHOLD = 10_000
MINHASH_MIN_BAND = 0.05


@dataclass(frozen=True)
class SimilarityHit:
    doc_id: str
    score: float
    zero_reason: str | None
    tiers_run: tuple[str, ...]
    shared_prime_count: int


@dataclass
class CorpusSearchResult:
    hits: list[SimilarityHit] = field(default_factory=list)
    zero_reason: str | None = None


def batch_gate_candidates(
    query_sig: BasisSignature,
    index: BasisIndex,
    *,
    min_shared_primes: int = 1,
    allowed_ids: set[str] | None = None,
) -> list[str]:
    """Arithmetisches Pruning über gespeicherte BasisSignaturen — ohne GpmDocument."""
    survivors: list[str] = []
    for doc_id, sig in index.signatures.items():
        if doc_id == query_sig.doc_id:
            continue
        if allowed_ids is not None and doc_id not in allowed_ids:
            continue
        gate = passes_document_relevance(query_sig, sig, min_shared_primes=min_shared_primes)
        if gate.passed:
            survivors.append(doc_id)
    return survivors


def find_similar_documents(
    query: GpmDocument,
    corpus: Iterable[tuple[str, GpmDocument]] | None = None,
    *,
    max_tier: CompareTier = CompareTier.BASIS,
    top_k: int = 20,
    min_shared_primes: int = 1,
    min_basis_score: float = 0.05,
    index: dict[AlphabetProfile, BasisIndex] | None = None,
    substance_hint: int | None = None,
    fusion_mode: str = "default",
    typed_weight: float = 0.0,
    corpus_ids: list[str] | None = None,
    doc_loader: Callable[[str], GpmDocument | None] | None = None,
) -> CorpusSearchResult:
    if corpus is None and (corpus_ids is None or doc_loader is None):
        raise ValueError("corpus oder (corpus_ids + doc_loader) erforderlich.")

    corpus_list = list(corpus) if corpus is not None else []
    corpus_id_set = set(corpus_ids) if corpus_ids is not None else {doc_id for doc_id, _ in corpus_list}
    use_minhash = len(corpus_id_set) >= MINHASH_AUTO_THRESHOLD
    include_typed = max_tier > CompareTier.BASIS

    partitions = index if index is not None else build_basis_index(
        corpus_list,
        include_relation_sketch=False,
        use_minhash=use_minhash,
        include_typed_sketch=include_typed,
    )
    query_sig = get_basis_signature(
        query,
        doc_id="__query__",
        include_relation_sketch=max_tier > CompareTier.BASIS,
        use_minhash=use_minhash,
        include_typed_sketch=include_typed,
    )
    profile = query.profile

    if profile not in partitions:
        return CorpusSearchResult([], zero_reason="profile_partition_empty")

    index_obj = partitions[profile]
    gated_ids = set(
        batch_gate_candidates(
            query_sig,
            index_obj,
            min_shared_primes=min_shared_primes,
            allowed_ids=corpus_id_set,
        )
    )
    if not gated_ids:
        return CorpusSearchResult([], zero_reason="batch_gate_empty")

    candidate_result = query_candidates(
        index_obj,
        query_sig,
        min_shared_primes=min_shared_primes,
        top_k=top_k * 5,
        substance_hint=substance_hint,
        minhash_min_band=MINHASH_MIN_BAND if use_minhash else 0.0,
    )
    if candidate_result.zero_reason and not candidate_result.candidates:
        return CorpusSearchResult([], zero_reason=candidate_result.zero_reason)

    hits: list[SimilarityHit] = []
    doc_by_id: dict[str, GpmDocument] = {}
    if doc_loader is None:
        doc_by_id = {doc_id: doc for doc_id, doc in corpus_list if doc.profile == profile}

    for doc_id, _candidate_score in candidate_result.candidates:
        if doc_id not in gated_ids:
            continue
        if doc_loader is not None:
            doc = doc_loader(doc_id)
        else:
            doc = doc_by_id.get(doc_id)
        if doc is None:
            continue
        tiered = compare_documents_tiered(
            query,
            doc,
            max_tier=max_tier,
            min_basis_score=min_basis_score,
            sig_a=query_sig,
            fusion_mode=fusion_mode,
            typed_weight=typed_weight,
        )
        if tiered.zero_reason and tiered.zero_reason != "basis_score_below_threshold":
            continue
        score = tiered.final_score
        if score < min_basis_score and max_tier <= CompareTier.BASIS:
            continue
        hits.append(
            SimilarityHit(
                doc_id=doc_id,
                score=round(score, 6),
                zero_reason=tiered.zero_reason,
                tiers_run=tuple(tiered.tiers_run),
                shared_prime_count=tiered.shared_prime_count,
            )
        )
        if len(hits) >= top_k:
            break

    hits.sort(key=lambda h: h.score, reverse=True)
    return CorpusSearchResult(hits[:top_k])
