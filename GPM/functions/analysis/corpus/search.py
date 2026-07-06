"""Anagramm-Suche im Roman-Alpha-Korpus."""

from __future__ import annotations

from pathlib import Path

from alphabets import AlphabetProfile
from alphabets.normalize import prepare_substrate
from alphabets.roman.map import uses_roman_alpha
from analysis.corpus.sqlite_roman import open_roman_alpha_corpus, roman_alpha_db_name
from gpm_types.si import encode_si


def search_anagrams_for_word(
    word: str,
    profile: AlphabetProfile | str = AlphabetProfile.OG,
    *,
    limit: int = 100,
    db_path: Path | str | None = None,
) -> dict:
    if isinstance(profile, str):
        profile = AlphabetProfile(profile)

    query = word.strip()
    if not query:
        raise ValueError("empty_word")

    normalized = prepare_substrate(query, profile)
    if not uses_roman_alpha(normalized):
        raise ValueError("not_roman_alpha")

    substance, perm_index = encode_si(query, profile)
    corpus = open_roman_alpha_corpus(db_path)

    raw_hits = corpus.find_anagrams(substance, exclude_perm=perm_index, limit=limit + 1)
    hits = [
        {
            "word_original": h.word_original or h.word_normalized,
            "word_normalized": h.word_normalized,
            "substance": h.substance,
            "perm_index": h.perm_index,
            "language": h.language or "random",
        }
        for h in raw_hits
        if h.word_normalized != normalized
    ]

    truncated = len(hits) > limit
    if truncated:
        hits = hits[:limit]

    by_language: dict[str, int] = {}
    for hit in hits:
        lang = hit["language"]
        by_language[lang] = by_language.get(lang, 0) + 1

    return {
        "query": query,
        "normalized": normalized,
        "substance": substance,
        "perm_index": perm_index,
        "hit_count": len(hits),
        "truncated": truncated,
        "hits": hits,
        "by_language": [{"language": lang, "count": count} for lang, count in sorted(by_language.items())],
        "db_name": roman_alpha_db_name(),
    }
