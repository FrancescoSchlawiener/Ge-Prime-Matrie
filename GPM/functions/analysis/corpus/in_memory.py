"""In-Memory-Anagramm-Korpus für Tests und manuelle Seeds."""

from __future__ import annotations

from analysis.corpus.protocol import AnagramCorpus, CorpusEntry


class InMemoryCorpus:
    def __init__(self, entries: list[CorpusEntry] | None = None) -> None:
        self._entries = list(entries or [])

    def add(self, entry: CorpusEntry) -> None:
        self._entries.append(entry)

    def find_by_substance(self, substance: int) -> list[CorpusEntry]:
        return [e for e in self._entries if e.substance == substance]

    def find_anagrams(
        self,
        substance: int,
        *,
        exclude_perm: int | None = None,
    ) -> list[CorpusEntry]:
        hits = [e for e in self._entries if e.substance == substance]
        if exclude_perm is not None:
            hits = [e for e in hits if e.perm_index != exclude_perm]
        return hits

    def find_by_normalized(self, normalized: str) -> list[CorpusEntry]:
        key = normalized.upper()
        return [e for e in self._entries if e.word_normalized == key]


def corpus_from_dicts(rows: list[dict]) -> InMemoryCorpus:
    entries = [
        CorpusEntry(
            substance=int(row["substance"]),
            perm_index=int(row["perm_index"]),
            word_normalized=str(row["word_normalized"]).upper(),
            word_original=row.get("word_original"),
        )
        for row in rows
    ]
    return InMemoryCorpus(entries)
