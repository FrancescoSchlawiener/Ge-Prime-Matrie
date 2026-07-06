"""CAS document compile cache contract tests."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
FUNCTIONS = ROOT.parent / "functions"
sys.path.insert(0, str(FUNCTIONS))
sys.path.insert(0, str(ROOT))

from api.cache.document_cache import document_cache  # noqa: E402
from api.main import app  # noqa: E402

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_cache():
    document_cache._cache.clear()
    yield
    document_cache._cache.clear()


def test_compile_cache_hit():
    payload = {"mode": "nl", "text": "Hello cache", "profile": "og"}
    calls = {"n": 0}
    original = None

    from analysis.compile import compiler

    original = compiler.compile_text

    def counted_compile(text, profile):
        calls["n"] += 1
        return original(text, profile)

    with patch.object(compiler, "compile_text", side_effect=counted_compile):
        r1 = client.post("/api/editor/compile", json=payload)
        r2 = client.post("/api/editor/compile", json=payload)
    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r1.json()["result"]["cache_hit"] is False
    assert r2.json()["result"]["cache_hit"] is True
    assert calls["n"] == 1


def test_compile_single_flight_cas_cache_invariant():
    """Explicit content_key must not trigger a second compile_text call."""
    from api.cache.document_cache import content_hash_key

    text = "SYSTEM NATIVE DETERMINISM"
    key = content_hash_key("nl", "og", text, None)
    payload = {"mode": "nl", "text": text, "profile": "og", "content_key": key}
    calls = {"n": 0}

    from analysis.compile import compiler

    original = compiler.compile_text

    def counted_compile(t, profile):
        calls["n"] += 1
        return original(t, profile)

    with patch.object(compiler, "compile_text", side_effect=counted_compile):
        r1 = client.post("/api/editor/compile", json=payload)
        r2 = client.post("/api/editor/compile", json=payload)
    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r1.json()["result"]["cache_hit"] is False
    assert r2.json()["result"]["cache_hit"] is True
    assert r1.json()["result"]["document_ref"] == r2.json()["result"]["document_ref"]
    assert calls["n"] == 1


def test_spectroscope_uses_session_not_recompile():
    payload = {"mode": "nl", "text": "Scan me", "profile": "og"}
    r = client.post("/api/editor/compile", json=payload)
    ref = r.json()["result"]["document_ref"]
    r2 = client.post(
        "/api/editor/spectroscope",
        json={"document_ref": ref, "token_start": 0, "token_end": 1},
    )
    assert r2.status_code == 200
