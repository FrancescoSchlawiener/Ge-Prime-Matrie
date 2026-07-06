"""Word-pair cache enrichment tests."""

from __future__ import annotations

import re

import pytest
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)
HASH_RE = re.compile(r"^[a-f0-9]{64}$")


@pytest.fixture(autouse=True)
def _clear_cache():
    from api.cache.document_cache import document_cache

    document_cache._cache.clear()
    yield
    document_cache._cache.clear()


def test_word_pair_compare_returns_content_hashes():
    r = client.post(
        "/api/compare/word-pair",
        json={"a": "Listen", "b": "Silent", "profile": "og", "mode": "compare"},
    )
    assert r.status_code == 200
    result = r.json()["result"]
    assert result["normalized1"] == "LISTEN"
    assert result["normalized2"] == "SILENT"
    assert HASH_RE.match(result["content_hash1"])
    assert HASH_RE.match(result["content_hash2"])
    assert result["content_hash1"] != result["content_hash2"]


def test_word_pair_diff_returns_content_hashes():
    r = client.post(
        "/api/compare/word-pair",
        json={"a": "Listen", "b": "Silent", "profile": "og", "mode": "diff"},
    )
    assert r.status_code == 200
    result = r.json()["result"]
    assert result["classification"]["is_anagram"] is True
    assert HASH_RE.match(result["content_hash1"])
    assert HASH_RE.match(result["content_hash2"])


def test_word_pair_size_batch_after_pair():
    r = client.post(
        "/api/compare/word-pair",
        json={"a": "Listen", "b": "Silent", "profile": "og", "mode": "compare"},
    )
    result = r.json()["result"]
    hashes = [result["content_hash1"], result["content_hash2"]]
    size_r = client.post(
        "/api/size/encode-batch",
        json={"word_hashes": hashes, "profile": "og"},
    )
    assert size_r.status_code == 200
    assert size_r.json()["result"]["subject"] == "encode_batch"
