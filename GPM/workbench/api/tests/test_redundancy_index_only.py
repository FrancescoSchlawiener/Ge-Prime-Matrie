"""Redundancy scan returns index-only chains."""

from __future__ import annotations

import json
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


def test_redundancy_index_only_payload():
    comp = client.post(
        "/api/editor/compile",
        json={"mode": "nl", "text": "alpha beta gamma alpha beta gamma", "profile": "og"},
    )
    ref = comp.json()["result"]["document_ref"]
    r = client.post("/api/compare/redundancy/scan", json={"document_ref": ref})
    assert r.status_code == 200
    raw = json.dumps(r.json())
    assert "word_canonical" not in raw
    assert "substring" not in raw
    chains = r.json()["result"].get("chains", [])
    if chains:
        chain = chains[0]
        assert "registry_ids" in chain
        assert "hit_positions" in chain
        assert "hits" not in chain
