"""Algebra-Gates und Zertifikate — Basis-Invariante A zuerst."""

from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass
from typing import TYPE_CHECKING

from alphabets import AlphabetProfile

from analysis.algebra.log_profile import log_gcd_similarity

if TYPE_CHECKING:
    from analysis.basis.signature import BasisSignature


@dataclass(frozen=True)
class BasisGateResult:
    passed: bool
    zero_reason: str | None
    shared_prime_count: int
    log_similarity: float


def profile_symmetry_guard(
    profile_a: AlphabetProfile | str,
    profile_b: AlphabetProfile | str,
) -> tuple[bool, str | None]:
    """Basis-Invariante A — disjunkte Prim-Räume bei Profil-Mismatch."""
    a = profile_a if isinstance(profile_a, AlphabetProfile) else AlphabetProfile(profile_a)
    b = profile_b if isinstance(profile_b, AlphabetProfile) else AlphabetProfile(profile_b)
    if a != b:
        return False, "profile_mismatch"
    return True, None


def prime_sets_disjoint(a: Counter[int], b: Counter[int]) -> bool:
    if not a or not b:
        return True
    return not (set(a.keys()) & set(b.keys()))


def substance_pair_gate(
    s1: int,
    s2: int,
    *,
    profile_a: AlphabetProfile | str,
    profile_b: AlphabetProfile | str,
) -> tuple[bool, str | None]:
    ok, reason = profile_symmetry_guard(profile_a, profile_b)
    if not ok:
        return False, reason
    if s1 <= 1 or s2 <= 1:
        return False, "invalid_substance"
    if math.gcd(s1, s2) <= 1:
        return False, "gcd_le_1"
    return True, None


def profile_pair_gate(
    profile_a: Counter[int],
    profile_b: Counter[int],
    *,
    doc_profile_a: AlphabetProfile | str,
    doc_profile_b: AlphabetProfile | str,
) -> tuple[bool, str | None]:
    ok, reason = profile_symmetry_guard(doc_profile_a, doc_profile_b)
    if not ok:
        return False, reason
    if not profile_a:
        return False, "empty_profile_a"
    if not profile_b:
        return False, "empty_profile_b"
    if prime_sets_disjoint(profile_a, profile_b):
        return False, "no_shared_primes"
    return True, None


def passes_document_relevance(
    sig_a: BasisSignature,
    sig_b: BasisSignature,
    *,
    min_shared_primes: int = 1,
) -> BasisGateResult:
    ok, reason = profile_symmetry_guard(sig_a.profile, sig_b.profile)
    if not ok:
        return BasisGateResult(False, reason, 0, 0.0)

    shared = len(sig_a.prime_set & sig_b.prime_set)
    if shared < min_shared_primes:
        zero = "no_shared_primes" if sig_a.prime_set and sig_b.prime_set else "empty_profile"
        return BasisGateResult(False, zero, shared, 0.0)

    log_sim = log_gcd_similarity(sig_a.prime_profile, sig_b.prime_profile)
    if log_sim <= 0.0:
        return BasisGateResult(False, "log_similarity_zero", shared, log_sim)
    return BasisGateResult(True, None, shared, log_sim)


def domain_scalar_gate(
    profile_overlap: float,
    relation_score: float,
    *,
    overlap_threshold: float = 0.35,
    relation_threshold: float = 0.35,
) -> tuple[bool, str | None]:
    """Domänen-ähnlicher Gate ohne DB — reine Skalar-Schwellwerte."""
    if profile_overlap < overlap_threshold:
        return False, "profile_overlap_low"
    if relation_score < relation_threshold:
        return False, "relation_score_low"
    return True, None
