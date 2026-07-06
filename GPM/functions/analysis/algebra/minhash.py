"""MinHash auf Prim-Profilen — Härtungs-Invariante A (Exponent + Salt)."""

from __future__ import annotations

import hashlib
from collections import Counter

from alphabets import AlphabetProfile


def _hash_token(salt: str, prime: int, k: int) -> int:
    payload = f"{salt}:{prime}:{k}".encode()
    digest = hashlib.sha256(payload).hexdigest()
    return int(digest[:16], 16)


def prime_minhash(
    prime_profile: Counter[int],
    *,
    alphabet_profile: AlphabetProfile,
    bands: int = 64,
) -> tuple[int, ...]:
    salt = alphabet_profile.value
    digests: list[int] = []
    for prime, exp in sorted(prime_profile.items()):
        if exp <= 0:
            continue
        for k in range(exp):
            digests.append(_hash_token(salt, prime, k))
    if not digests:
        return tuple()
    digests.sort()
    if len(digests) <= bands:
        return tuple(digests)
    step = max(1, len(digests) // bands)
    sampled = [digests[i] for i in range(0, len(digests), step)][:bands]
    return tuple(sampled)


def minhash_band_distance(
    a: tuple[int, ...] | None,
    b: tuple[int, ...] | None,
) -> float:
    """Jaccard-ähnliche Band-Übereinstimmung für Vorfilter (0.0–1.0)."""
    if not a or not b:
        return 0.0
    set_a = set(a)
    set_b = set(b)
    union = set_a | set_b
    if not union:
        return 0.0
    return len(set_a & set_b) / len(union)
