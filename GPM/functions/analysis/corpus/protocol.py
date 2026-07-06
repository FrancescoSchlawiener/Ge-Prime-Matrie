"""Anagramm-Korpus-Protokoll — schlanker Stub ohne SQLite."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable


@dataclass(frozen=True)
class CorpusEntry:
    substance: int
    perm_index: int
    word_normalized: str
    word_original: str | None = None
    language: str = ""


@runtime_checkable
class AnagramCorpus(Protocol):
    def find_by_substance(self, substance: int) -> list[CorpusEntry]: ...

    def find_anagrams(
        self,
        substance: int,
        *,
        exclude_perm: int | None = None,
    ) -> list[CorpusEntry]: ...

    def find_by_normalized(self, normalized: str) -> list[CorpusEntry]: ...
