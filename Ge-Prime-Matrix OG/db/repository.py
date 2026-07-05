import sqlite3
import threading
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

from db.paths import default_db_path
from db.schema import SCHEMA_SQL
from db.models import StoredWord, row_to_stored_word
from pipeline.process import ProcessResult

DEFAULT_DB_PATH = default_db_path()


@dataclass
class InsertStats:
    inserted: int = 0
    duplicates: int = 0


class WordRepository:
    def __init__(self, db_path: Path | str | None = None):
        if db_path is None:
            self.db_path = default_db_path()
        else:
            self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()

    @contextmanager
    def _connection(self):
        with self._lock:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON")
            conn.execute("PRAGMA busy_timeout = 30000")
            try:
                yield conn
                conn.commit()
            finally:
                conn.close()

    def init_db(self) -> None:
        with self._connection() as conn:
            conn.executescript(SCHEMA_SQL)

    def delete_database(self) -> None:
        """Datenbankdatei löschen (Neustart)."""
        self.close()
        if self.db_path.exists():
            self.db_path.unlink()

    def close(self) -> None:
        pass

    def get_or_create_source(self, name: str, url: str | None = None) -> int:
        with self._connection() as conn:
            row = conn.execute(
                "SELECT id FROM sources WHERE name = ?", (name,)
            ).fetchone()
            if row:
                conn.execute(
                    "UPDATE sources SET url = COALESCE(?, url), fetched_at = datetime('now') WHERE id = ?",
                    (url, row["id"]),
                )
                return row["id"]

            cur = conn.execute(
                "INSERT INTO sources (name, url, fetched_at) VALUES (?, ?, datetime('now'))",
                (name, url),
            )
            return cur.lastrowid

    def insert_words_batch(
        self,
        words: list[ProcessResult],
        source_id: int,
        *,
        batch_size: int = 1000,
    ) -> InsertStats:
        stats = InsertStats()
        with self._connection() as conn:
            for i in range(0, len(words), batch_size):
                chunk = words[i : i + batch_size]
                for w in chunk:
                    try:
                        conn.execute(
                            """
                            INSERT INTO words
                                (word_original, word_normalized, substance, perm_index, language, source_id)
                            VALUES (?, ?, ?, ?, ?, ?)
                            """,
                            (
                                w.word_original,
                                w.word_normalized,
                                str(w.substance),
                                w.perm_index,
                                w.language,
                                source_id,
                            ),
                        )
                        stats.inserted += 1
                    except sqlite3.IntegrityError:
                        stats.duplicates += 1
        if stats.inserted:
            try:
                from ge_prime.linguistics.profiles import invalidate_repo_profile_cache

                invalidate_repo_profile_cache(self)
            except ImportError:
                pass
        return stats

    def count_by_language(self) -> list[tuple[str | None, int]]:
        with self._connection() as conn:
            rows = conn.execute(
                """
                SELECT language, COUNT(*) AS cnt
                FROM words
                GROUP BY language
                ORDER BY cnt DESC
                """
            ).fetchall()
        return [(row["language"], row["cnt"]) for row in rows]

    def count_words_by_language(self, *, exclude_random: bool = True) -> dict[str, int]:
        counts: dict[str, int] = {}
        for lang, cnt in self.count_by_language():
            code = (lang or "random").strip().lower()
            if exclude_random and code == "random":
                continue
            counts[code] = counts.get(code, 0) + cnt
        return counts

    def sample_normalized_words(self, language: str, *, limit: int = 500) -> list[str]:
        lang = (language or "").strip().lower()
        if not lang:
            return []
        with self._connection() as conn:
            rows = conn.execute(
                """
                SELECT DISTINCT word_normalized
                FROM words
                WHERE language = ?
                ORDER BY id
                LIMIT ?
                """,
                (lang, limit),
            ).fetchall()
        return [row["word_normalized"] for row in rows if row["word_normalized"]]

    def total_count(self) -> int:
        with self._connection() as conn:
            row = conn.execute("SELECT COUNT(*) AS cnt FROM words").fetchone()
        return row["cnt"]

    def find_by_normalized(self, normalized: str, language: str | None = None) -> list[sqlite3.Row]:
        with self._connection() as conn:
            if language is None:
                return conn.execute(
                    "SELECT * FROM words WHERE word_normalized = ?",
                    (normalized,),
                ).fetchall()
            return conn.execute(
                "SELECT * FROM words WHERE word_normalized = ? AND language = ?",
                (normalized, language),
            ).fetchall()

    def lookup_languages_bulk(self, normalized_words: list[str]) -> dict[str, dict[str, int]]:
        """Pro normalisiertem Wort: {sprache: trefferzahl} in einem oder wenigen Queries."""
        unique = [w for w in dict.fromkeys(normalized_words) if w]
        if not unique:
            return {}

        result: dict[str, dict[str, int]] = {}
        chunk_size = 900
        with self._connection() as conn:
            for start in range(0, len(unique), chunk_size):
                chunk = unique[start : start + chunk_size]
                placeholders = ",".join("?" * len(chunk))
                rows = conn.execute(
                    f"""
                    SELECT word_normalized, language, COUNT(*) AS cnt
                    FROM words
                    WHERE word_normalized IN ({placeholders})
                    GROUP BY word_normalized, language
                    """,
                    chunk,
                ).fetchall()
                for row in rows:
                    norm = row["word_normalized"]
                    lang = (row["language"] or "unknown").strip().lower()
                    result.setdefault(norm, {})[lang] = int(row["cnt"])
        return result

    def get_by_original(self, word_original: str) -> StoredWord | None:
        with self._connection() as conn:
            row = conn.execute(
                "SELECT * FROM words WHERE word_original = ? ORDER BY id DESC LIMIT 1",
                (word_original,),
            ).fetchone()
        if row is None:
            return None
        return row_to_stored_word(row)

    def get_by_id(self, word_id: int) -> StoredWord | None:
        with self._connection() as conn:
            row = conn.execute(
                "SELECT * FROM words WHERE id = ?",
                (word_id,),
            ).fetchone()
        if row is None:
            return None
        return row_to_stored_word(row)
