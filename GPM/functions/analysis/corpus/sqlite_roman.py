"""SQLite-Anagramm-Korpus — ge_prime_roman_alpha_alt.db (read-only)."""

from __future__ import annotations

import sqlite3
import threading
from contextlib import contextmanager
from pathlib import Path

from analysis.corpus.protocol import CorpusEntry
from db.paths import GPM_ROMAN_ALPHA_DB

_DB_NAME = "ge_prime_roman_alpha_alt.db"


class SqliteRomanAlphaCorpus:
    def __init__(self, db_path: Path | str | None = None) -> None:
        self.db_path = Path(db_path) if db_path is not None else GPM_ROMAN_ALPHA_DB
        self._lock = threading.RLock()

    @contextmanager
    def _connection(self):
        with self._lock:
            conn = sqlite3.connect(f"file:{self.db_path}?mode=ro", uri=True)
            conn.row_factory = sqlite3.Row
            try:
                yield conn
            finally:
                conn.close()

    def _row_to_entry(self, row: sqlite3.Row) -> CorpusEntry:
        return CorpusEntry(
            substance=int(row["substance"]),
            perm_index=int(row["perm_index"]),
            word_normalized=str(row["word_normalized"]).upper(),
            word_original=row["word_original"],
            language=str(row["language"] or ""),
        )

    _SELECT_COLS = "word_original, word_normalized, substance, perm_index, language"

    def find_by_substance(self, substance: int) -> list[CorpusEntry]:
        with self._connection() as conn:
            rows = conn.execute(
                f"""
                SELECT {self._SELECT_COLS}
                FROM words
                WHERE substance = ?
                ORDER BY language, word_normalized
                """,
                (str(substance),),
            ).fetchall()
        return [self._row_to_entry(r) for r in rows]

    def find_by_normalized(self, normalized: str) -> list[CorpusEntry]:
        key = normalized.upper()
        with self._connection() as conn:
            rows = conn.execute(
                f"""
                SELECT {self._SELECT_COLS}
                FROM words
                WHERE word_normalized = ?
                ORDER BY word_original
                """,
                (key,),
            ).fetchall()
        return [self._row_to_entry(r) for r in rows]

    def find_anagrams(
        self,
        substance: int,
        *,
        exclude_perm: int | None = None,
        limit: int = 100,
    ) -> list[CorpusEntry]:
        if exclude_perm is None:
            with self._connection() as conn:
                rows = conn.execute(
                    f"""
                    SELECT {self._SELECT_COLS}
                    FROM words
                    WHERE substance = ?
                    ORDER BY language, word_normalized
                    LIMIT ?
                    """,
                    (str(substance), limit + 1),
                ).fetchall()
        else:
            with self._connection() as conn:
                rows = conn.execute(
                    f"""
                    SELECT {self._SELECT_COLS}
                    FROM words
                    WHERE substance = ? AND perm_index != ?
                    ORDER BY language, word_normalized
                    LIMIT ?
                    """,
                    (str(substance), exclude_perm, limit + 1),
                ).fetchall()
        return [self._row_to_entry(r) for r in rows]

    def count_words(self) -> int:
        with self._connection() as conn:
            row = conn.execute("SELECT COUNT(*) AS c FROM words").fetchone()
        return int(row["c"])

    def count_by_language(self) -> list[tuple[str, int]]:
        with self._connection() as conn:
            rows = conn.execute(
                """
                SELECT language, COUNT(*) AS c
                FROM words
                GROUP BY language
                ORDER BY c DESC
                """
            ).fetchall()
        return [(str(r["language"]), int(r["c"])) for r in rows]


def open_roman_alpha_corpus(db_path: Path | str | None = None) -> SqliteRomanAlphaCorpus:
    path = Path(db_path) if db_path is not None else GPM_ROMAN_ALPHA_DB
    if not path.is_file():
        raise FileNotFoundError(str(path))
    return SqliteRomanAlphaCorpus(path)


def roman_alpha_db_name() -> str:
    return _DB_NAME
