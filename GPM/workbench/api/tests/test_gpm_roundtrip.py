"""GPM compile → write → read roundtrip."""

from __future__ import annotations

import base64
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
FUNCTIONS = ROOT.parent / "functions"
sys.path.insert(0, str(FUNCTIONS))
sys.path.insert(0, str(ROOT))

from api.main import app  # noqa: E402

client = TestClient(app)


@pytest.fixture(autouse=True)
def _clear_cache():
    from api.cache.document_cache import document_cache

    document_cache._cache.clear()
    yield
    document_cache._cache.clear()


def test_gpm_compile_write_read_roundtrip():
    source = "Hallo Welt"
    compile_resp = client.post(
        "/api/editor/compile",
        json={"mode": "nl", "text": source, "profile": "og"},
    )
    assert compile_resp.status_code == 200
    compile_body = compile_resp.json()
    document_ref = compile_body["result"]["document_ref"]
    assert document_ref

    write_resp = client.post(
        "/api/editor/gpm/write",
        json={"document_ref": document_ref, "profile": "og"},
    )
    assert write_resp.status_code == 200
    write_body = write_resp.json()
    b64 = write_body["result"]["base64"]
    assert b64
    raw = base64.b64decode(b64)
    assert raw[:3] == b"GPM"
    assert len(raw) >= 12

    read_resp = client.post(
        "/api/editor/gpm/read",
        json={"base64": b64},
    )
    assert read_resp.status_code == 200
    read_body = read_resp.json()
    result = read_body["result"]
    assert result.get("document_ref")
    assert result.get("reconstructed_text") == source
    assert result.get("token_count", 0) >= 1
