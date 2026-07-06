"""Anagram search API tests."""

from __future__ import annotations

import re
import sqlite3
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from api.main import app
from gpm_types.si import encode_si

client = TestClient(app)
HASH_RE = re.compile(r"^[a-f0-9]{64}$")

SCHEMA = """
CREATE TABLE sources (id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE);
CREATE TABLE words (
    id INTEGER PRIMARY KEY,
    word_original TEXT NOT NULL,
    word_normalized TEXT NOT NULL,
    substance TEXT NOT NULL,
    perm_index INTEGER NOT NULL,
    language TEXT NOT NULL DEFAULT 'en',
    source_id INTEGER NOT NULL
);
CREATE INDEX idx_words_substance ON words(substance);
"""


@pytest.fixture(autouse=True)
def _clear_cache():
    from api.cache.document_cache import document_cache

    document_cache._cache.clear()
    yield
    document_cache._cache.clear()


def _make_fixture_db(tmp: Path) -> Path:
    db = tmp / "roman.db"
    s_listen, i_listen = encode_si("Listen", "og")
    s_silent, i_silent = encode_si("Silent", "og")
    conn = sqlite3.connect(db)
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
    conn.close()
    return db


def test_anagram_search_hits(monkeypatch):
    from analysis.corpus.sqlite_roman import SqliteRomanAlphaCorpus

    with tempfile.TemporaryDirectory() as tmp_dir:
        db = _make_fixture_db(Path(tmp_dir))

        def _open(db_path=None):
            return SqliteRomanAlphaCorpus(db)

        monkeypatch.setattr("analysis.corpus.search.open_roman_alpha_corpus", _open)

        r = client.post(
            "/api/compare/anagram-search",
            json={"word": "Listen", "profile": "og", "limit": 50},
        )
        assert r.status_code == 200
        result = r.json()["result"]
        assert result["normalized"] == "LISTEN"
        assert HASH_RE.match(result["content_hash"])
        norms = {h["word_normalized"] for h in result["hits"]}
        assert "SILENT" in norms
        assert result["hits"][0]["language"] == "en"
        assert result["by_language"] == [{"language": "en", "count": 1}]


def test_anagram_search_not_roman_alpha():
    r = client.post(
        "/api/compare/anagram-search",
        json={"word": "ΩMEGA", "profile": "og"},
    )
    assert r.status_code == 400
    body = r.json()
    assert body["error"]["message"] == "not_roman_alpha"
