"""Pedagogy must not double-invoke encode_si in calc routes."""

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

from api.main import app  # noqa: E402

client = TestClient(app)


def test_encode_word_single_inference():
    calls = {"n": 0}
    import gpm_types.si.codec as codec

    original = codec.encode_si_with_trace

    def counted(*args, **kwargs):
        calls["n"] += 1
        return original(*args, **kwargs)

    with patch.object(codec, "encode_si_with_trace", side_effect=counted):
        r = client.post("/api/calc/encode-word", json={"word": "HALLO", "profile": "og"})
    assert r.status_code == 200
    assert calls["n"] == 1
    assert len(r.json()["steps"]) >= 1
