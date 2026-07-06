"""Log-Raum-Metriken — Basis-Invariante B: nur O(k) Log-Summen, kein profile_to_vector."""

from __future__ import annotations

import math
from collections import Counter

from analysis.meta.fingerprint import compare_profiles


def profile_log_norm(profile: Counter[int]) -> float:
    """Basis-Invariante B — schlanke Log-Summe über dünn besetztes Counter[int]."""
    return sum(exp * math.log(prime) for prime, exp in profile.items() if exp)


def log_gcd_similarity(a: Counter[int], b: Counter[int]) -> float:
    return compare_profiles(a, b)["similarity_ratio"]


def log_jaccard_primes(a: Counter[int], b: Counter[int]) -> float:
    keys = set(a) | set(b)
    if not keys:
        return 0.0
    inter = sum(min(a.get(k, 0), b.get(k, 0)) for k in keys)
    union = sum(max(a.get(k, 0), b.get(k, 0)) for k in keys)
    return inter / union if union else 0.0


def prime_entropy(profile: Counter[int]) -> float:
    total = sum(profile.values())
    if total <= 0:
        return 0.0
    entropy = 0.0
    for exp in profile.values():
        if exp <= 0:
            continue
        p = exp / total
        entropy -= p * math.log(p)
    return entropy


def compare_profiles_sparse(a: Counter[int], b: Counter[int]) -> dict:
    """O(k) Profil-Diagnostik ohne BigInt-V."""
    keys = set(a) | set(b)
    shared: Counter[int] = Counter()
    for k in keys:
        m = min(a.get(k, 0), b.get(k, 0))
        if m:
            shared[k] = m
    similarity = log_gcd_similarity(a, b)
    return {
        "shared_profile": shared,
        "similarity_ratio": similarity,
        "shared_prime_count": len(shared),
        "jaccard": log_jaccard_primes(a, b),
    }
