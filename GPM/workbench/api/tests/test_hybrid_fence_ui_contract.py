"""Invariante A — hybrid compile must not leak fences into registry_entries."""

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

HYBRID_SOURCE = """# Demo

Ein Wort: HALLO

```python
def foo():
    return 1
```

Nach dem Fence.
"""


def test_hybrid_fence_not_in_registry():
    r = client.post(
        "/api/editor/compile",
        json={"mode": "hybrid", "text": HYBRID_SOURCE, "profile": "og"},
    )
    assert r.status_code == 200, r.text
    result = r.json()["result"]
    registry = result.get("registry_entries", [])
    fence_boundaries = result.get("fence_boundaries", [])
    assert len(fence_boundaries) >= 2
    for entry in registry:
        canonical = entry.get("word_canonical", "")
        assert "```" not in canonical
        assert "~~~" not in canonical
        assert not canonical.strip().startswith("```")
    for gap in result.get("gaps", []):
        assert "```" not in gap or gap == ""


def test_hybrid_fence_boundaries_present():
    r = client.post(
        "/api/editor/compile",
        json={"mode": "hybrid", "text": HYBRID_SOURCE, "profile": "og"},
    )
    result = r.json()["result"]
    lines = {fb.get("fence_line", "") for fb in result["fence_boundaries"]}
    assert any("```python" in line for line in lines)
