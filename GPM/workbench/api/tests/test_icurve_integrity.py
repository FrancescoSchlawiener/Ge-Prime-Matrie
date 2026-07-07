"""I-Kurve Integrität — Invariante I3-G Dual-Gateway und Preview-Vertrag."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
FUNCTIONS = ROOT.parent / "functions"
sys.path.insert(0, str(FUNCTIONS))
sys.path.insert(0, str(ROOT))

from analysis.document.model import GpmToken  # noqa: E402
from api.main import app  # noqa: E402
from api.session import store  # noqa: E402
from gpm_types.classify import PayloadKind  # noqa: E402

client = TestClient(app)


@pytest.fixture(autouse=True)
def _clear_cache():
    from api.cache.document_cache import document_cache

    document_cache._cache.clear()
    yield
    document_cache._cache.clear()


def _compile(text: str) -> str:
    r = client.post("/api/editor/compile", json={"mode": "nl", "text": text, "profile": "og"})
    assert r.status_code == 200
    return r.json()["result"]["document_ref"]


def _assert_icurve_previews(result: dict) -> None:
    for key in ("genome_preview_a", "genome_preview_b", "geometry_preview_a", "geometry_preview_b"):
        assert isinstance(result.get(key), list)
        assert len(result[key]) >= 1

    curve_pts = result["curve_a"]["points"]
    geometry = result["geometry_preview_a"]
    for idx, pt in enumerate(curve_pts):
        if idx < len(geometry):
            assert pt["substance"] == geometry[idx]["substance"]


def test_icurve_valid_pair_includes_previews():
    ref_a = _compile("HALLO WELT")
    ref_b = _compile("HALLO WELT")
    r = client.post(
        "/api/compare/i-curve",
        json={"doc_a_ref": ref_a, "doc_b_ref": ref_b, "profile": "og"},
    )
    assert r.status_code == 200, r.text
    result = r.json()["result"]
    _assert_icurve_previews(result)
    cells = result["cell_geometry_a"]["points"]
    assert cells and cells[0].get("label")


def test_icurve_rejects_corrupt_document_no_result_rumpf():
    ref_a = _compile("hello")
    ref_b = _compile("world")
    stored = store.get_document(ref_b)
    doc = stored.document
    assert doc is not None
    token = doc.tokens[0]
    doc.tokens[0] = GpmToken(
        word_id=99,
        perm_index=token.perm_index,
        case_code=token.case_code,
        payload_kind=PayloadKind.S,
    )

    r = client.post(
        "/api/compare/i-curve",
        json={"doc_a_ref": ref_a, "doc_b_ref": ref_b, "profile": "og"},
    )
    assert r.status_code == 400
    body = r.json()
    assert "result" not in body or body.get("result") is None


def test_icurve_rejects_corrupt_doc_a_only():
    ref_a = _compile("alpha")
    ref_b = _compile("beta")
    stored = store.get_document(ref_a)
    doc = stored.document
    assert doc is not None
    token = doc.tokens[0]
    doc.tokens[0] = GpmToken(
        word_id=99,
        perm_index=token.perm_index,
        case_code=token.case_code,
        payload_kind=PayloadKind.S,
    )

    r = client.post(
        "/api/compare/i-curve",
        json={"doc_a_ref": ref_a, "doc_b_ref": ref_b, "profile": "og"},
    )
    assert r.status_code == 400
