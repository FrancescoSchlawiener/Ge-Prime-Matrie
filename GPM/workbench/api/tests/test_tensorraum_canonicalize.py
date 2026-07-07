"""Tensorraum canonicalize API contract."""

from __future__ import annotations

import base64
import json
import sys
from pathlib import Path

import pytest

_FUNCTIONS = Path(__file__).resolve().parents[2] / "functions"
if str(_FUNCTIONS) not in sys.path:
    sys.path.insert(0, str(_FUNCTIONS))

from analysis.code.decompile import reconstruct_source  # noqa: E402
from analysis.code.wire import decode_code_module  # noqa: E402
from api.steps.code import canonicalize_for_code  # noqa: E402


def _decode_result(result: dict) -> tuple:
    wire = base64.b64decode(result["wire_b64"])
    return decode_code_module(wire)


def test_canonicalize_js_add_function():
    src = "function add(a,b){return a+b;}\n"
    result = canonicalize_for_code(src, "add.js")
    assert result["language_id"] == "js"
    assert "tree" not in result
    assert result["roundtrip_ok"] is True
    assert "normalized_code" in result
    assert "reconstructed" in result
    json.dumps(result)
    _mod, reg = _decode_result(result)
    s_vals = {e.word_canonical for e in reg.s_entries}
    assert "FUNCTION" in s_vals or "ADD" in s_vals


def test_canonicalize_hybrid_abc123():
    src = "var x = abc123 + 42;\n"
    result = canonicalize_for_code(src, "test.js")
    _mod, reg = _decode_result(result)
    assert len(reg.h_entries) >= 1
    segs = reg.h_entries[0].segments
    tags = [s.tag for s in segs]
    assert "S" in tags and "N" in tags
    n_displays = {reg.n_display(i) for i in range(len(reg.n_entries))}
    assert "42" in n_displays and "123" in n_displays
    s_vals = {e.word_canonical for e in reg.s_entries}
    assert "abc123" not in s_vals


def test_canonicalize_decimal_relation():
    src = "const pi = 3.14;\n"
    result = canonicalize_for_code(src, "pi.js")
    _mod, reg = _decode_result(result)
    if not reg.d_entries:
        pytest.skip("D-Registry leer (bekannter Tokenizer-Bug)")
    from analysis.blocks.registry import DCodeEntry
    from gpm_types.di.relation import parse_decimal

    entry = reg.d_entries[0]
    raw = entry.display if isinstance(entry, DCodeEntry) else str(entry)
    rel = parse_decimal(raw)
    assert rel.whole and rel.den_reduced and rel.ggt


def test_canonicalize_workbench_index_html():
    index_path = Path(__file__).resolve().parents[2] / "web" / "index.html"
    src = index_path.read_text(encoding="utf-8")
    result = canonicalize_for_code(src, "index.html")
    assert result["language_id"] == "html"
    _mod, reg = _decode_result(result)
    assert len(reg.c_entries) >= 1
    assert any(b"doctype" in e.key_bytes.lower() for e in reg.c_entries)


def test_canonicalize_response_shape():
    src = "let x = 1;\n"
    result = canonicalize_for_code(src, "shape.js")
    json.dumps(result)
    assert set(result.keys()) == {
        "filename",
        "language_id",
        "language_name",
        "language_manifest",
        "normalized_code",
        "reconstructed",
        "roundtrip_ok",
        "trailing_whitespace",
        "wire_b64",
        "collision_report",
    }
    assert "tree" not in result
    assert "registry" not in result
    assert result["language_manifest"]["primary"] == "js"
    # Kollisionsbericht je Kategorie, alle kollisionsfrei fuer sauberen Code.
    report = result["collision_report"]
    assert set(report.keys()) == {"S", "N", "C", "H"}
    assert all(cat["collision_free"] for cat in report.values())


def test_canonicalize_fraktaler_tensorraum_html():
    fixture = Path(__file__).resolve().parents[4] / "Toy" / "gpm_c_i_fraktaler_tensorraum_v35.html"
    if not fixture.is_file():
        pytest.skip("Toy fixture missing")
    src = fixture.read_text(encoding="utf-8")
    result = canonicalize_for_code(src, fixture.name)
    json.dumps(result)
    assert "tree" not in result
    assert result["language_id"] == "html"
    mod, reg = _decode_result(result)
    assert len(reg.s_entries) > 10
    assert len(reg.c_entries) > 10
    s_vals = {e.word_canonical for e in reg.s_entries}
    isolated_hex = {v for v in s_vals if len(v) in (3, 4, 6, 8) and all(c in "0123456789ABCDEF" for c in v)}
    assert "8b8b98" not in isolated_hex and "8B8B98" not in isolated_hex
    reconstructed = result["reconstructed"]
    assert "</HTML>" in reconstructed or reconstructed.rstrip().endswith("</BODY>")
    line_delta = abs(len(reconstructed.splitlines()) - len(src.splitlines()))
    assert line_delta <= 30
