#!/usr/bin/env python3
"""Workbench bootstrap — venv, pip, GPM/functions, npm."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FUNCTIONS = ROOT.parent / "functions"
WEB = ROOT / "web"
VENV_PY = ROOT / ".venv" / ("Scripts" if sys.platform == "win32" else "bin") / (
    "python.exe" if sys.platform == "win32" else "python"
)


def _say(msg: str) -> None:
    """Console-safe print (Windows cp1252 cannot encode some path chars)."""
    try:
        print(msg, flush=True)
    except UnicodeEncodeError:
        print(msg.encode("ascii", "backslashreplace").decode("ascii"), flush=True)


def _ensure_venv() -> Path:
    if VENV_PY.is_file():
        return VENV_PY
    start_dir = Path(__file__).resolve().parent
    sys.path.insert(0, str(start_dir))
    from find_python import ensure_venv

    ensure_venv()
    if not VENV_PY.is_file():
        raise SystemExit(
            "[FEHLER] Virtuelle Umgebung fehlt nach ensure_venv(). "
            "Installieren Sie Python 3.10+ von python.org (mit venv-Modul). "
            "pgAdmin/PostgreSQL-Python ist nicht geeignet."
        )
    return VENV_PY


def _pip_install(python: Path) -> None:
    req = ROOT / "requirements.txt"
    if not req.is_file():
        return
    subprocess.run([str(python), "-m", "pip", "install", "--upgrade", "pip", "-q"], check=True)
    subprocess.run([str(python), "-m", "pip", "install", "-r", str(req)], check=True)


def _check_node() -> None:
    npm = "npm.cmd" if sys.platform == "win32" else "npm"
    ver = subprocess.run([npm, "--version"], capture_output=True, text=True, check=False)
    if ver.returncode != 0:
        _say("[WARN] npm nicht gefunden — Frontend-Setup übersprungen.")
        return
    major = int(ver.stdout.strip().split(".")[0])
    if major < 20:
        _say(f"[WARN] Node {ver.stdout.strip()} — empfohlen: Node 20+")
    if (WEB / "package.json").is_file() and not (WEB / "node_modules").is_dir():
        _say("npm install in web/ …")
        subprocess.run([npm, "install"], cwd=str(WEB), check=True)


def bootstrap() -> None:
    py = _ensure_venv()
    _pip_install(py)

    sys.path.insert(0, str(FUNCTIONS))
    try:
        import alphabets  # noqa: F401
        import cachetools  # noqa: F401
        import fastapi  # noqa: F401
    except ImportError as exc:
        raise SystemExit(f"[FEHLER] Python-Abhängigkeit fehlt: {exc}") from exc

    if not FUNCTIONS.is_dir():
        raise SystemExit(f"[FEHLER] GPM/functions nicht gefunden: {FUNCTIONS}")

    example = ROOT / ".vscode" / "settings.json.example"
    example.parent.mkdir(exist_ok=True)
    if py.is_file():
        escaped = str(py.resolve()).replace("\\", "/")
        example.write_text(
            '{\n'
            f'  "python.defaultInterpreterPath": "{escaped}",\n'
            '  "python.terminal.activateEnvironment": true\n'
            "}\n",
            encoding="utf-8",
        )

    _check_node()

    _say("[OK] GPM Workbench bootstrap fertig.")
    _say(f"     functions: {FUNCTIONS}")
    _say("     Start: start\\dev.bat (Windows) oder start/dev.sh")


if __name__ == "__main__":
    bootstrap()
