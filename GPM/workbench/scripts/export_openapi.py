#!/usr/bin/env python3
"""Export OpenAPI schema to web/openapi.snapshot.json."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FUNCTIONS = ROOT.parent / "functions"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(FUNCTIONS))

from api.main import app  # noqa: E402

out = ROOT / "web" / "openapi.snapshot.json"
out.write_text(json.dumps(app.openapi(), indent=2), encoding="utf-8")
try:
    print(f"Wrote {out}")
except UnicodeEncodeError:
    print("Wrote openapi.snapshot.json")
