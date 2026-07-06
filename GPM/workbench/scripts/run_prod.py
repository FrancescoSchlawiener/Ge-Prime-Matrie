#!/usr/bin/env python3
"""Production entry — uvicorn with static frontend."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FUNCTIONS = ROOT.parent / "functions"

os.environ.setdefault("WORKBENCH_PROD", "1")
os.environ["PYTHONPATH"] = str(FUNCTIONS) + os.pathsep + os.environ.get("PYTHONPATH", "")

import uvicorn  # noqa: E402

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=port,
        app_dir=str(ROOT),
    )
