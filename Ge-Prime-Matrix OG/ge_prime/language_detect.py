"""Inkrementelles DB-Vektorgitter für Sprach-Audit (v49 Richtwert)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ge_prime.linguistics.registry import LANGUAGE_MIN_CONFIDENCE
from gpm.model import GpmDocument

if TYPE_CHECKING:
    from db.repository import WordRepository

PREVIEW_TOKEN_LIMIT = 30
KANONISCHER_MATRIX_RICHTWERT = 0.40
MIN_SIGNAL_WEIGHT_BUDGET = 1.5

# DEPRECATED in v49 — will be removed in v50
CONFIDENCE_ANOMALY_THRESHOLD = KANONISCHER_MATRIX_RICHTWERT
NOISE_WEIGHT_THRESHOLD = MIN_SIGNAL_WEIGHT_BUDGET


def _repo_cache_key(repo: WordRepository) -> str:
    return str(getattr(repo, "db_path", id(repo)))


def _preview_normalized_words(document: GpmDocument) -> list[str]:
    norms: list[str] = []
    seen: set[str] = set()
    for token in document.tokens[:PREVIEW_TOKEN_LIMIT]:
        norm = document.header[token.word_id].word_normalized
        if not norm or norm in seen:
            continue
        seen.add(norm)
        norms.append(norm)
    return norms


def _accumulate_language_vector(
    document: GpmDocument,
    repo: WordRepository,
) -> dict[str, float]:
    preview_norms = _preview_normalized_words(document)
    if not preview_norms:
        return {}

    bulk = repo.lookup_languages_bulk(preview_norms)
    language_vector: dict[str, float] = {}
    for norm in preview_norms:
        matches = bulk.get(norm) or {}
        if not matches:
            continue
        for lang, score in matches.items():
            language_vector[lang] = language_vector.get(lang, 0.0) + float(score)
    return language_vector


def _critical_payload(document: GpmDocument, *, db_audit_mode: str) -> dict:
    return {
        "primary_language": "unknown",
        "confidence": 0.0,
        "language_uncertain": True,
        "audit_status": "CRITICAL_ANOMALY",
        "unknown_language_flag": True,
        "foreign_tokens_found": len(document.tokens),
        "top_foreign_tokens": [],
        "vector_distribution": {},
        "expected_lang": "unknown",
        "db_audit_mode": db_audit_mode,
        "coverage_ratio": 0.0,
        "confirmed_count": 0,
        "ambiguous_count": 0,
        "unknown_count": 0,
        "other_lang_count": 0,
        "unique_tokens": 0,
        "sample_mismatches": [],
        "foreign_tokens": [],
        "available": False,
        "reason": "language_unknown",
    }


def _audit_lang_from_vector(language_vector: dict[str, float]) -> str | None:
    if not language_vector:
        return None
    primary = max(language_vector, key=language_vector.get)
    if primary in ("de", "en"):
        return primary
    de = language_vector.get("de", 0.0)
    en = language_vector.get("en", 0.0)
    if de > 0 or en > 0:
        return "de" if de >= en else "en"
    return None


def build_meta_genome_db_audit(
    document: GpmDocument,
    language: dict | None,
    repo: WordRepository | None,
    *,
    db_audit_mode: str = "de_en",
) -> dict:
    """Rollierender 30-Wort-Vektor-Scan gegen die Sprach-DB (Richtwert)."""
    if db_audit_mode == "off" or repo is None:
        return {
            "primary_language": (language or {}).get("code", "unknown"),
            "confidence": float((language or {}).get("confidence", 0.0) or 0.0),
            "language_uncertain": False,
            "audit_status": "VERIFIED",
            "vector_distribution": {},
            "unknown_language_flag": False,
            "foreign_tokens_found": 0,
            "top_foreign_tokens": [],
            "expected_lang": (language or {}).get("code", "unknown"),
            "db_audit_mode": db_audit_mode,
            "coverage_ratio": 0.0,
            "confirmed_count": 0,
            "ambiguous_count": 0,
            "unknown_count": 0,
            "other_lang_count": 0,
            "unique_tokens": 0,
            "sample_mismatches": [],
            "foreign_tokens": [],
            "available": False,
            "reason": "audit_off" if db_audit_mode == "off" else "no_repo",
        }

    lang_info = language or {}
    lang_code = lang_info.get("code", "unknown")
    classify_conf = float(lang_info.get("confidence", 0.0) or 0.0)
    language_vector = _accumulate_language_vector(document, repo)
    total_weight = sum(language_vector.values())

    if language_vector and total_weight > 0.0:
        primary_lang = max(language_vector, key=language_vector.get)
        confidence = language_vector[primary_lang] / total_weight
        primary_weight = language_vector[primary_lang]
    else:
        primary_lang = lang_code if lang_code in ("de", "en") else "unknown"
        confidence = classify_conf if lang_code in ("de", "en") else 0.0
        primary_weight = 0.0

    classified_certain = (
        lang_code in ("de", "en") and classify_conf >= LANGUAGE_MIN_CONFIDENCE
    )

    if classified_certain:
        audit_lang = lang_code
        language_uncertain = False
        audit_status = "VERIFIED"
    else:
        if not language_vector or total_weight <= 0.0:
            return _critical_payload(document, db_audit_mode=db_audit_mode)

        audit_status = "VERIFIED"
        language_uncertain = False

        if confidence < KANONISCHER_MATRIX_RICHTWERT:
            language_uncertain = True
            if primary_weight < MIN_SIGNAL_WEIGHT_BUDGET:
                return _critical_payload(document, db_audit_mode=db_audit_mode)

        from ge_prime.linguistics.language import resolve_db_audit_language

        audit_lang = _audit_lang_from_vector(language_vector)
        resolved_lang, inferred_uncertain = resolve_db_audit_language(lang_info)
        if inferred_uncertain:
            language_uncertain = True
        if audit_lang is None:
            audit_lang = resolved_lang
        if audit_lang is None:
            return _critical_payload(document, db_audit_mode=db_audit_mode)

        if language_uncertain:
            audit_status = "UNCERTAIN"

    from ge_prime.meta_genome import db_token_language_audit

    coverage = db_token_language_audit(
        document,
        repo,
        audit_lang,
        db_audit_mode=db_audit_mode,
    )
    coverage["language_uncertain"] = language_uncertain
    if language_uncertain:
        coverage["inferred_lang"] = audit_lang
    else:
        coverage.pop("inferred_lang", None)

    return {
        "primary_language": primary_lang,
        "confidence": round(confidence, 4),
        "language_uncertain": language_uncertain,
        "audit_status": audit_status,
        "vector_distribution": language_vector,
        "unknown_language_flag": False,
        "foreign_tokens_found": len(coverage.get("foreign_tokens") or []),
        "top_foreign_tokens": (coverage.get("foreign_tokens") or [])[:5],
        **coverage,
    }


def merge_db_speech_audit(a: dict | None, b: dict | None) -> dict | None:
    """Schlimmster Audit-Status aus zwei Seiten für Zone-1."""
    if not a and not b:
        return None
    if not a:
        return dict(b) if b else None
    if not b:
        return dict(a)

    rank = {"CRITICAL_ANOMALY": 3, "UNCERTAIN": 2, "VERIFIED": 1}

    def score(row: dict) -> int:
        status = row.get("audit_status") or "VERIFIED"
        base = rank.get(status, 0)
        if row.get("language_uncertain"):
            base = max(base, rank["UNCERTAIN"])
        return base

    return dict(a) if score(a) >= score(b) else dict(b)
