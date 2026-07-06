#!/usr/bin/env python3
"""Start API (uvicorn) and Vite dev server together."""

from __future__ import annotations

import os
import signal
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FUNCTIONS = ROOT.parent / "functions"
WEB = ROOT / "web"


def _preflight() -> None:
    if not (FUNCTIONS / "alphabets").is_dir():
        raise SystemExit(f"[FEHLER] GPM/functions fehlt: {FUNCTIONS}")
    if not (WEB / "node_modules").is_dir():
        print("[HINWEIS] web/node_modules fehlt — starte zuerst start/setup.bat")


def main() -> None:
    _preflight()
    env = os.environ.copy()
    env["PYTHONPATH"] = str(FUNCTIONS) + os.pathsep + env.get("PYTHONPATH", "")

    print("GPM Workbench Dev")
    print("  API:  http://127.0.0.1:8000/api/health")
    print("  UI:   http://127.0.0.1:5173")
    print("  Stop: Ctrl+C")

    api = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "api.main:app", "--reload", "--host", "127.0.0.1", "--port", "8000"],
        cwd=str(ROOT),
        env=env,
    )
    fe = subprocess.Popen(["npm", "run", "dev"], cwd=str(WEB), shell=sys.platform == "win32")

    def shutdown(*_args):
        for proc in (api, fe):
            if proc.poll() is None:
                proc.terminate()

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)
    try:
        api.wait()
    finally:
        shutdown()


if __name__ == "__main__":
    main()
