"""Tensorraum canonicalize API contract."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_FUNCTIONS = Path(__file__).resolve().parents[2] / "functions"
if str(_FUNCTIONS) not in sys.path:
    sys.path.insert(0, str(_FUNCTIONS))

from api.steps.tensorraum import canonicalize_for_tensorraum  # noqa: E402


def test_canonicalize_js_add_function():
    src = "function add(a,b){return a+b;}\n"
    result = canonicalize_for_tensorraum(src, "add.js")
    assert result["language_id"] == "js"
    s_vals = {e["value"] for e in result["registry"]["S"]}
    assert "function" in s_vals or "add" in s_vals
    assert result["roundtrip_ok"] is True


def test_canonicalize_hybrid_abc123():
    src = "var x = abc123 + 42;\n"
    result = canonicalize_for_tensorraum(src, "test.js")
    h_entries = result["registry"]["H"]
    assert len(h_entries) >= 1
    segs = h_entries[0]["segments"]
    tags = [s["tag"] for s in segs]
    assert "S" in tags and "N" in tags
    n_vals = {e["value"] for e in result["registry"]["N"]}
    assert "42" in n_vals
    s_vals = {e["value"] for e in result["registry"]["S"]}
    assert "abc123" not in s_vals


def test_canonicalize_decimal_relation():
    src = "const pi = 3.14;\n"
    result = canonicalize_for_tensorraum(src, "pi.js")
    d_entries = result["registry"]["D"]
    assert len(d_entries) >= 1
    rel = d_entries[0]["relation"]
    assert "whole" in rel and "den_reduced" in rel and "ggt" in rel


def test_canonicalize_workbench_index_html():
    index_path = Path(__file__).resolve().parents[2] / "web" / "index.html"
    src = index_path.read_text(encoding="utf-8")
    result = canonicalize_for_tensorraum(src, "index.html")
    assert result["language_id"] == "html"
    assert len(result["registry"]["C"]) >= 1
    assert any("doctype" in e["value"].lower() for e in result["registry"]["C"])


def test_canonicalize_fraktaler_tensorraum_html():
    fixture = Path(__file__).resolve().parents[4] / "Toy" / "gpm_c_i_fraktaler_tensorraum_v35.html"
    if not fixture.is_file():
        pytest.skip("Toy fixture missing")
    src = fixture.read_text(encoding="utf-8")
    result = canonicalize_for_tensorraum(src, "gpm_c_i_fraktaler_tensorraum_v37.html")
    assert result["language_id"] == "html"
    assert len(result["registry"]["S"]) > 10
    assert len(result["registry"]["C"]) > 10
