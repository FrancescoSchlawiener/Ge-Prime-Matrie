"""Contract tests for structured WorkbenchError responses."""

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


def test_unknown_document_ref_structured_error():
    r = client.post("/api/editor/reconstruct", json={"mode": "nl", "document_ref": "missing"})
    assert r.status_code == 404
    body = r.json()
    assert body["error"]["code"] == "document_ref_not_found"


def test_gpm_encrypted_blob_cipher_key_required():
    gpc = b"GPC\x01" + b"\x00" * 20
    r = client.post(
        "/api/editor/gpm/read",
        json={"base64": base64.b64encode(gpc).decode("ascii")},
    )
    assert r.status_code == 401
    assert r.json()["error"]["code"] == "cipher_key_required"


def test_gpm_invalid_magic_422():
    r = client.post(
        "/api/editor/gpm/read",
        json={"base64": base64.b64encode(b"BAD").decode("ascii")},
    )
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "gpm_invalid_stream"
