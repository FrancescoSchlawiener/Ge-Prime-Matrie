"""Einzelwort-Compile mit CAS-LRU (Invariante I3-C)."""

from __future__ import annotations

from alphabets import AlphabetProfile
from analysis.compile.compiler import compile_text
from analysis.inference.trace import InferenceTrace
from api.cache.document_cache import CachedCompileEntry, document_cache, word_hash_key


def compile_word_cached(original: str, profile: AlphabetProfile | str) -> tuple[CachedCompileEntry, bool]:
    if isinstance(profile, str):
        profile = AlphabetProfile(profile)

    key = word_hash_key(profile.value, original)

    def _build() -> CachedCompileEntry:
        doc, stats = compile_text(original, profile)
        trace = InferenceTrace(compile_stats=stats, normalized=doc.header[0].word_normalized if doc.header else "")
        return CachedCompileEntry(
            content_hash=key,
            mode="word",
            profile=profile,
            document=doc,
            source_text=original,
            stats=stats,
            trace=trace,
        )

    return document_cache.get_or_compile(key, _build)


def word_entry_from_cache(entry: CachedCompileEntry) -> dict:
    if not entry.document.header or not entry.document.tokens:
        raise ValueError("Cache-Eintrag ohne Wortdaten.")

    header = entry.document.header[0]
    token = entry.document.tokens[0]
    return {
        "original": entry.source_text,
        "normalized": header.word_normalized,
        "substance": header.substance,
        "perm_index": token.perm_index,
        "index": token.perm_index,
        "content_hash": entry.content_hash,
    }


def register_word_pair_cached(
    a: str, b: str, profile: AlphabetProfile | str
) -> tuple[dict, dict]:
    entry_a, _ = compile_word_cached(a, profile)
    entry_b, _ = compile_word_cached(b, profile)
    return word_entry_from_cache(entry_a), word_entry_from_cache(entry_b)
