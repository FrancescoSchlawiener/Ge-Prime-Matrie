"""Size compare API contract tests."""

from __future__ import annotations

import re

import pytest
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)

GERMAN_UI_PATTERN = re.compile(
    r"(Klartext|Dokumente|vorteilhaft|Speicher|Markdown|Textdatei|schlägt)",
    re.IGNORECASE,
)


@pytest.fixture(autouse=True)
def _clear_cache():
    from api.cache.document_cache import document_cache

    document_cache._cache.clear()
    yield
    document_cache._cache.clear()


def _encode_batch(text: str) -> dict:
    r = client.post(
        "/api/calc/encode-batch",
        json={"text": text, "profile": "og", "include_steps": False},
    )
    assert r.status_code == 200
    return r.json()["result"]


def test_encode_batch_returns_content_hash():
    result = _encode_batch("HALLO WELT")
    words = result["words"]
    assert len(words) == 2
    for w in words:
        assert len(w.get("content_hash", "")) == 64


def test_size_encode_word_cache_hit():
    batch = _encode_batch("HALLO")
    word = batch["words"][0]
    r = client.post(
        "/api/size/encode-word",
        json={"content_hash": word["content_hash"], "profile": "og"},
    )
    assert r.status_code == 200
    data = r.json()["result"]
    assert data["subject"] == "encode_word"
    assert data["insight"]["verdict"] in ("win", "tie", "learn")
    assert "rows" in data and len(data["rows"]) > 0
    assert not GERMAN_UI_PATTERN.search(str(data))


def test_size_encode_word_cache_miss_without_fallback():
    batch = _encode_batch("HALLO")
    from api.cache.document_cache import document_cache

    document_cache._cache.clear()
    r = client.post(
        "/api/size/encode-word",
        json={"content_hash": batch["words"][0]["content_hash"], "profile": "og"},
    )
    assert r.status_code == 400


def test_size_encode_batch_word_hashes_only():
    batch = _encode_batch("hallo welt")
    hashes = [w["content_hash"] for w in batch["words"]]
    r = client.post(
        "/api/size/encode-batch",
        json={"word_hashes": hashes, "profile": "og"},
    )
    assert r.status_code == 200
    data = r.json()["result"]
    assert data["subject"] == "encode_batch"
    assert data["insight"]["verdict"] in ("win", "tie", "learn")
    row_ids = {row["id"] for row in data["rows"]}
    assert "batch_joined_utf8" in row_ids
    assert "batch_sum_binary_si" in row_ids
    assert not GERMAN_UI_PATTERN.search(str(data))


def test_size_batch_cache_miss():
    r = client.post(
        "/api/size/encode-batch",
        json={"word_hashes": ["a" * 64], "profile": "og"},
    )
    assert r.status_code == 400


def _decode_word(substance: int, perm_index: int) -> dict:
    r = client.post(
        "/api/calc/decode-word",
        json={"substance": substance, "index": perm_index, "profile": "og", "include_steps": False},
    )
    assert r.status_code == 200
    return r.json()["result"]


def test_decode_word_returns_content_hash():
    result = _decode_word(372945, 13)
    assert result["word"] == "HALLO"
    assert len(result.get("content_hash", "")) == 64


def test_size_decode_cache_hit():
    decoded = _decode_word(372945, 13)
    r = client.post(
        "/api/size/decode",
        json={"content_hash": decoded["content_hash"], "profile": "og"},
    )
    assert r.status_code == 200
    data = r.json()["result"]
    assert data["subject"] == "decode_word"
    assert data["calculation"][0]["step_id"] == "reconstruction"
    assert not GERMAN_UI_PATTERN.search(str(data))


def test_size_decode_cache_miss_without_fallback():
    decoded = _decode_word(372945, 13)
    from api.cache.document_cache import document_cache

    document_cache._cache.clear()
    r = client.post(
        "/api/size/decode",
        json={"content_hash": decoded["content_hash"], "profile": "og"},
    )
    assert r.status_code == 400
