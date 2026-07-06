"""I-curve viewport API tests."""

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


def _compile(text: str) -> str:
    r = client.post("/api/editor/compile", json={"mode": "nl", "text": text, "profile": "og"})
    assert r.status_code == 200
    return r.json()["result"]["document_ref"]


def test_i_curve_viewport_payload():
    ref_a = _compile("HALLO WELT")
    ref_b = _compile("WELT HALLO")
    r = client.post(
        "/api/compare/i-curve",
        json={"doc_a_ref": ref_a, "doc_b_ref": ref_b, "profile": "og"},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    result = body["result"]
    vp_a = result["viewport_a"]
    vp_b = result["viewport_b"]
    assert vp_a["reconstructed_text"]
    assert len(vp_a["token_char_map"]) > 0
    assert vp_b["reconstructed_text"]
    assert result.get("relation_comparison") is not None
    steps = result["validation_pipeline"]["steps"]
    assert len(steps) == 5
    comparison = result["comparison"]
    axis_scores = comparison.get("axis_scores") or {}
    assert axis_scores.get("token_i") is not None
    assert result["meta_a"].get("vector") is not None


def test_i_curve_token_limit():
    words = " ".join(f"W{i}" for i in range(10_001))
    ref = _compile(words)
    r = client.post(
        "/api/compare/i-curve",
        json={"doc_a_ref": ref, "doc_b_ref": ref, "profile": "og"},
    )
    assert r.status_code == 400


def test_i_curve_long_prose_viewport():
    """Regression: langer Prosatext mit Umlauten und [1124] — kein 2-Byte-Overflow."""
    text_a = (
        "Morgenröte\nGedanken über die Moral als Vorurteil\n1\n"
        "[1124] Mit diesem Buche beginnt mein Feldzug gegen die Moral. "
        "Nicht daß es den geringsten Pulvergeruch an sich hätte – man wird ganz "
        "andere und viel lieblichere Gerüche an ihm wahrnehmen, gesetzt, daß man "
        "einige Feinheit in den Nüstern hat. Weder großes, noch auch kleines "
        "Geschütz: ist die Wirkung des Buches negativ, so sind es seine Mittel um "
        "so weniger, diese Mittel, aus denen die Wirkung wie ein Schluß, nicht wie "
        "ein Kanonschuß folgt."
    )
    text_b = (
        "Jenseits von Gut und Böse\nVorspiel einer Philosophie der Zukunft\n1\n"
        "[1141] Die Aufgabe für die nunmehr folgenden Jahre war so streng als "
        "möglich vorgezeichnet. Nachdem der jasagende Teil meiner Aufgabe gelöst "
        "war, kam die neinsagende, neintuende Hälfte derselben an die Reihe: die "
        "Umwertung der bisherigen Werte selbst, der große Krieg – die "
        "Heraufbeschwörung eines Tags der Entscheidung."
    )
    ref_a = _compile(text_a)
    ref_b = _compile(text_b)
    r = client.post(
        "/api/compare/i-curve",
        json={"doc_a_ref": ref_a, "doc_b_ref": ref_b, "profile": "og"},
    )
    assert r.status_code == 200, r.text
    result = r.json()["result"]
    assert result["viewport_a"]["reconstructed_text"]
    assert len(result["viewport_a"]["token_char_map"]) > 0
    assert "plain_gpm_base64" not in result["viewport_a"]
    comparison = result["comparison"]
    assert comparison.get("axis_scores")
    assert result["meta_a"].get("vector") is not None
    assert result["meta_a"].get("total_letter_mass") is not None
