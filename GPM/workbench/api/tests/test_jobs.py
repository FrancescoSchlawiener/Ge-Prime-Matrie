"""Job runner API tests."""

from __future__ import annotations

import time

from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def _compile_nl(text: str = "ALPHA BETA ALPHA GAMMA") -> str:
    r = client.post(
        "/api/editor/compile",
        json={"mode": "nl", "text": text, "profile": "og"},
    )
    assert r.status_code == 200
    return r.json()["result"]["document_ref"]


def test_job_redundancy_scan_completes():
    ref = _compile_nl()
    start = client.post(
        "/api/jobs/redundancy/scan",
        json={"document_ref": ref, "window_mode": "adaptive"},
    )
    assert start.status_code == 200
    job_id = start.json()["job_id"]

    for _ in range(50):
        status = client.get(f"/api/jobs/{job_id}")
        assert status.status_code == 200
        body = status.json()
        if body["status"] in ("done", "failed"):
            break
        time.sleep(0.05)
    else:
        raise AssertionError("job timeout")

    assert body["status"] == "done"
    assert "chains" in body["result"]
    assert "summary" in body["result"]
    assert body["progress"]["percent"] == 100


def test_job_compile_completes():
    start = client.post(
        "/api/jobs/compile",
        json={"mode": "nl", "text": "JOB COMPILE CONTRACT", "profile": "og"},
    )
    assert start.status_code == 200
    job_id = start.json()["job_id"]

    body = None
    for _ in range(50):
        status = client.get(f"/api/jobs/{job_id}")
        assert status.status_code == 200
        body = status.json()
        if body["status"] in ("done", "failed"):
            break
        time.sleep(0.05)
    else:
        raise AssertionError("job timeout")

    assert body is not None
    assert body["status"] == "done"
    assert body["result"]["response"]["result"]["document_ref"]
    assert body["progress"]["percent"] == 100


def test_job_not_found():
    r = client.get("/api/jobs/does-not-exist")
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "job_not_found"
