"""ggT, kgV und Ähnlichkeit zweier Substanzen (Buchstaben-Multimenge)."""

import math
from collections import Counter

from ge_prime.decode import get_ingredients


def substance_lcm(s1: int, s2: int) -> int:
    """Kleinste gemeinsame Vielfache zweier Substanzen (Vereinigungsmenge der Buchstaben)."""
    if s1 < 1 or s2 < 1:
        raise ValueError("Substanz muss >= 1 sein.")
    return math.lcm(s1, s2)


def substance_covers(container: int, required: int) -> bool:
    """True wenn container alle Primfaktoren von required enthält (container % required == 0)."""
    if required < 1:
        raise ValueError("Erforderliche Substanz muss >= 1 sein.")
    if container < 1:
        return False
    return container % required == 0


def union_letters(s1: int, s2: int) -> dict:
    """Buchstaben-Vereinigung zweier Substanzen über kgV."""
    lcm_value = substance_lcm(s1, s2)
    return dict(get_ingredients(lcm_value)) if lcm_value > 1 else {}


def substance_ggt_kgv_similarity(s1: int, s2: int) -> float:
    """ln(ggT) / ln(kgV) — Anagramm → 1.0."""
    gcd_val = math.gcd(s1, s2)
    if gcd_val <= 1 or s1 <= 1 or s2 <= 1:
        return 0.0
    lcm_val = math.lcm(s1, s2)
    ln_gcd = math.log(gcd_val)
    ln_kgv = math.log(lcm_val)
    if ln_kgv <= 0:
        return 0.0
    return ln_gcd / ln_kgv


def substance_ggt_kgv_distance(s1: int, s2: int) -> float:
    """DTW-Punktabstand auf [0, 1] — 0 bei identischer Substanz."""
    return 1.0 - substance_ggt_kgv_similarity(s1, s2)


def substance_transition_similarity(s_prev: int, s_curr: int) -> float:
    """ggT/kgV-Ähnlichkeit zwischen aufeinanderfolgenden Substanzen."""
    return substance_ggt_kgv_similarity(s_prev, s_curr)


def substance_log_similarity(s1: int, s2: int) -> float:
    """Alias — ln(ggT)/ln(kgV)."""
    return substance_ggt_kgv_similarity(s1, s2)


def substance_log_distance(s1: int, s2: int) -> float:
    return substance_ggt_kgv_distance(s1, s2)


def compare_substances(s1: int, s2: int) -> dict:
    """Vergleicht zwei Substanzen: ggT (Schnittmenge) und kgV (Vereinigung)."""
    gcd_value = math.gcd(s1, s2)
    shared = get_ingredients(gcd_value) if gcd_value > 1 else Counter()

    s1_unique = _relative_ingredients(s1, gcd_value)
    s2_unique = _relative_ingredients(s2, gcd_value)

    lcm_value = substance_lcm(s1, s2)
    union = get_ingredients(lcm_value) if lcm_value > 1 else Counter()

    smaller = min(s1, s2)
    legacy_similarity = gcd_value / smaller if smaller > 0 else 0.0
    ggt_kgv_sim = substance_ggt_kgv_similarity(s1, s2)

    return {
        "gcd_value": gcd_value,
        "lcm_value": lcm_value,
        "kgv_value": lcm_value,
        "shared_letters": dict(shared),
        "union_letters": dict(union),
        "unique_to_first": dict(s1_unique),
        "unique_to_second": dict(s2_unique),
        "similarity_ratio": round(legacy_similarity, 6),
        "legacy_similarity_ratio": round(legacy_similarity, 6),
        "ggt_kgv_similarity": round(ggt_kgv_sim, 6),
    }


def _relative_ingredients(value: int, divisor: int) -> Counter:
    if divisor <= 0 or value <= 0:
        return Counter()
    quotient = value // divisor
    return get_ingredients(quotient) if quotient > 1 else Counter()
