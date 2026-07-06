"""Size compare helpers — cache-first (Invariant I3-C)."""

from __future__ import annotations

from alphabets import AlphabetProfile
from analysis.storage.size_compare import (
    WordSnapshot,
    compare_batch_snapshots,
    compare_decode_snapshot,
    compare_word_snapshot,
)
from api.cache.document_cache import CachedCompileEntry, document_cache
from api.cache.word_compile import compile_word_cached, word_entry_from_cache
from api.schemas.common import WorkbenchError
from api.steps.pedagogy import build_decode_steps


def _snapshot_from_entry(entry: CachedCompileEntry) -> WordSnapshot:
    data = word_entry_from_cache(entry)
    return WordSnapshot(
        original=data["original"],
        normalized=data["normalized"],
        substance=data["substance"],
        perm_index=data["perm_index"],
    )


def resolve_word_entry(
    *,
    content_hash: str,
    profile: str = "og",
    fallback: dict | None = None,
) -> tuple[CachedCompileEntry, bool]:
    cached = document_cache.get(content_hash)
    if cached is not None:
        return cached, False

    if not fallback:
        raise WorkbenchError("cache_miss", "content_hash ohne Treffer.", status_code=400)

    original = str(fallback.get("original") or "").strip()
    if not original:
        raise WorkbenchError("cache_miss", "Fallback ohne original.", status_code=400)

    prof = AlphabetProfile(profile)
    entry, _hit = compile_word_cached(original, prof)
    if entry.content_hash != content_hash:
        raise WorkbenchError("cache_miss", "content_hash stimmt nicht mit Fallback überein.", status_code=400)
    return entry, True


def compare_encode_word_cached(
    *,
    content_hash: str,
    profile: str = "og",
    fallback: dict | None = None,
) -> dict:
    entry, cache_miss = resolve_word_entry(content_hash=content_hash, profile=profile, fallback=fallback)
    result = compare_word_snapshot(_snapshot_from_entry(entry)).to_dict()
    if cache_miss:
        result["cache_miss"] = True
    return result


def compare_encode_batch_cached(*, word_hashes: list[str]) -> dict:
    snapshots: list[WordSnapshot] = []
    for key in word_hashes:
        entry = document_cache.get(key)
        if entry is None:
            raise WorkbenchError(
                "cache_miss",
                f"content_hash ohne Treffer: {key[:8]}…",
                status_code=400,
            )
        snapshots.append(_snapshot_from_entry(entry))
    return compare_batch_snapshots(snapshots).to_dict()


def resolve_decode_entry(
    *,
    content_hash: str,
    profile: str = "og",
    fallback: dict | None = None,
) -> tuple[CachedCompileEntry, bool]:
    cached = document_cache.get(content_hash)
    if cached is not None:
        return cached, False

    if not fallback:
        raise WorkbenchError("cache_miss", "content_hash ohne Treffer.", status_code=400)

    try:
        substance = int(fallback.get("substance"))
        perm_index = int(fallback.get("perm_index"))
    except (TypeError, ValueError) as exc:
        raise WorkbenchError("cache_miss", "Fallback S/I ungültig.", status_code=400) from exc

    prof = AlphabetProfile(profile)
    entry_data = build_decode_steps(substance, perm_index, prof)
    if entry_data is None:
        raise WorkbenchError("cache_miss", "S/I ungültig — kein Wort rekonstruierbar.", status_code=400)

    cache_entry, _hit = compile_word_cached(entry_data["word"], prof)
    if cache_entry.content_hash != content_hash:
        raise WorkbenchError("cache_miss", "content_hash stimmt nicht mit Fallback überein.", status_code=400)
    return cache_entry, True


def compare_decode_cached(
    *,
    content_hash: str,
    profile: str = "og",
    fallback: dict | None = None,
) -> dict:
    entry, cache_miss = resolve_decode_entry(content_hash=content_hash, profile=profile, fallback=fallback)
    result = compare_decode_snapshot(_snapshot_from_entry(entry)).to_dict()
    if cache_miss:
        result["cache_miss"] = True
    return result
