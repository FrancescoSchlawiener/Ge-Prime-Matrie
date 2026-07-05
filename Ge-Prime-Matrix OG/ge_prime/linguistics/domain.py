"""Domänenerkennung — Keywords + Profil, Fallback auf allgemein."""

from __future__ import annotations

from collections import Counter
from typing import TYPE_CHECKING

from functools import lru_cache

from ge_prime.linguistics.profiles import domain_seed_profile, normalized_token_counts, profile_overlap
from ge_prime.relation_profile import build_relation_profile, score_domain_relations
from ge_prime.linguistics.registry import (
    DOMAIN_MIN_MARGIN,
    DOMAIN_UNKNOWN_LANG_THRESHOLD,
    DOMAIN_WEIGHT_KEYWORDS,
    DOMAIN_WEIGHT_PROFILE,
    DOMAIN_WEIGHT_RELATIONS,
    DomainSpec,
    domain_label,
    get_domain,
    iter_domains,
)
from gpm.model import GpmDocument

if TYPE_CHECKING:
    from db.repository import WordRepository


@lru_cache(maxsize=128)
def _domain_reference_profile(domain_code: str, lang_code: str) -> Counter:
    spec = get_domain(domain_code)
    if spec is None:
        return Counter()
    seed = spec.profile_seed.get(lang_code, "")
    return domain_seed_profile(seed) if seed else Counter()


def _keyword_score(token_counts: Counter, keywords: frozenset[str]) -> tuple[float, list[str]]:
    if not keywords or not token_counts:
        return 0.0, []
    unique = len(token_counts) or 1
    weighted_hits = 0.0
    matched: list[str] = []
    for word, count in token_counts.items():
        if word in keywords:
            weighted_hits += count
            matched.append(word.lower())
    score = weighted_hits / (unique ** 0.5)
    return min(1.0, score), matched[:6]


def _languages_for_domain_detection(language_code: str) -> list[str]:
    if language_code in ("de", "en"):
        return [language_code]
    return ["de", "en"]


def _score_domain(
    spec: DomainSpec,
    *,
    profile: Counter,
    token_counts: Counter,
    lang_code: str,
    relation_profile: dict | None = None,
) -> tuple[float, list[str], int]:
    keywords = spec.keywords.get(lang_code, frozenset())
    kw_score, matched = _keyword_score(token_counts, keywords)
    seed = spec.profile_seed.get(lang_code, "")
    seed_profile = _domain_reference_profile(spec.code, lang_code) if seed else Counter()
    prof_score = profile_overlap(profile, seed_profile) if seed_profile else 0.0
    rel_score = 0.0
    if relation_profile and seed:
        rel_score = score_domain_relations(seed, relation_profile)
    combined = (
        DOMAIN_WEIGHT_KEYWORDS * kw_score
        + DOMAIN_WEIGHT_PROFILE * prof_score
        + DOMAIN_WEIGHT_RELATIONS * rel_score
    )
    hit_count = sum(1 for w in token_counts if w in keywords)
    return combined, matched, hit_count


def classify_domain(
    document: GpmDocument,
    profile: Counter,
    language_code: str,
    repo: WordRepository | None = None,
) -> dict:
    """Domäne erkennen; bei niedriger Konfidenz → allgemein."""
    _ = repo
    token_counts = normalized_token_counts(document)
    relation_profile = build_relation_profile(document)
    langs = _languages_for_domain_detection(language_code)
    threshold_scale = 1.0 if language_code in ("de", "en") else DOMAIN_UNKNOWN_LANG_THRESHOLD / 0.28

    raw_scores: dict[str, float] = {}
    matched_by_domain: dict[str, list[str]] = {}
    hits_by_domain: dict[str, int] = {}

    for spec in iter_domains(active_only=True):
        best_score = 0.0
        best_matched: list[str] = []
        best_hits = 0
        for lang in langs:
            if lang not in spec.keywords:
                continue
            score, matched, hit_count = _score_domain(
                spec,
                profile=profile,
                token_counts=token_counts,
                lang_code=lang,
                relation_profile=relation_profile,
            )
            if score > best_score:
                best_score = score
                best_matched = matched
                best_hits = hit_count
        raw_scores[spec.code] = best_score
        matched_by_domain[spec.code] = best_matched
        hits_by_domain[spec.code] = best_hits

    general = get_domain("general")
    assert general is not None

    if not raw_scores:
        label_lang = language_code if language_code in ("de", "en") else "de"
        return {
            "code": "general",
            "label": domain_label(general, label_lang),
            "confidence": 0.0,
            "scores": {},
            "matched_keywords": [],
            "fallback": True,
        }

    ranked = sorted(raw_scores.items(), key=lambda item: item[1], reverse=True)
    best_code, best_score = ranked[0]
    second_score = ranked[1][1] if len(ranked) > 1 else 0.0
    margin = best_score - second_score
    best_spec = get_domain(best_code)
    assert best_spec is not None

    min_conf = best_spec.min_confidence * threshold_scale
    min_hits = best_spec.min_keyword_hits
    hit_count = hits_by_domain.get(best_code, 0)

    label_lang = language_code if language_code in ("de", "en") else "de"
    fallback = (
        best_score < min_conf
        or hit_count < min_hits
        or margin < DOMAIN_MIN_MARGIN
    )

    if fallback:
        return {
            "code": "general",
            "label": domain_label(general, label_lang),
            "confidence": round(best_score, 6),
            "scores": {k: round(v, 6) for k, v in raw_scores.items()},
            "matched_keywords": matched_by_domain.get(best_code, [])[:6],
            "fallback": True,
        }

    return {
        "code": best_code,
        "label": domain_label(best_spec, label_lang),
        "confidence": round(best_score, 6),
        "scores": {k: round(v, 6) for k, v in raw_scores.items()},
        "matched_keywords": matched_by_domain.get(best_code, [])[:6],
        "fallback": False,
    }
