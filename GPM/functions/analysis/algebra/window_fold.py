"""Fenster-Exponent-Fold — partielle Ordnung ohne Integer-LCM."""

from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass

from alphabets import AlphabetProfile

from analysis.algebra.fusion import log_jaccard_basis_blend
from analysis.algebra.gates import BasisGateResult, profile_symmetry_guard
from analysis.algebra.log_profile import log_gcd_similarity, log_jaccard_primes


@dataclass(frozen=True)
class ExponentWindow:
    exponents: dict[int, int]

    def as_counter(self) -> Counter[int]:
        return Counter({k: v for k, v in self.exponents.items() if v})

    def covers(self, other: ExponentWindow) -> bool:
        for prime, exp in other.exponents.items():
            if self.exponents.get(prime, 0) < exp:
                return False
        return True

    def fold_max(self, other: ExponentWindow) -> ExponentWindow:
        keys = set(self.exponents) | set(other.exponents)
        merged = {k: max(self.exponents.get(k, 0), other.exponents.get(k, 0)) for k in keys}
        return ExponentWindow({k: v for k, v in merged.items() if v})


def exponent_window_to_substance(window: ExponentWindow) -> int:
    """Fenster-LCM — nur Legacy-/Divisor-Metadaten (F-A), nie Similarity-Hotpath mit profile."""
    result = 1
    for prime, exp in window.exponents.items():
        if exp:
            result = math.lcm(result, prime**exp)
    return result


def fold_window_from_token_exponents(
    per_token: list[dict[int, int]],
    start: int,
    end: int,
) -> ExponentWindow:
    if start < 0:
        start = 0
    if end > len(per_token):
        end = len(per_token)
    if start >= end:
        return ExponentWindow({})
    exponents: dict[int, int] = {}
    for exps in per_token[start:end]:
        for prime, exp in exps.items():
            if exp:
                exponents[prime] = max(exponents.get(prime, 0), exp)
    return ExponentWindow(exponents)


def fold_window_from_series(
    exp_by_prime: dict[int, list[int]],
    start: int,
    end: int,
) -> ExponentWindow:
    if start >= end:
        return ExponentWindow({})
    exponents: dict[int, int] = {}
    for prime, series in exp_by_prime.items():
        if start >= len(series):
            continue
        end_clamped = min(end, len(series))
        max_exp = max(series[start:end_clamped])
        if max_exp:
            exponents[prime] = max_exp
    return ExponentWindow(exponents)


def window_similarity(
    w_a: ExponentWindow,
    w_b: ExponentWindow,
    *,
    profile_a: AlphabetProfile,
    profile_b: AlphabetProfile,
) -> tuple[float, str | None]:
    """Härtungs-Invariante D-C: Guard first, dann log-GCD/Jaccard-Mix."""
    ok, reason = profile_symmetry_guard(profile_a, profile_b)
    if not ok:
        return 0.0, reason
    ca = w_a.as_counter()
    cb = w_b.as_counter()
    if not ca or not cb:
        return 0.0, None
    log_sim = log_gcd_similarity(ca, cb)
    jaccard = log_jaccard_primes(ca, cb)
    score = log_jaccard_basis_blend(log_sim, jaccard)
    return score, None


def compare_windows_pair(
    w_a: ExponentWindow,
    w_b: ExponentWindow,
    *,
    profile_a: AlphabetProfile,
    profile_b: AlphabetProfile,
) -> BasisGateResult:
    ok, reason = profile_symmetry_guard(profile_a, profile_b)
    if not ok:
        return BasisGateResult(
            passed=False,
            zero_reason=reason,
            shared_prime_count=0,
            log_similarity=0.0,
        )
    ca = w_a.as_counter()
    cb = w_b.as_counter()
    shared = len(set(ca) & set(cb))
    if shared == 0:
        return BasisGateResult(
            passed=False,
            zero_reason="no_shared_primes",
            shared_prime_count=0,
            log_similarity=0.0,
        )
    log_sim = log_gcd_similarity(ca, cb)
    return BasisGateResult(
        passed=log_sim > 0,
        zero_reason=None if log_sim > 0 else "log_similarity_zero",
        shared_prime_count=shared,
        log_similarity=log_sim,
    )
