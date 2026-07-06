"""API contract tests."""

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


def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_version():
    r = client.get("/api/version")
    assert r.status_code == 200
    assert "workbench" in r.json()


def test_profiles():
    r = client.get("/api/profiles")
    assert r.status_code == 200
    assert r.json()["count"] >= 33
