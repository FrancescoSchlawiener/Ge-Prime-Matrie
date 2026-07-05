import hashlib
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.copy_roman_alpha_db import copy_and_filter_roman_alpha_db

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
"""


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        h.update(f.read())
    return h.hexdigest()


class TestCopyRomanAlphaDb(unittest.TestCase):
    def test_filter_vacuum_integrity(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            source = tmp_path / "source.db"
            dest = tmp_path / "dest.db"

            conn = sqlite3.connect(source)
            conn.executescript(SCHEMA)
            conn.execute("INSERT INTO sources (id, name) VALUES (1, 'test')")
            conn.executemany(
                "INSERT INTO words (word_original, word_normalized, substance, perm_index, language, source_id) VALUES (?,?,?,?,?,?)",
                [
                    ("Hallo", "HALLO", "1", 1, "de", 1),
                    ("Omega", "ΩMEGA", "2", 1, "el", 1),
                ],
            )
            conn.commit()
            conn.close()
            hash_before = _sha256(source)
            size_before_copy = source.stat().st_size

            result = copy_and_filter_roman_alpha_db(source=source, dest=dest)

            self.assertEqual(result["deleted_words"], 1)
            self.assertEqual(result["remaining_words"], 1)
            self.assertEqual(result["integrity_check"], "ok")
            self.assertTrue(result["source_unchanged"])
            self.assertEqual(_sha256(source), hash_before)

            dconn = sqlite3.connect(dest)
            try:
                count = dconn.execute("SELECT COUNT(*) FROM words").fetchone()[0]
                self.assertEqual(count, 1)
                norm = dconn.execute("SELECT word_normalized FROM words").fetchone()[0]
                self.assertEqual(norm, "HALLO")
            finally:
                dconn.close()


if __name__ == "__main__":
    unittest.main()
