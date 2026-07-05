"""Primzahl-Profile für Sprache und Domäne — Overlap, Seeds, DB."""

from __future__ import annotations

from collections import Counter
from functools import lru_cache
from typing import TYPE_CHECKING

from ge_prime.core import PRIME_MAP
from ge_prime.decode import get_ingredients
from ge_prime.encode import encode_word
from ge_prime.linguistics.registry import MIN_DB_WORDS_PER_LANGUAGE, LanguageSpec, iter_languages
from gpm.compiler import compile_text
from gpm.model import GpmDocument

if TYPE_CHECKING:
    from db.repository import WordRepository


def word_frequencies(document: GpmDocument) -> Counter:
    counts: Counter = Counter()
    for token in document.tokens:
        counts[token.word_id] += 1
    return counts


def ingredients_to_profile(ingredients: Counter, *, multiplier: int = 1) -> Counter:
    profile: Counter = Counter()
    for char, count in ingredients.items():
        prime = PRIME_MAP.get(char)
        if prime:
            profile[prime] += count * multiplier
    return profile


def build_prime_profile(document: GpmDocument) -> Counter:
    freqs = word_frequencies(document)
    profile: Counter = Counter()
    for word_id, count in freqs.items():
        entry = document.header[word_id]
        ingredients = get_ingredients(entry.substance)
        profile.update(ingredients_to_profile(ingredients, multiplier=count))
    return profile


def profile_overlap(a: Counter, b: Counter) -> float:
    keys = set(a) | set(b)
    inter = sum(min(a.get(k, 0), b.get(k, 0)) for k in keys)
    denom = min(sum(a.values()), sum(b.values()))
    return inter / denom if denom else 0.0


def normalized_token_counts(document: GpmDocument) -> Counter:
    """Häufigkeiten normalisierter Wörter im Dokument."""
    counts: Counter = Counter()
    for token in document.tokens:
        entry = document.header[token.word_id]
        counts[entry.word_normalized] += 1
    return counts


@lru_cache(maxsize=32)
def seed_profile_from_text(seed_text: str) -> Counter:
    if not seed_text or not seed_text.strip():
        return Counter()
    doc, _, _ = compile_text(seed_text)
    return build_prime_profile(doc)


_lang_ref_cache: dict[tuple[str, str], tuple[Counter, str]] = {}
_lang_count_cache: dict[str, dict[str, int]] = {}
_db_tier_available: dict[str, bool] = {}


def clear_profile_caches() -> None:
    """Test-Hilfe: Referenzprofile zurücksetzen."""
    _lang_ref_cache.clear()
    _lang_count_cache.clear()
    _db_tier_available.clear()
    seed_profile_from_text.cache_clear()


def _repo_profile_key(repo: WordRepository) -> str:
    return str(getattr(repo, "db_path", id(repo)))


def invalidate_repo_profile_cache(repo: WordRepository) -> None:
    """Nach DB-Import: DB-Tier-Entscheidung neu bewerten."""
    key = _repo_profile_key(repo)
    _db_tier_available.pop(key, None)
    _lang_count_cache.pop(key, None)
    prefix = key + ":"
    for cache_key in list(_lang_ref_cache):
        if cache_key[0] == key:
            _lang_ref_cache.pop(cache_key, None)


def db_tier_available(repo: WordRepository) -> bool:
    """True nur wenn die DB genug Wörter pro Sprache für Referenzprofile hat."""
    key = _repo_profile_key(repo)
    cached = _db_tier_available.get(key)
    if cached is not None:
        return cached
    total_count_fn = getattr(repo, "total_count", None)
    if total_count_fn is None:
        _db_tier_available[key] = False
        _lang_count_cache[key] = {}
        return False
    if total_count_fn() == 0:
        _db_tier_available[key] = False
        _lang_count_cache[key] = {}
        return False
    counts = repo.count_words_by_language(exclude_random=True)
    _lang_count_cache[key] = counts
    ready = any(n >= MIN_DB_WORDS_PER_LANGUAGE for n in counts.values())
    _db_tier_available[key] = ready
    return ready


def resolve_linguistics_repo(repo: WordRepository | None) -> WordRepository | None:
    """Leere oder zu kleine DB → None (nur Funktionswort-Muster, keine DB-Abfragen)."""
    if repo is None:
        return None
    return repo if db_tier_available(repo) else None


def _cached_language_counts(repo: WordRepository) -> dict[str, int]:
    key = _repo_profile_key(repo)
    if key not in _lang_count_cache:
        if not db_tier_available(repo):
            return {}
        _lang_count_cache[key] = repo.count_words_by_language(exclude_random=True)
    return _lang_count_cache[key]


def build_profile_from_word_list(words: list[str]) -> Counter:
    profile: Counter = Counter()
    for word in words:
        if not word:
            continue
        substance, _ = encode_word(word)
        profile.update(ingredients_to_profile(get_ingredients(substance)))
    return profile


def language_reference_profile(spec: LanguageSpec, repo: WordRepository | None) -> tuple[Counter, str]:
    """Referenzprofil für eine Sprache: DB wenn genug Wörter, sonst Seed (gecacht)."""
    cache_key = (_repo_profile_key(repo) if repo is not None else "", spec.code)
    cached = _lang_ref_cache.get(cache_key)
    if cached is not None:
        return cached

    if repo is not None and db_tier_available(repo):
        counts = _cached_language_counts(repo)
        if counts.get(spec.code, 0) >= MIN_DB_WORDS_PER_LANGUAGE:
            words = repo.sample_normalized_words(spec.code, limit=80)
            if words:
                result = (build_profile_from_word_list(words), "db")
                _lang_ref_cache[cache_key] = result
                return result

    result = (seed_profile_from_text(spec.profile_seed), "patterns")
    _lang_ref_cache[cache_key] = result
    return result


def domain_seed_profile(seed_text: str) -> Counter:
    return seed_profile_from_text(seed_text)


def db_has_language(repo: WordRepository | None, lang_code: str) -> bool:
    if repo is None:
        return False
    counts = _cached_language_counts(repo)
    return counts.get(lang_code, 0) >= MIN_DB_WORDS_PER_LANGUAGE


def language_detection_method(repo: WordRepository | None) -> str:
    if repo is None or not db_tier_available(repo):
        return "patterns"
    return "hybrid"
