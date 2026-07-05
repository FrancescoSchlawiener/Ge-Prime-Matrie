"""Sparse Prime-Exponent-Gitter — Fenster-LCM in O(n · #primes_doc)."""

from __future__ import annotations

import math
from collections import Counter, deque
from dataclasses import dataclass, field

from alphabets.registry import char_map_for_profile
from analysis.document.model import GpmDocument
from analysis.substance.compare import substance_ggt_kgv_similarity
from gpm_types.si.substance import ingredients_for_profile


@dataclass(frozen=True)
class WindowFingerprint:
    exponents: dict[int, int]

    def as_substance_cover(self) -> Counter:
        return Counter(self.exponents)

    def covers(self, other: WindowFingerprint) -> bool:
        for prime, exp in other.exponents.items():
            if self.exponents.get(prime, 0) < exp:
                return False
        return True


@dataclass
class SubstanceIndex:
    token_count: int
    exp_by_prime: dict[int, list[int]] = field(default_factory=dict)

    def primes(self) -> list[int]:
        return sorted(self.exp_by_prime.keys())


def _prime_exponents(substance: int, profile) -> dict[int, int]:
    counts = ingredients_for_profile(substance, profile)
    char_to_prime = {v: k for k, v in char_map_for_profile(profile).items()}
    result: dict[int, int] = {}
    for char, count in counts.items():
        prime = char_to_prime.get(char)
        if prime and count:
            result[prime] = count
    return result


def _sliding_max_windows(series: list[int], width: int) -> list[int]:
    if width <= 0 or len(series) < width:
        return []
    dq: deque[int] = deque()
    maxes: list[int] = []
    for i, value in enumerate(series):
        while dq and dq[0] <= i - width:
            dq.popleft()
        while dq and series[dq[-1]] <= value:
            dq.pop()
        dq.append(i)
        if i >= width - 1:
            maxes.append(series[dq[0]])
    return maxes


def build_substance_index(document: GpmDocument) -> SubstanceIndex:
    n = len(document.tokens)
    exp_by_prime: dict[int, list[int]] = {}
    prime_set: set[int] = set()
    profile = document.profile

    per_token: list[dict[int, int]] = []
    for token in document.tokens:
        entry = document.header[token.word_id]
        exps = _prime_exponents(entry.substance, profile)
        per_token.append(exps)
        prime_set.update(exps.keys())

    for prime in sorted(prime_set):
        exp_by_prime[prime] = [exps.get(prime, 0) for exps in per_token]

    return SubstanceIndex(token_count=n, exp_by_prime=exp_by_prime)


def window_fingerprint(index: SubstanceIndex, start: int, end: int) -> WindowFingerprint:
    if start < 0:
        start = 0
    if end > index.token_count:
        end = index.token_count
    if start >= end:
        return WindowFingerprint({})

    exponents: dict[int, int] = {}
    for prime, series in index.exp_by_prime.items():
        max_exp = max(series[start:end])
        if max_exp:
            exponents[prime] = max_exp
    return WindowFingerprint(exponents)


def _fingerprint_lcm_value(fp: WindowFingerprint) -> int:
    result = 1
    for prime, exp in fp.exponents.items():
        result = math.lcm(result, prime**exp)
    return result


def fingerprint_similarity(a: WindowFingerprint, b: WindowFingerprint) -> float:
    sa = _fingerprint_lcm_value(a)
    sb = _fingerprint_lcm_value(b)
    if sa <= 0 or sb <= 0:
        return 0.0
    return substance_ggt_kgv_similarity(sa, sb)


def scan_windows(
    index: SubstanceIndex,
    width: int,
    target: WindowFingerprint,
    *,
    modes: list[str],
    skip_start: int | None = None,
) -> list[dict]:
    if width <= 0 or index.token_count < width:
        return []

    window_count = index.token_count - width + 1
    sliding: dict[int, list[int]] = {
        prime: _sliding_max_windows(series, width)
        for prime, series in index.exp_by_prime.items()
    }

    matches: list[dict] = []
    target_lcm = _fingerprint_lcm_value(target)

    for start in range(window_count):
        if skip_start is not None and start == skip_start:
            continue
        exponents: dict[int, int] = {}
        for prime, maxes in sliding.items():
            if start < len(maxes):
                exp = maxes[start]
                if exp:
                    exponents[prime] = exp
        fp = WindowFingerprint(exponents)
        window_lcm = _fingerprint_lcm_value(fp)
        sim = fingerprint_similarity(fp, target)

        if "anagram_shadow" in modes and sim >= 0.999:
            matches.append(
                {
                    "mode": "anagram_shadow",
                    "token_start": start,
                    "token_end": start + width,
                    "score_semantic": round(sim, 6),
                    "score": round(sim, 6),
                    "window_lcm": window_lcm,
                }
            )
        elif "substance_divisor" in modes and target_lcm > 1 and window_lcm > 1:
            if target_lcm % window_lcm == 0 or window_lcm % target_lcm == 0:
                if sim < 0.2 and target_lcm != window_lcm:
                    continue
                matches.append(
                    {
                        "mode": "substance_divisor",
                        "token_start": start,
                        "token_end": start + width,
                        "score_semantic": round(sim, 6),
                        "score": round(sim, 6),
                        "window_lcm": window_lcm,
                    }
                )
    return matches


def get_substance_index(document: GpmDocument) -> SubstanceIndex:
    idx = getattr(document, "substance_index", None)
    if idx is not None:
        return idx
    return build_substance_index(document)
