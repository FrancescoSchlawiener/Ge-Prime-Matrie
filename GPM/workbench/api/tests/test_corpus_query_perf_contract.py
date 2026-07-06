"""Corpus query should not load all documents before tiered compare."""

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


def test_corpus_query_lazy_load():
    refs = []
    for text in ("hello world", "silent listen", "foo bar"):
        r = client.post("/api/editor/compile", json={"mode": "nl", "text": text, "profile": "og"})
        refs.append(r.json()["result"]["document_ref"])
    idx = client.post(
        "/api/compare/corpus/index",
        json={"document_refs": refs, "profile": "og"},
    )
    index_id = idx.json()["result"]["index_id"]
    loads = {"n": 0}
    from api import session

    original_get = session.store.get_document

    def counting_get(ref):
        loads["n"] += 1
        return original_get(ref)

    with patch.object(session.store, "get_document", side_effect=counting_get):
        q = client.post(
            "/api/compare/corpus/query",
            json={"index_id": index_id, "query_ref": refs[0], "top_k": 2, "tier": 1},
        )
    assert q.status_code == 200
    assert loads["n"] < len(refs) + 2
