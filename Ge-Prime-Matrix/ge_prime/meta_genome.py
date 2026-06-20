"""Meta-Genom — Dokumenten-Vektor V aus Header-Genomen.

Aus Häufigkeiten der Header-Substanzen entsteht V = ∏ S^count.
Sprache/Domäne: ``ge_prime.linguistics``; Plagiats-Signale mit I-Kurve.
"""

from __future__ import annotations

import math
from collections import Counter
from typing import TYPE_CHECKING

from ge_prime.core import CHAR_MAP, PRIME_MAP
from ge_prime.linguistics.domain import classify_domain
from ge_prime.language_detect import build_meta_genome_db_audit, merge_db_speech_audit
from ge_prime.linguistics.language import classify_language
from ge_prime.linguistics.profiles import build_prime_profile, resolve_linguistics_repo
from ge_prime.relation_profile import (
    SAME_DOMAIN_RELATIONAL_THRESHOLD,
    build_relation_profile,
    compare_relation_profiles,
    relation_twins,
)
from gpm.compiler import compile_text
from gpm.model import GpmDocument
from pipeline.normalize import apply_case

if TYPE_CHECKING:
    from db.repository import WordRepository

DOMAIN_SIMILARITY_THRESHOLD = 0.12
_POOL_SIZES_CACHE: dict[str, int] | None = None


def _language_pool_sizes(repo: WordRepository | None) -> dict[str, int]:
    global _POOL_SIZES_CACHE
    if repo is None:
        return {}
    if _POOL_SIZES_CACHE is None:
        _POOL_SIZES_CACHE = repo.count_words_by_language()
    return _POOL_SIZES_CACHE
META_PLAGIARISM_GENOME_THRESHOLD = 0.18
COMBINED_PLAGIARISM_THRESHOLD = 0.55
DB_LANGUAGE_COVERAGE_THRESHOLD = 0.5
MIXED_LANGUAGE_RATIO_THRESHOLD = 0.30
TOP_WORDS_LIMIT = 15
MAX_SAFE_VECTOR_DIGITS = 4000


def profile_to_vector(profile: Counter) -> int:
    """Dokumenten-Vektor V = ∏ p^e über alle Primfaktoren."""
    value = 1
    for prime, exp in profile.items():
        if exp:
            value *= pow(int(prime), int(exp))
    return value


def _profile_log10_digits(profile: Counter) -> float:
    return sum(exp * math.log10(prime) for prime, exp in profile.items() if exp)


def profile_bit_length(profile: Counter) -> int:
    if not profile:
        return 0
    log2_v = sum(exp * math.log2(prime) for prime, exp in profile.items() if exp)
    return max(1, int(log2_v) + 1)


def _profile_vector_fields(profile: Counter) -> tuple[str, int]:
    est_digits = _profile_log10_digits(profile)
    bits = profile_bit_length(profile)
    if est_digits <= MAX_SAFE_VECTOR_DIGITS:
        vector = profile_to_vector(profile)
        return str(vector), vector.bit_length()
    label = f"∏{len(profile)} Primfaktoren (~{int(est_digits):,} Ziffern)".replace(",", ".")
    return label, bits


def _prime_profile_from_int(value: int) -> Counter:
    profile = Counter()
    remaining = value
    for prime in sorted(set(PRIME_MAP.values())):
        while remaining % prime == 0:
            profile[prime] += 1
            remaining //= prime
    return profile


def _profile_from_meta(meta: dict) -> Counter:
    raw = meta.get("profile")
    if raw:
        return Counter({int(k): int(v) for k, v in raw.items()})
    vector_raw = meta.get("vector")
    if isinstance(vector_raw, str) and vector_raw.isdigit() and len(vector_raw) <= MAX_SAFE_VECTOR_DIGITS:
        return _prime_profile_from_int(int(vector_raw))
    return Counter()


def _profile_shared_letters(shared_profile: Counter) -> dict[str, int]:
    letters: dict[str, int] = {}
    for prime, exp in shared_profile.items():
        char = CHAR_MAP.get(prime)
        if char and exp:
            letters[char] = exp
    return letters


def compare_profiles(profile_a: Counter, profile_b: Counter) -> dict:
    keys = set(profile_a) | set(profile_b)
    shared_profile = Counter()
    log_gcd = 0.0
    log_a = 0.0
    log_b = 0.0

    for prime in keys:
        a = profile_a.get(prime, 0)
        b = profile_b.get(prime, 0)
        shared = min(a, b)
        if shared:
            shared_profile[prime] = shared
            log_gcd += shared * math.log(prime)
        if a:
            log_a += a * math.log(prime)
        if b:
            log_b += b * math.log(prime)

    if log_a <= 0 or log_b <= 0 or log_gcd <= 0:
        similarity = 0.0
    elif log_a <= log_b:
        similarity = math.exp(log_gcd - log_a)
    else:
        similarity = math.exp(log_gcd - log_b)
    similarity = round(min(1.0, max(0.0, similarity)), 6)

    gcd_digits = _profile_log10_digits(shared_profile)
    if gcd_digits <= MAX_SAFE_VECTOR_DIGITS and shared_profile:
        gcd_value = str(profile_to_vector(shared_profile))
    elif shared_profile:
        gcd_value = f"ggT-Profil ({len(shared_profile)} Primfaktoren, ~{int(gcd_digits):,} Ziffern)".replace(",", ".")
    else:
        gcd_value = "1"

    return {
        "gcd_value": gcd_value,
        "similarity_ratio": similarity,
        "ggt_kgv_similarity": similarity,
        "shared_letters": _profile_shared_letters(shared_profile),
        "shared_profile": shared_profile,
    }


def _word_frequencies(document: GpmDocument) -> Counter:
    counts: Counter = Counter()
    for token in document.tokens:
        counts[token.word_id] += 1
    return counts


def db_token_language_audit(
    document: GpmDocument,
    repo: WordRepository | None,
    expected_lang: str,
    *,
    db_audit_mode: str = "de_en",
) -> dict:
    """Prüft unique Token gegen Wort-DB (de/en oder alle Sprachen per Bulk-Lookup)."""
    empty = {
        "expected_lang": expected_lang,
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
    }
    if db_audit_mode == "off" or repo is None or expected_lang not in ("de", "en"):
        reason = "audit_off" if db_audit_mode == "off" else "no_repo" if repo is None else "language_unknown"
        return {**empty, "reason": reason}

    mode = db_audit_mode if db_audit_mode in ("de_en", "all_db") else "de_en"
    other = "en" if expected_lang == "de" else "de"

    norm_freq: Counter = Counter()
    norm_word: dict[str, str] = {}
    for token in document.tokens:
        entry = document.header[token.word_id]
        norm = entry.word_normalized
        norm_freq[norm] += 1
        if norm not in norm_word:
            norm_word[norm] = apply_case(entry.word_original, 0)

    unique_norms = list(norm_freq.keys())
    bulk = repo.lookup_languages_bulk(unique_norms)
    pool_sizes = _language_pool_sizes(repo)

    confirmed = 0
    ambiguous = 0
    unknown = 0
    other_lang = 0
    foreign_candidates: list[dict] = []

    for norm in unique_norms:
        lang_counts = bulk.get(norm, {})
        in_expected = expected_lang in lang_counts

        if mode == "de_en":
            in_other = other in lang_counts
            if in_expected and in_other:
                ambiguous += 1
            elif in_expected:
                confirmed += 1
            elif in_other:
                other_lang += 1
                foreign_candidates.append(
                    {
                        "word": norm_word[norm],
                        "normalized": norm,
                        "detected_lang": other,
                        "expected_lang": expected_lang,
                        "pool_size": pool_sizes.get(other, 0),
                        "freq": norm_freq[norm],
                    }
                )
            else:
                unknown += 1
        else:
            if not lang_counts:
                unknown += 1
            elif in_expected:
                if len(lang_counts) == 1:
                    confirmed += 1
                else:
                    ambiguous += 1
            else:
                dominant = max(lang_counts, key=lang_counts.get)
                other_lang += 1
                foreign_candidates.append(
                    {
                        "word": norm_word[norm],
                        "normalized": norm,
                        "detected_lang": dominant,
                        "expected_lang": expected_lang,
                        "pool_size": pool_sizes.get(dominant, 0),
                        "freq": norm_freq[norm],
                    }
                )

    unique = len(unique_norms)
    coverage = confirmed / unique if unique else 0.0
    foreign_candidates.sort(key=lambda row: (-row["freq"], row["normalized"]))
    foreign_tokens = [
        {k: v for k, v in row.items() if k != "freq"}
        for row in foreign_candidates[:5]
    ]
    sample_mismatches = [row["normalized"] for row in foreign_tokens]

    return {
        "expected_lang": expected_lang,
        "db_audit_mode": mode,
        "coverage_ratio": round(coverage, 6),
        "confirmed_count": confirmed,
        "ambiguous_count": ambiguous,
        "unknown_count": unknown,
        "other_lang_count": other_lang,
        "unique_tokens": unique,
        "sample_mismatches": sample_mismatches,
        "foreign_tokens": foreign_tokens,
        "available": True,
    }


def build_meta_genome(
    document: GpmDocument,
    repo: WordRepository | None = None,
    *,
    db_audit_mode: str = "de_en",
) -> dict:
    freqs = _word_frequencies(document)
    profile = build_prime_profile(document)
    vector_label, vector_bits = _profile_vector_fields(profile)
    total_tokens = sum(freqs.values())

    top_rows = []
    for word_id, count in freqs.most_common(TOP_WORDS_LIMIT):
        entry = document.header[word_id]
        top_rows.append(
            {
                "word_id": word_id,
                "word": apply_case(entry.word_original, 0),
                "normalized": entry.word_normalized,
                "substance": entry.substance,
                "count": count,
                "weight": round(count / total_tokens, 6) if total_tokens else 0.0,
            }
        )

    ling_repo = resolve_linguistics_repo(repo)
    language = classify_language(document, profile, ling_repo)
    if db_audit_mode != "off" and repo is not None:
        language = dict(language)
        speech_audit = build_meta_genome_db_audit(
            document,
            language,
            repo,
            db_audit_mode=db_audit_mode,
        )
        language["db_speech_audit"] = speech_audit
        language["db_coverage"] = {
            key: speech_audit[key]
            for key in (
                "expected_lang",
                "db_audit_mode",
                "coverage_ratio",
                "confirmed_count",
                "ambiguous_count",
                "unknown_count",
                "other_lang_count",
                "unique_tokens",
                "sample_mismatches",
                "foreign_tokens",
                "available",
                "language_uncertain",
                "inferred_lang",
                "reason",
            )
            if key in speech_audit
        }
    lang_code = language.get("code", "unknown")
    domain = classify_domain(document, profile, lang_code, ling_repo)
    relation_profile = build_relation_profile(document)

    return {
        "vector": vector_label,
        "vector_bits": vector_bits,
        "profile": {str(p): c for p, c in sorted(profile.items())},
        "prime_factor_count": len(profile),
        "total_letter_mass": sum(profile.values()),
        "unique_words": len(document.header),
        "token_count": total_tokens,
        "top_words": top_rows,
        "language": language,
        "domain": domain,
        "relation_profile": {
            "bigram_count": relation_profile["bigram_count"],
        },
    }


def build_meta_genome_from_text(text: str, repo: WordRepository | None = None) -> dict:
    document, _, _ = compile_text(text)
    return build_meta_genome(document, repo)


def _domains_match(meta_a: dict, meta_b: dict, profile_similarity: float) -> bool:
    """Gleiche Domäne nur bei übereinstimmendem Code und ggT-Profil über Schwellwert."""
    dom_a = meta_a.get("domain") or {}
    dom_b = meta_b.get("domain") or {}
    code_a = dom_a.get("code", "general")
    code_b = dom_b.get("code", "general")
    if code_a == "general" or code_b == "general" or code_a != code_b:
        return False
    if dom_a.get("fallback") or dom_b.get("fallback"):
        return False
    return profile_similarity >= DOMAIN_SIMILARITY_THRESHOLD


def compare_meta_genomes(meta_a: dict, meta_b: dict, *, relation_comparison: dict | None = None) -> dict:
    profile_a = _profile_from_meta(meta_a)
    profile_b = _profile_from_meta(meta_b)
    cmp = compare_profiles(profile_a, profile_b)
    shared_profile = cmp["shared_profile"]
    similarity = cmp["similarity_ratio"]
    rel_score = (relation_comparison or {}).get("relation_score", 0.0)

    same_domain = _domains_match(meta_a, meta_b, similarity)
    same_domain_relational = (
        same_domain
        and rel_score >= SAME_DOMAIN_RELATIONAL_THRESHOLD
    )

    return {
        "gcd_value": cmp["gcd_value"],
        "similarity_ratio": similarity,
        "ggt_kgv_similarity": cmp.get("ggt_kgv_similarity", similarity),
        "shared_letters": cmp["shared_letters"],
        "same_domain": same_domain,
        "same_domain_relational": same_domain_relational,
        "relation_score": rel_score,
        "domain_threshold": DOMAIN_SIMILARITY_THRESHOLD,
        "heavy_shared_primes": [
            {"prime": p, "letter": CHAR_MAP.get(p, "?"), "exponent": shared_profile[p]}
            for p in sorted(shared_profile.keys(), reverse=True)[:8]
        ],
    }


def assess_parallel_signals(
    *,
    icurve_comparison: dict,
    meta_a: dict,
    meta_b: dict,
    meta_comparison: dict,
    relation_comparison: dict,
) -> dict:
    """Fusionierte Plagiats-/Parallel-Signale über alle Ebenen."""
    word_geo = icurve_comparison.get("geometry_score", 0.0)
    literal = icurve_comparison.get("literal_match_ratio", 0.0)
    meta_sim = meta_comparison.get("similarity_ratio", 0.0)
    aligned = icurve_comparison.get("aligned", False)

    cell_cmp = icurve_comparison.get("cell_geometry") or {}
    cell_score = cell_cmp.get("geometry_score", 0.0)
    subst_cmp = icurve_comparison.get("substance_geometry") or {}
    subst_score = subst_cmp.get("geometry_score", 0.0)
    rel_score = relation_comparison.get("relation_score", 0.0)

    lang_a = meta_a.get("language", {})
    lang_b = meta_b.get("language", {})
    db_a = lang_a.get("db_coverage") or {}
    db_b = lang_b.get("db_coverage") or {}
    speech_a = lang_a.get("db_speech_audit")
    speech_b = lang_b.get("db_speech_audit")
    db_speech_audit = merge_db_speech_audit(speech_a, speech_b)
    language_consistent = (
        lang_a.get("code") == lang_b.get("code")
        and lang_a.get("code") not in (None, "unknown")
    )

    word_parallel = bool(icurve_comparison.get("suspicious_parallel"))
    fester_offset = bool(icurve_comparison.get("fester_offset_erkannt"))
    elastische_streckung = bool(icurve_comparison.get("elastische_streckung"))
    hybride_modifikation = bool(icurve_comparison.get("hybride_modifikation"))
    cell_twins = bool(icurve_comparison.get("structural_cell_twins"))
    substance_parallel = bool(subst_cmp.get("substance_parallel"))
    relation_twins_flag = relation_twins(relation_comparison, literal_match_ratio=literal)
    meta_genome_strong = meta_sim >= META_PLAGIARISM_GENOME_THRESHOLD
    db_confirmed = (
        language_consistent
        and db_a.get("available")
        and db_b.get("available")
        and db_a.get("coverage_ratio", 0) >= DB_LANGUAGE_COVERAGE_THRESHOLD
        and db_b.get("coverage_ratio", 0) >= DB_LANGUAGE_COVERAGE_THRESHOLD
    )
    mixed_language_suspect = (
        db_a.get("available")
        and db_b.get("available")
        and (
            (
                db_a.get("unique_tokens", 0) >= 3
                and db_a.get("other_lang_count", 0) / db_a.get("unique_tokens", 1)
                >= MIXED_LANGUAGE_RATIO_THRESHOLD
            )
            or (
                db_b.get("unique_tokens", 0) >= 3
                and db_b.get("other_lang_count", 0) / db_b.get("unique_tokens", 1)
                >= MIXED_LANGUAGE_RATIO_THRESHOLD
            )
        )
    )

    if aligned:
        combined = (
            0.25 * word_geo
            + 0.20 * cell_score
            + 0.20 * subst_score
            + 0.15 * rel_score
            + 0.15 * meta_sim
            + 0.05 * literal
        )
    else:
        combined = (
            0.20 * word_geo
            + 0.20 * cell_score
            + 0.20 * subst_score
            + 0.20 * rel_score
            + 0.20 * meta_sim
        )

    signals: list[str] = []
    if word_parallel:
        signals.append("word_parallel")
    if fester_offset:
        signals.append("fester_offset_erkannt")
    if elastische_streckung:
        signals.append("elastische_streckung")
    if hybride_modifikation:
        signals.append("hybride_modifikation")
    if cell_twins:
        signals.append("cell_twins")
    if substance_parallel:
        signals.append("substance_parallel")
    if relation_twins_flag:
        signals.append("relation_twins")
    if meta_genome_strong:
        signals.append("meta_genome_strong")
    if meta_comparison.get("same_domain"):
        signals.append("meta_genom_gleiche_domäne")
    if meta_comparison.get("same_domain_relational"):
        signals.append("same_domain_relational")
    if db_confirmed:
        signals.append("db_language_confirmed")
    if mixed_language_suspect:
        signals.append("mixed_language_suspect")
    if combined >= COMBINED_PLAGIARISM_THRESHOLD and literal < 0.6:
        signals.append("combined_plagiarism_risk")

    bullets: list[str] = []
    if word_parallel:
        bullets.append(f"Wort-I parallel ({word_geo:.0%})")
    if fester_offset:
        bullets.append("Starre Kopie (MAE+DTW hoch)")
    if elastische_streckung:
        bullets.append("Elastische Streckung (nur DTW hoch)")
    if hybride_modifikation:
        bullets.append("Teilweise Paraphrase (DTW hoch, MAE mittel)")
    if cell_twins:
        bullets.append(f"Zell-DTW hoch ({cell_score:.0%})")
    if substance_parallel:
        bullets.append(
            f"Substanz-Kette deckt {subst_score:.0%} — {subst_cmp.get('substance_twin_count', 0)} Substanz-Zwillinge"
        )
    if relation_twins_flag:
        shared = relation_comparison.get("shared_word_bigrams") or []
        bullets.append(
            f"{len(shared)} geteilte Wort-Bigramme — Relations-Score {rel_score:.0%}"
        )
    if meta_genome_strong:
        bullets.append(f"Meta-Genom ggT {meta_sim:.0%}")
    if db_confirmed:
        bullets.append(
            f"DB bestätigt {db_a.get('coverage_ratio', 0):.0%} / {db_b.get('coverage_ratio', 0):.0%} der {lang_a.get('label', '?')}-Tokens"
        )
    if mixed_language_suspect:
        bullets.append("Mischsignal in der DB-Matrix (≥30 % — Richtwert)")
    if not bullets:
        bullets.append("Kein starkes kombiniertes Parallel-Signal")

    interpretation = " · ".join(bullets)

    return {
        "combined_score": round(combined, 6),
        "combined_threshold": COMBINED_PLAGIARISM_THRESHOLD,
        "geometry_score": word_geo,
        "cell_score": cell_score,
        "substance_score": subst_score,
        "relation_score": rel_score,
        "meta_genome_similarity": meta_sim,
        "literal_match_ratio": literal,
        "language_a": lang_a.get("label", "?"),
        "language_b": lang_b.get("label", "?"),
        "language_consistent": language_consistent,
        "domain_a": meta_a.get("domain", {}).get("label", "?"),
        "domain_b": meta_b.get("domain", {}).get("label", "?"),
        "db_coverage_a": db_a,
        "db_coverage_b": db_b,
        "db_speech_audit_a": speech_a,
        "db_speech_audit_b": speech_b,
        "db_speech_audit": db_speech_audit,
        "signals": signals,
        "interpretation": interpretation,
        "interpretation_bullets": bullets,
        "highlight": combined >= COMBINED_PLAGIARISM_THRESHOLD and literal < 0.6,
        "word_parallel": word_parallel,
        "fester_offset_erkannt": fester_offset,
        "elastische_streckung": elastische_streckung,
        "hybride_modifikation": hybride_modifikation,
        "cell_twins": cell_twins,
        "substance_parallel": substance_parallel,
        "relation_twins": relation_twins_flag,
        "meta_genome_strong": meta_genome_strong,
        "db_confirmed": db_confirmed,
        "mixed_language_suspect": mixed_language_suspect,
    }


def assess_plagiarism_meta(
    *,
    icurve_comparison: dict,
    meta_a: dict,
    meta_b: dict,
    meta_comparison: dict,
) -> dict:
    geo = icurve_comparison.get("geometry_score", 0.0)
    literal = icurve_comparison.get("literal_match_ratio", 0.0)
    meta_sim = meta_comparison.get("similarity_ratio", 0.0)
    aligned = icurve_comparison.get("aligned", False)

    lang_a = meta_a.get("language", {})
    lang_b = meta_b.get("language", {})
    language_consistent = (
        lang_a.get("code") == lang_b.get("code")
        and lang_a.get("code") not in (None, "unknown")
    )

    if aligned:
        combined = 0.45 * geo + 0.35 * meta_sim + 0.20 * literal
    else:
        combined = 0.50 * geo + 0.50 * meta_sim

    signals: list[str] = []
    if icurve_comparison.get("suspicious_parallel"):
        signals.append("i_kurve_strukturell_parallel")
    if meta_comparison.get("same_domain"):
        signals.append("meta_genom_gleiche_domäne")
    if meta_sim >= META_PLAGIARISM_GENOME_THRESHOLD:
        signals.append("meta_genom_starker_ggt")
    if geo >= 0.6 and meta_sim >= META_PLAGIARISM_GENOME_THRESHOLD:
        signals.append("geometrie_und_genom")
    if combined >= COMBINED_PLAGIARISM_THRESHOLD and literal < 0.6 and aligned:
        signals.append("plagiats_heuristik_kombiniert")

    if combined >= COMBINED_PLAGIARISM_THRESHOLD and literal < 0.5:
        interpretation = (
            "Kombiniertes Signal: ähnliche I-Kurven-Geometrie und überlappendes Meta-Genom "
            "trotz unterschiedlicher Wörter — strukturelle Parallele prüfen."
        )
    elif icurve_comparison.get("suspicious_parallel"):
        interpretation = icurve_comparison.get("interpretation", "")
    elif meta_sim >= META_PLAGIARISM_GENOME_THRESHOLD and not aligned:
        interpretation = (
            "Meta-Genom-ggT hoch — ähnliche Buchstaben-/Fachvokabular-Menge, "
            "aber unterschiedliche Token-Länge (I-Kurve nicht punktweise ausgerichtet)."
        )
    elif meta_comparison.get("same_domain") and geo >= 0.5:
        interpretation = "Gleiche Domäne und teilweise ähnliche Satzgeometrie — weiter manuell prüfen."
    elif literal >= 0.99 and geo >= 0.99:
        interpretation = "Nahezu identische Texte (Literal + I-Kurve + Meta-Genom)."
    else:
        interpretation = "Kein starkes kombiniertes Plagiats-Signal — I-Kurve und Meta-Genom weitgehend unabhängig."

    return {
        "combined_score": round(combined, 6),
        "combined_threshold": COMBINED_PLAGIARISM_THRESHOLD,
        "geometry_score": geo,
        "meta_genome_similarity": meta_sim,
        "literal_match_ratio": literal,
        "language_a": lang_a.get("label", "?"),
        "language_b": lang_b.get("label", "?"),
        "language_consistent": language_consistent,
        "domain_a": meta_a.get("domain", {}).get("label", "?"),
        "domain_b": meta_b.get("domain", {}).get("label", "?"),
        "signals": signals,
        "interpretation": interpretation,
        "highlight": combined >= COMBINED_PLAGIARISM_THRESHOLD and literal < 0.6,
    }


def enrich_pair_analysis(
    document_a: GpmDocument,
    document_b: GpmDocument,
    icurve_comparison: dict,
    repo: WordRepository | None = None,
    *,
    db_audit_mode: str = "de_en",
) -> dict:
    meta_a = build_meta_genome(document_a, repo, db_audit_mode=db_audit_mode)
    meta_b = build_meta_genome(document_b, repo, db_audit_mode=db_audit_mode)
    prof_a = build_relation_profile(document_a)
    prof_b = build_relation_profile(document_b)
    relation_comparison = compare_relation_profiles(prof_a, prof_b)
    meta_comparison = compare_meta_genomes(meta_a, meta_b, relation_comparison=relation_comparison)
    icurve_comparison["relation_twins"] = relation_twins(
        relation_comparison,
        literal_match_ratio=icurve_comparison.get("literal_match_ratio", 0.0),
    )
    plagiarism = assess_parallel_signals(
        icurve_comparison=icurve_comparison,
        meta_a=meta_a,
        meta_b=meta_b,
        meta_comparison=meta_comparison,
        relation_comparison=relation_comparison,
    )
    plagiarism["db_audit_mode"] = db_audit_mode
    return {
        "meta_a": meta_a,
        "meta_b": meta_b,
        "meta_comparison": meta_comparison,
        "relation_comparison": relation_comparison,
        "plagiarism_assessment": plagiarism,
    }
