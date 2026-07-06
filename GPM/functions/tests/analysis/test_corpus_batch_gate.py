"""batch_gate_candidates unit tests."""

from __future__ import annotations

from collections import Counter

from alphabets import AlphabetProfile
from analysis.basis.corpus_compare import batch_gate_candidates
from analysis.basis.index import BasisIndex
from analysis.basis.signature import BasisSignature


def _sig(doc_id: str, primes: set[int]) -> BasisSignature:
    profile = Counter({p: 1 for p in primes})
    return BasisSignature(
        doc_id=doc_id,
        profile=AlphabetProfile.OG,
        prime_profile=profile,
        prime_set=frozenset(primes),
        token_count=1,
        header_substance_set=frozenset(),
        relation_sketch=None,
        log_norm=1.0,
        has_relation_sketch=False,
    )


def test_batch_gate_filters_disjoint():
    index = BasisIndex(profile=AlphabetProfile.OG)
    index.add("a", _sig("a", {2, 3}))
    index.add("b", _sig("b", {5, 7}))
    query = _sig("__query__", {2, 11})
    survivors = batch_gate_candidates(query, index, min_shared_primes=1)
    assert survivors == ["a"]


def test_batch_gate_respects_allowed_ids():
    index = BasisIndex(profile=AlphabetProfile.OG)
    index.add("a", _sig("a", {2, 3}))
    index.add("b", _sig("b", {2, 5}))
    query = _sig("__query__", {2})
    survivors = batch_gate_candidates(query, index, allowed_ids={"b"})
    assert survivors == ["b"]
