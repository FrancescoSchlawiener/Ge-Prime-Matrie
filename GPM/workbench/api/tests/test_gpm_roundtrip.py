"""GPM compile → write → read roundtrip (JSON + multipart)."""

from __future__ import annotations

import base64
import io
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


def _compile_write(source: str) -> tuple[str, bytes, str]:
    compile_resp = client.post(
        "/api/editor/compile",
        json={"mode": "nl", "text": source, "profile": "og"},
    )
    assert compile_resp.status_code == 200
    document_ref = compile_resp.json()["result"]["document_ref"]
    assert document_ref

    write_resp = client.post(
        "/api/editor/gpm/write",
        json={"document_ref": document_ref, "profile": "og"},
    )
    assert write_resp.status_code == 200
    b64 = write_resp.json()["result"]["base64"]
    assert b64
    raw = base64.b64decode(b64)
    assert raw[:3] == b"GPM"
    assert len(raw) >= 12
    return document_ref, raw, b64


def test_gpm_compile_write_read_json_roundtrip():
    source = "Hallo Welt"
    _, _, b64 = _compile_write(source)

    read_resp = client.post(
        "/api/editor/gpm/read",
        json={"base64": b64},
    )
    assert read_resp.status_code == 200
    result = read_resp.json()["result"]
    assert result.get("document_ref")
    assert result.get("reconstructed_text") == source
    assert result.get("base64")
    assert result.get("token_count", 0) >= 1
    _assert_document_previews(result, min_genome=1, min_geometry=1)


def test_nl_compile_includes_reconstructed_text():
    source = "test"
    compile_resp = client.post(
        "/api/editor/compile",
        json={"mode": "nl", "text": source, "profile": "og"},
    )
    assert compile_resp.status_code == 200
    result = compile_resp.json()["result"]
    assert result.get("reconstructed_text") == source
    assert result.get("roundtrip_ok") is True
    _assert_document_previews(result, min_genome=1, min_geometry=1)


def _assert_document_previews(
    result: dict,
    *,
    min_genome: int,
    min_geometry: int,
) -> None:
    genome = result.get("genome_preview")
    geometry = result.get("geometry_preview")
    assert isinstance(genome, list) and len(genome) >= min_genome
    assert isinstance(geometry, list) and len(geometry) >= min_geometry
    assert "perm_index" not in genome[0]
    assert "word" in geometry[0]
    assert "substance" in geometry[0]
    assert "perm_index" in geometry[0]
    genome_by_word = {row["word"]: row["substance"] for row in genome}
    for row in geometry:
        assert row["substance"] == genome_by_word[row["word"]]


def test_gpm_multipart_read_roundtrip():
    source = "test"
    _, raw, _ = _compile_write(source)

    read_resp = client.post(
        "/api/editor/gpm/read/file",
        files={"file": ("test.gpm", io.BytesIO(raw), "application/octet-stream")},
    )
    assert read_resp.status_code == 200
    result = read_resp.json()["result"]
    assert result.get("document_ref")
    assert result.get("reconstructed_text") == source
    assert result.get("base64")


def test_gpm_json_base64_browser_simulation():
    source = "browser sim"
    _, raw, _ = _compile_write(source)
    b64 = base64.b64encode(raw).decode("ascii")

    read_resp = client.post(
        "/api/editor/gpm/read",
        json={"base64": b64},
    )
    assert read_resp.status_code == 200
    assert read_resp.json()["result"]["reconstructed_text"] == source


def test_gpm_read_rejects_plaintext_multipart():
    read_resp = client.post(
        "/api/editor/gpm/read/file",
        files={"file": ("plain.txt", io.BytesIO(b"not a gpm file"), "text/plain")},
    )
    assert read_resp.status_code == 422
    assert read_resp.json()["error"]["code"] == "gpm_invalid_stream"


def test_gpm_read_rejects_invalid_json_base64():
    read_resp = client.post(
        "/api/editor/gpm/read",
        json={"base64": "!!!not-valid-base64!!!"},
    )
    assert read_resp.status_code == 422
    assert read_resp.json()["error"]["code"] == "gpm_invalid_stream"
