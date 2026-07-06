"""SQLite Roman-Alpha corpus tests."""

from __future__ import annotations

import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from analysis.corpus.search import search_anagrams_for_word
from analysis.corpus.sqlite_roman import SqliteRomanAlphaCorpus
from gpm_types.si import encode_si

SCHEMA = """
CREATE TABLE sources (id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE, url TEXT, fetched_at TEXT);
CREATE TABLE words (
    id INTEGER PRIMARY KEY,
    word_original TEXT NOT NULL,
    word_normalized TEXT NOT NULL,
    substance TEXT NOT NULL,
    perm_index INTEGER NOT NULL,
    language TEXT NOT NULL DEFAULT 'random',
    source_id INTEGER NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (source_id) REFERENCES sources(id)
);
CREATE INDEX idx_words_substance ON words(substance);
"""


def _seed_listen_silent(db_path: Path) -> None:
    s_listen, i_listen = encode_si("Listen", "og")
    s_silent, i_silent = encode_si("Silent", "og")
    assert s_listen == s_silent
    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(SCHEMA)
        conn.execute("INSERT INTO sources (id, name) VALUES (1, 'test')")
        conn.executemany(
            "INSERT INTO words (word_original, word_normalized, substance, perm_index, language, source_id) VALUES (?,?,?,?,?,?)",
            [
                ("Listen", "LISTEN", str(s_listen), i_listen, "en", 1),
                ("Silent", "SILENT", str(s_silent), i_silent, "en", 1),
            ],
        )
        conn.commit()
    finally:
        conn.close()


class TestSqliteRomanCorpus(unittest.TestCase):
    def test_find_anagrams_excludes_perm(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "test.db"
            _seed_listen_silent(db)
            corpus = SqliteRomanAlphaCorpus(db)
            s, i = encode_si("Listen", "og")
            hits = corpus.find_anagrams(s, exclude_perm=i)
            norms = {h.word_normalized for h in hits}
            self.assertNotIn("LISTEN", norms)
            self.assertIn("SILENT", norms)

    def test_search_anagrams_groups_by_language(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "test.db"
            s_listen, i_listen = encode_si("Listen", "og")
            s_silent, i_silent = encode_si("Silent", "og")
            conn = sqlite3.connect(db)
            try:
                conn.executescript(SCHEMA)
                conn.execute("INSERT INTO sources (id, name) VALUES (1, 'test')")
                conn.executemany(
                    "INSERT INTO words (word_original, word_normalized, substance, perm_index, language, source_id) VALUES (?,?,?,?,?,?)",
                    [
                        ("Listen", "LISTEN", str(s_listen), i_listen, "en", 1),
                        ("Silent", "SILENT", str(s_silent), i_silent, "en", 1),
                        ("Enlist", "ENLIST", str(s_silent), i_silent + 1, "de", 1),
                    ],
                )
                conn.commit()
            finally:
                conn.close()
            result = search_anagrams_for_word("Listen", "og", db_path=db, limit=50)
            langs = {row["language"] for row in result["hits"]}
            self.assertEqual(langs, {"de", "en"})
            self.assertEqual(len(result["by_language"]), 2)

    def test_search_anagrams_for_word(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "test.db"
            _seed_listen_silent(db)
            result = search_anagrams_for_word("Listen", "og", db_path=db)
            self.assertEqual(result["normalized"], "LISTEN")
            self.assertGreaterEqual(result["hit_count"], 1)
            norms = {h["word_normalized"] for h in result["hits"]}
            self.assertIn("SILENT", norms)
            self.assertNotIn("LISTEN", norms)
            self.assertEqual(result["hits"][0]["language"], "en")
            self.assertTrue(result["by_language"])


if __name__ == "__main__":
    unittest.main()
