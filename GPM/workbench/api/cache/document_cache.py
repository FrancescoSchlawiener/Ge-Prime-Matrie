"""Content-Addressable Compile-Cache (SHA-256 LRU + Single-Flight)."""

from __future__ import annotations

import hashlib
import json
import threading
from dataclasses import dataclass
from typing import Any, Callable

from cachetools import LRUCache

from alphabets import AlphabetProfile
from analysis.document.model import CompileStats, GpmDocument
from analysis.inference.trace import InferenceTrace
from api.cache.warmup import warmup_document


@dataclass
class CachedCompileEntry:
    content_hash: str
    mode: str
    profile: AlphabetProfile
    document: GpmDocument
    source_text: str
    hybrid: Any | None = None
    stats: CompileStats | None = None
    trace: InferenceTrace | None = None
    language_id: str | None = None


def word_hash_key(profile: str, original: str) -> str:
    return content_hash_key("word", profile, original, None)


def content_hash_key(
    mode: str,
    profile: str,
    text: str,
    language_id: str | None = None,
) -> str:
    payload = json.dumps(
        {"mode": mode, "profile": profile, "text": text, "language_id": language_id},
        sort_keys=True,
        ensure_ascii=False,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class DocumentCompileCache:
    def __init__(self, maxsize: int = 128) -> None:
        self._cache: LRUCache[str, CachedCompileEntry] = LRUCache(maxsize=maxsize)
        self._lock = threading.RLock()
        self._inflight: dict[str, threading.Event] = {}
        self._inflight_result: dict[str, CachedCompileEntry | Exception] = {}

    def get(self, key: str) -> CachedCompileEntry | None:
        with self._lock:
            return self._cache.get(key)

    def get_or_compile(
        self,
        key: str,
        compile_fn: Callable[[], CachedCompileEntry],
    ) -> tuple[CachedCompileEntry, bool]:
        with self._lock:
            hit = self._cache.get(key)
            if hit is not None:
                return hit, True
            if key in self._inflight:
                event = self._inflight[key]
                owner = False
            else:
                event = threading.Event()
                self._inflight[key] = event
                owner = True

        if not owner:
            event.wait()
            with self._lock:
                result = self._inflight_result.get(key)
                if isinstance(result, Exception):
                    raise result
                if result is None:
                    raise RuntimeError("Single-flight compile ohne Ergebnis.")
                cached = self._cache.get(key)
                if cached is not None:
                    return cached, True
                return result, True

        try:
            entry = compile_fn()
            warmup_document(entry.document)
            with self._lock:
                self._cache[key] = entry
                self._inflight_result[key] = entry
            return entry, False
        except Exception as exc:
            with self._lock:
                self._inflight_result[key] = exc
            raise
        finally:
            with self._lock:
                ev = self._inflight.pop(key, None)
                if ev is not None:
                    ev.set()
                self._inflight_result.pop(key, None)


document_cache = DocumentCompileCache()
