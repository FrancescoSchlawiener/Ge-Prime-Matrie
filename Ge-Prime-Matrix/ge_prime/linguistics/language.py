"""Spracherkennung — Funktionswort-Muster, DB-Profile, Hybrid-Score."""

from __future__ import annotations

from collections import Counter
from typing import TYPE_CHECKING

from ge_prime.core import PRIME_MAP
from ge_prime.linguistics.profiles import (
    language_detection_method,
    language_reference_profile,
    normalized_token_counts,
    profile_overlap,
)
from ge_prime.linguistics.registry import (
    LANG_WEIGHT_PATTERNS,
    LANG_WEIGHT_PROFILE,
    LANG_WEIGHT_SIGNALS,
    LANGUAGE_MIN_CONFIDENCE,
    LANGUAGE_MIN_MARGIN,
    LanguageSpec,
    iter_languages,
)
from gpm.model import GpmDocument

if TYPE_CHECKING:
    from db.repository import WordRepository

# Nur de/en in der Wort-DB speichern — sonst random (Linguistik-Fallback)
_DB_STORED_LANGUAGES = frozenset({"de", "en"})
# Etwas toleranter als classify_language (Meta-Genom), damit Scraper/Encode sinnvoll taggen
_DB_TAG_MIN_SCORE = 0.28
_DB_TAG_MIN_MARGIN = 0.11


def _function_word_rate(token_counts: Counter, spec: LanguageSpec) -> float:
    if not token_counts:
        return 0.0
    hits = sum(count for word, count in token_counts.items() if word in spec.function_words)
    total = sum(token_counts.values())
    return hits / total if total else 0.0


def _language_signal_score(profile: Counter, spec: LanguageSpec) -> float:
    total_mass = sum(profile.values()) or 1
    eszett_mass = profile.get(PRIME_MAP["ß"], 0)
    score = 0.0
    if spec.signals.get("eszett_boost") and eszett_mass > 0:
        boost = spec.signals["eszett_boost"]
        score += min(boost, eszett_mass / total_mass)
    if spec.signals.get("eszett_penalty") and eszett_mass > 0:
        penalty = spec.signals["eszett_penalty"]
        score = max(0.0, score - min(penalty, eszett_mass / total_mass))
    return min(1.0, score)


def _score_language(
    spec: LanguageSpec,
    *,
    profile: Counter,
    token_counts: Counter,
    repo: WordRepository | None,
) -> tuple[float, str]:
    ref_profile, ref_method = language_reference_profile(spec, repo)
    pattern = _function_word_rate(token_counts, spec)
    overlap = profile_overlap(profile, ref_profile) if ref_profile else 0.0
    signal = _language_signal_score(profile, spec)
    score = (
        LANG_WEIGHT_PATTERNS * pattern
        + LANG_WEIGHT_PROFILE * overlap
        + LANG_WEIGHT_SIGNALS * signal
    )
    return min(1.0, max(0.0, score)), ref_method


def classify_language(
    document: GpmDocument,
    profile: Counter,
    repo: WordRepository | None = None,
) -> dict:
    """Hybrid-Spracherkennung mit Fallback auf unknown bei niedriger Konfidenz."""
    token_counts = normalized_token_counts(document)
    eszett_mass = int(profile.get(PRIME_MAP["ß"], 0))
    methods_seen: set[str] = set()
    raw_scores: dict[str, float] = {}

    for spec in iter_languages():
        score, ref_method = _score_language(
            spec, profile=profile, token_counts=token_counts, repo=repo
        )
        raw_scores[spec.code] = score
        methods_seen.add(ref_method)

    if not raw_scores:
        return {
            "code": "unknown",
            "label": "Unklar",
            "scores": {},
            "confidence": 0.0,
            "method": "patterns",
            "has_eszett": eszett_mass > 0,
            "eszett_mass": eszett_mass,
        }

    ranked = sorted(raw_scores.items(), key=lambda item: item[1], reverse=True)
    best_code, best_score = ranked[0]
    second_score = ranked[1][1] if len(ranked) > 1 else 0.0
    margin = best_score - second_score

    total = sum(raw_scores.values()) or 1.0
    confidence = best_score

    if confidence < LANGUAGE_MIN_CONFIDENCE or margin < LANGUAGE_MIN_MARGIN:
        return {
            "code": "unknown",
            "label": "Unklar",
            "scores": {k: round(v, 6) for k, v in raw_scores.items()},
            "confidence": round(confidence, 6),
            "method": language_detection_method(repo),
            "has_eszett": eszett_mass > 0,
            "eszett_mass": eszett_mass,
        }

    spec = next(s for s in iter_languages() if s.code == best_code)
    method = language_detection_method(repo)
    if "db" in methods_seen and method == "patterns":
        method = "hybrid"

    return {
        "code": best_code,
        "label": spec.label,
        "scores": {k: round(v, 6) for k, v in raw_scores.items()},
        "confidence": round(confidence, 6),
        "method": method,
        "has_eszett": eszett_mass > 0,
        "eszett_mass": eszett_mass,
    }


def resolve_db_audit_language(language: dict) -> tuple[str | None, bool]:
    """Sprache für den DB-Audit — auch bei Meta-Genom „Unklar“ aus de/en-Scores."""
    code = language.get("code", "unknown")
    if code in _DB_STORED_LANGUAGES:
        return code, False

    scores = language.get("scores") or {}
    de = float(scores.get("de", 0.0))
    en = float(scores.get("en", 0.0))

    if de >= _DB_TAG_MIN_SCORE and de - en >= _DB_TAG_MIN_MARGIN:
        return "de", True
    if en >= _DB_TAG_MIN_SCORE and en - de >= _DB_TAG_MIN_MARGIN:
        return "en", True

    if de > 0.0 or en > 0.0:
        return ("de", True) if de >= en else ("en", True)

    return None, True


def infer_text_language_code(text: str, repo: WordRepository | None = None) -> str:
    """Sprach-Tag für DB-Speicherung: de/en wenn erkennbar, sonst random."""
    from db.language import LANGUAGE_RANDOM

    cleaned = (text or "").strip()
    if not cleaned:
        return LANGUAGE_RANDOM

    from ge_prime.linguistics.profiles import build_prime_profile, resolve_linguistics_repo
    from gpm.compiler import compile_text

    document, _, _ = compile_text(cleaned)
    profile = build_prime_profile(document)
    if len(document.tokens) < 3:
        return LANGUAGE_RANDOM
    ling_repo = resolve_linguistics_repo(repo)
    result = classify_language(document, profile, ling_repo)
    code = result.get("code", "unknown")
    if code in _DB_STORED_LANGUAGES:
        return code

    audit_lang, _ = resolve_db_audit_language(result)
    if audit_lang:
        return audit_lang
    return LANGUAGE_RANDOM
