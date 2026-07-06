"""Meta-Genom Fingerprint — Profil-Vektor V und ggT-Vergleich."""

from __future__ import annotations

import math
from collections import Counter

from alphabets import AlphabetProfile
from alphabets.registry import char_map_for_profile, prime_map_for_profile

MAX_SAFE_VECTOR_DIGITS = 4000


def profile_to_vector(profile: Counter[int]) -> int:
    """Dokumenten-Vektor V = ∏ p^e über alle Primfaktoren."""
    value = 1
    for prime, exp in profile.items():
        if exp:
            value *= pow(int(prime), int(exp))
    return value


def _profile_log10_digits(profile: Counter[int]) -> float:
    return sum(exp * math.log10(prime) for prime, exp in profile.items() if exp)


def profile_bit_length(profile: Counter[int]) -> int:
    if not profile:
        return 0
    log2_v = sum(exp * math.log2(prime) for prime, exp in profile.items() if exp)
    return max(1, int(log2_v) + 1)


def profile_vector_fields(profile: Counter[int]) -> tuple[str, int]:
    est_digits = _profile_log10_digits(profile)
    bits = profile_bit_length(profile)
    if est_digits <= MAX_SAFE_VECTOR_DIGITS:
        vector = profile_to_vector(profile)
        return str(vector), vector.bit_length()
    label = f"∏{len(profile)} Primfaktoren (~{int(est_digits):,} Ziffern)".replace(",", ".")
    return label, bits


def prime_profile_from_int(value: int, profile: AlphabetProfile | str) -> Counter[int]:
    result: Counter[int] = Counter()
    remaining = value
    prime_map = prime_map_for_profile(profile)
    for prime in sorted(set(prime_map.values())):
        while remaining % prime == 0:
            result[prime] += 1
            remaining //= prime
    return result


def profile_from_meta(meta: dict, *, document_profile: AlphabetProfile | str | None = None) -> Counter[int]:
    raw = meta.get("profile")
    if raw:
        return Counter({int(k): int(v) for k, v in raw.items()})
    vector_raw = meta.get("vector")
    if (
        document_profile is not None
        and isinstance(vector_raw, str)
        and vector_raw.isdigit()
        and len(vector_raw) <= MAX_SAFE_VECTOR_DIGITS
    ):
        return prime_profile_from_int(int(vector_raw), document_profile)
    return Counter()


def profile_shared_letters(
    shared_profile: Counter[int],
    profile: AlphabetProfile | str,
) -> dict[str, int]:
    char_map = char_map_for_profile(profile)
    letters: dict[str, int] = {}
    for prime, exp in shared_profile.items():
        char = char_map.get(prime)
        if char and exp:
            letters[char] = exp
    return letters


def compare_profiles(
    profile_a: Counter[int],
    profile_b: Counter[int],
    *,
    document_profile: AlphabetProfile | str | None = None,
) -> dict:
    keys = set(profile_a) | set(profile_b)
    shared_profile = Counter[int]()
    log_gcd = 0.0
    log_a = 0.0
    log_b = 0.0
    log_lcm = 0.0
    shared_prime_entries: list[dict] = []

    for prime in keys:
        a = profile_a.get(prime, 0)
        b = profile_b.get(prime, 0)
        shared = min(a, b)
        combined = max(a, b)
        if shared:
            shared_profile[prime] = shared
            log_gcd += shared * math.log(prime)
            shared_prime_entries.append(
                {"prime": prime, "exp_a": a, "exp_b": b, "shared": shared}
            )
        if a:
            log_a += a * math.log(prime)
        if b:
            log_b += b * math.log(prime)
        if combined:
            log_lcm += combined * math.log(prime)

    zero_reason: str | None = None
    if not profile_a:
        zero_reason = "empty_profile_a"
    elif not profile_b:
        zero_reason = "empty_profile_b"
    elif log_gcd <= 0:
        zero_reason = "no_shared_primes"

    if log_gcd <= 0 or log_lcm <= 0:
        similarity = 0.0
    else:
        similarity = log_gcd / log_lcm
    similarity = round(min(1.0, max(0.0, similarity)), 6)

    gcd_digits = _profile_log10_digits(shared_profile)
    if gcd_digits <= MAX_SAFE_VECTOR_DIGITS and shared_profile:
        gcd_value = str(profile_to_vector(shared_profile))
    elif shared_profile:
        gcd_value = f"ggT-Profil ({len(shared_profile)} Primfaktoren, ~{int(gcd_digits):,} Ziffern)".replace(",", ".")
    else:
        gcd_value = "1"

    shared_letters: dict[str, int] = {}
    if document_profile is not None and shared_profile:
        shared_letters = profile_shared_letters(shared_profile, document_profile)

    return {
        "gcd_value": gcd_value,
        "similarity_ratio": similarity,
        "ggt_kgv_similarity": similarity,
        "shared_letters": shared_letters,
        "shared_profile": shared_profile,
        "log_gcd": round(log_gcd, 6),
        "log_a": round(log_a, 6),
        "log_b": round(log_b, 6),
        "log_lcm": round(log_lcm, 6),
        "shared_prime_count": len(shared_prime_entries),
        "shared_prime_entries": shared_prime_entries,
        "zero_reason": zero_reason,
    }
