"""Sparse Prime-Exponent-Gitter — Fenster-LCM in O(n · #primes_doc)."""

from __future__ import annotations

from collections import Counter, deque
from dataclasses import dataclass, field

from alphabets import AlphabetProfile
from alphabets.registry import char_map_for_profile
from analysis.algebra.window_fold import (
    ExponentWindow,
    exponent_window_to_substance,
    fold_window_from_series,
    fold_window_from_token_exponents,
    window_similarity,
)
from analysis.document.model import GpmDocument
from gpm_types.si.substance import ingredients_for_profile

WindowFingerprint = ExponentWindow


SPARSE_TOKEN_THRESHOLD = 8192


@dataclass
class SubstanceIndex:
    token_count: int
    exp_by_prime: dict[int, list[int]] = field(default_factory=dict)
    per_token: list[dict[int, int]] | None = None
    sparse: bool = False

    def primes(self) -> list[int]:
        if self.exp_by_prime:
            return sorted(self.exp_by_prime.keys())
        if self.per_token:
            keys: set[int] = set()
            for exps in self.per_token:
                keys.update(exps.keys())
            return sorted(keys)
        return []


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


def build_substance_index(
    document: GpmDocument,
    *,
    mode: str = "auto",
) -> SubstanceIndex:
    n = len(document.tokens)
    use_sparse = mode == "sparse" or (mode == "auto" and n > SPARSE_TOKEN_THRESHOLD)
    profile = document.profile

    per_token: list[dict[int, int]] = []
    prime_set: set[int] = set()
    for token in document.tokens:
        entry = document.header[token.word_id]
        exps = _prime_exponents(entry.substance, profile)
        per_token.append(exps)
        prime_set.update(exps.keys())

    if use_sparse:
        return SubstanceIndex(
            token_count=n,
            exp_by_prime={},
            per_token=per_token,
            sparse=True,
        )

    exp_by_prime: dict[int, list[int]] = {}
    for prime in sorted(prime_set):
        exp_by_prime[prime] = [exps.get(prime, 0) for exps in per_token]

    return SubstanceIndex(token_count=n, exp_by_prime=exp_by_prime, per_token=per_token, sparse=False)


def window_fingerprint(index: SubstanceIndex, start: int, end: int) -> WindowFingerprint:
    if start < 0:
        start = 0
    if end > index.token_count:
        end = index.token_count
    if start >= end:
        return WindowFingerprint({})
    if index.sparse and index.per_token is not None:
        return fold_window_from_token_exponents(index.per_token, start, end)
    return fold_window_from_series(index.exp_by_prime, start, end)


def _fingerprint_lcm_value(fp: WindowFingerprint) -> int:
    return exponent_window_to_substance(fp)


def fingerprint_similarity(
    a: WindowFingerprint,
    b: WindowFingerprint,
    *,
    profile: AlphabetProfile | None = None,
) -> float:
    """Härtungs-Inv. E-A: mit profile → Log-Raum via window_similarity, sonst Legacy-LCM."""
    if profile is not None:
        score, _ = window_similarity(a, b, profile_a=profile, profile_b=profile)
        return score
    sa = _fingerprint_lcm_value(a)
    sb = _fingerprint_lcm_value(b)
    if sa <= 0 or sb <= 0:
        return 0.0
    from analysis.algebra.substance_kernel import substance_ggt_kgv_similarity

    return substance_ggt_kgv_similarity(sa, sb)


def scan_windows(
    index: SubstanceIndex,
    width: int,
    target: WindowFingerprint,
    *,
    modes: list[str],
    skip_start: int | None = None,
    profile: AlphabetProfile | None = None,
) -> list[dict]:
    if width <= 0 or index.token_count < width:
        return []

    if index.sparse and index.per_token is not None:
        window_count = index.token_count - width + 1
        matches: list[dict] = []
        target_lcm = _fingerprint_lcm_value(target)
        for start in range(window_count):
            if skip_start is not None and start == skip_start:
                continue
            exponents: dict[int, int] = {}
            for exps in index.per_token[start : start + width]:
                for prime, exp in exps.items():
                    if exp:
                        exponents[prime] = max(exponents.get(prime, 0), exp)
            fp = WindowFingerprint(exponents)
            window_lcm = _fingerprint_lcm_value(fp)
            sim = fingerprint_similarity(fp, target, profile=profile)
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
        sim = fingerprint_similarity(fp, target, profile=profile)

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


def get_substance_index(document: GpmDocument, *, mode: str = "auto") -> SubstanceIndex:
    idx = getattr(document, "substance_index", None)
    if idx is not None:
        return idx
    idx = build_substance_index(document, mode=mode)
    document.substance_index = idx
    return idx
