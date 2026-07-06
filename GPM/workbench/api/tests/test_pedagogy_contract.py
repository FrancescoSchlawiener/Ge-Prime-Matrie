"""Säule 4 — every calc endpoint returns at least one pedagogical step."""

from __future__ import annotations

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


def test_decode_returns_steps():
    enc = client.post("/api/calc/encode-word", json={"word": "HALLO", "profile": "og"})
    assert enc.status_code == 200
    r = enc.json()["result"]
    dec = client.post(
        "/api/calc/decode-word",
        json={"substance": r["substance"], "index": r["index"], "profile": "og"},
    )
    assert dec.status_code == 200
    body = dec.json()
    assert len(body["steps"]) >= 1


@pytest.mark.parametrize(
    "endpoint,payload",
    [
        ("/api/calc/encode-word", {"word": "HALLO", "profile": "og"}),
        ("/api/calc/compare-words", {"a": "LISTEN", "b": "SILENT", "profile": "og"}),
    ],
)
def test_calc_returns_steps(endpoint, payload):
    r = client.post(endpoint, json=payload)
    assert r.status_code == 200, r.text
    body = r.json()
    assert "steps" in body
    assert len(body["steps"]) >= 1
    assert "result" in body
