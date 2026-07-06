"""Invariante B — i-curve responses downsample to max 512 points."""

from __future__ import annotations

import sys
from pathlib import Path

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
FUNCTIONS = ROOT.parent / "functions"
sys.path.insert(0, str(FUNCTIONS))
sys.path.insert(0, str(ROOT))

from api.main import app  # noqa: E402

client = TestClient(app)
SPARKLINE_LIMIT = 512


def _compile(text: str) -> str:
    r = client.post("/api/editor/compile", json={"mode": "nl", "text": text, "profile": "og"})
    assert r.status_code == 200
    return r.json()["result"]["document_ref"]


def test_i_curve_downsample_contract():
    words = " ".join(f"WORT{i}" for i in range(600))
    ref_a = _compile(words)
    ref_b = _compile(words + " EXTRA")
    r = client.post(
        "/api/compare/i-curve",
        json={"doc_a_ref": ref_a, "doc_b_ref": ref_b, "profile": "og"},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    result = body["result"]
    curve_a = result["curve_a"]
    curve_b = result["curve_b"]
    spark_a = curve_a.get("sparkline_points") or curve_a.get("points") or []
    spark_b = curve_b.get("sparkline_points") or curve_b.get("points") or []
    if isinstance(spark_a, list):
        assert len(spark_a) <= SPARKLINE_LIMIT + 2
    if isinstance(spark_b, list):
        assert len(spark_b) <= SPARKLINE_LIMIT + 2
    assert result.get("validation_pipeline", {}).get("steps")
    assert len(result["validation_pipeline"]["steps"]) == 5
    assert "relation_comparison" in result
    meta = body.get("curve_meta")
    if meta and meta.get("downsampled"):
        assert meta["limit"] == SPARKLINE_LIMIT
        assert meta["full_count"] > SPARKLINE_LIMIT
